"""Parent-side STEP extraction orchestration.

Never imports OCP: the toolchain runs only inside the worker subprocess.
This module verifies and assembles the worker's output into contract
models, derives deterministic entity ids, parses declared units from the
raw payload itself, and builds the index-keyed glTF node map.
"""

import hashlib
import json
import platform
import re
import struct
import sys
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from backend.data_sources.contracts import (
    ComponentInstance,
    CoordinateConversion,
    DerivativeRecord,
    ExtractionEnvironment,
    ExtractionError,
    ExtractionResult,
    ExtractorIdentity,
    PartDefinition,
    StepExtractionManifest,
    StepManifestResult,
    TessellationParameters,
    TransformSpec,
    UnitContext,
)
from backend.data_sources.extractors.format_detector import parse_declared_schemas
from backend.data_sources.extractors.worker_harness import (
    WorkerLimits,
    invoke_worker,
)
from backend.data_sources.provenance import derive_entity_id, payload_checksum

STEP_EXTRACTOR_VERSION = "1.0.0"
LEVELS_SUPPORTED = [0, 1, 2, 3]

_REPO_ROOT = Path(__file__).resolve().parents[4]

UNIT_CONTEXT_DECLARED = "uc-step-declared"
UNIT_CONTEXT_OCCT = "uc-occt-import"

_PMI_MARKERS = (b"DIMENSIONAL_CHARACTERISTIC", b"GEOMETRIC_TOLERANCE", b"DATUM_FEATURE")


class StepExtractionConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    linear_deflection: float = Field(default=0.1, gt=0)
    angular_deflection: float = Field(default=0.5, gt=0)
    relative: bool = False


@dataclass
class StepExtractionProduct:
    """What the runtime publishes: the envelope plus derivative payload
    bytes keyed by their content-addressed reference. The extractor never
    touches the raw store."""

    result: ExtractionResult
    derivative_payloads: dict[str, bytes] = field(default_factory=dict)


def step_extractor_identity(config: StepExtractionConfig, toolchain: str) -> ExtractorIdentity:
    fingerprint = hashlib.sha256(config.model_dump_json().encode()).hexdigest()[:16]
    return ExtractorIdentity(
        name="step_extractor",
        version=STEP_EXTRACTOR_VERSION,
        toolchain=toolchain,
        config_fingerprint=fingerprint,
    )


def extract_step(
    payload: bytes,
    raw_record_id: str,
    config: StepExtractionConfig,
    limits: WorkerLimits,
    scratch_root: Path | None = None,
) -> StepExtractionProduct:
    def build_argv(input_path: Path, output_dir: Path) -> list[str]:
        return [
            sys.executable,
            "-m",
            "backend.data_sources.extractors.step.worker",
            str(input_path),
            str(output_dir),
            config.model_dump_json(),
        ]

    outcome = invoke_worker(
        build_argv,
        payload=payload,
        expected_checksum=payload_checksum(payload),
        limits=limits,
        scratch_root=scratch_root,
        payload_filename="payload.step",
        extra_env={"PYTHONPATH": str(_REPO_ROOT)},
    )

    if outcome.status == "timeout":
        raise ExtractionError(
            "EXTRACT_WORKER_TIMEOUT",
            f"STEP worker exceeded the {limits.timeout_seconds:.0f}s limit and "
            "was terminated",
        )
    if outcome.status == "crashed":
        raise ExtractionError(
            "EXTRACT_WORKER_CRASHED",
            f"STEP worker terminated abnormally (returncode "
            f"{outcome.returncode}); stderr tail: {outcome.stderr_tail[-200:]!r}",
        )

    if "worker_result.json" not in outcome.outputs:
        raise ExtractionError(
            "EXTRACT_WORKER_CRASHED", "STEP worker exited cleanly but produced no result"
        )
    worker = json.loads(outcome.outputs["worker_result.json"])

    if worker["status"] == "parse_failed":
        raise ExtractionError("EXTRACT_STEP_PARSE_FAILED", worker["error"])

    identity = step_extractor_identity(config, worker["toolchain"])
    warnings: list[str] = list(worker.get("warnings", []))

    unit_contexts, unit_warnings = _build_unit_contexts(payload)
    warnings.extend(unit_warnings)

    def def_id(path: str) -> str:
        return derive_entity_id(raw_record_id, STEP_EXTRACTOR_VERSION, f"def:{path}")

    definitions = [
        PartDefinition(
            definition_id=def_id(item["path"]),
            extractor_path_id=item["path"],
            name=item["name"],
            is_assembly=item["is_assembly"],
            properties=[],
            unit_context_ref=UNIT_CONTEXT_OCCT,
        )
        for item in worker["definitions"]
    ]
    def_name_by_path = {item["path"]: item["name"] for item in worker["definitions"]}

    instances: list[ComponentInstance] = []
    instance_id_by_path: dict[str, str] = {}
    root_instance_ids: list[str] = []

    for root in worker["free_roots"]:
        instance_id = derive_entity_id(
            raw_record_id, STEP_EXTRACTOR_VERSION, f"root:{root['path']}"
        )
        instance_id_by_path[root["path"]] = instance_id
        root_instance_ids.append(instance_id)
        instances.append(
            ComponentInstance(
                instance_id=instance_id,
                definition_ref=def_id(root["path"]),
                parent_definition_ref=None,
                occurrence_name=root["name"],
                extractor_path_id=root["path"],
                transform=_transform(
                    [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
                    source=f"definition:{root['name']}",
                    destination="document_root",
                ),
            )
        )

    for occurrence in worker["occurrences"]:
        instance_id = derive_entity_id(
            raw_record_id, STEP_EXTRACTOR_VERSION, f"occ:{occurrence['path']}"
        )
        instance_id_by_path[occurrence["path"]] = instance_id
        instances.append(
            ComponentInstance(
                instance_id=instance_id,
                definition_ref=def_id(occurrence["ref_path"]),
                parent_definition_ref=def_id(occurrence["parent_def_path"]),
                occurrence_name=occurrence["name"],
                extractor_path_id=occurrence["path"],
                transform=_transform(
                    occurrence["matrix12"],
                    source=f"definition:{def_name_by_path.get(occurrence['ref_path'])}",
                    destination=f"definition:{def_name_by_path.get(occurrence['parent_def_path'])}",
                ),
            )
        )

    unsupported = [
        f"{marker.decode()} entities present but not interpreted"
        for marker in _PMI_MARKERS
        if marker in payload
    ]
    lossy = [
        "B-rep geometry tessellated for the visualization derivative at "
        f"linear deflection {config.linear_deflection} / angular "
        f"{config.angular_deflection}; geometric fidelity reduced",
    ]

    derivatives: list[DerivativeRecord] = []
    derivative_payloads: dict[str, bytes] = {}
    gltf = worker["gltf"]
    outcome_value = "succeeded"
    levels = [0, 1, 2]

    if gltf["ok"] and gltf["file"] in outcome.outputs:
        glb = outcome.outputs[gltf["file"]]
        node_map, map_warnings = _build_node_map(glb, instance_id_by_path)
        warnings.extend(map_warnings)
        lossy.append(
            "glTF node names replaced by extractor path ids for traceability; "
            "original occurrence names preserved in this manifest"
        )
        reference = payload_checksum(glb)
        conversion = worker["coordinate_conversion"]
        derivatives.append(
            DerivativeRecord(
                derivative_id=derive_entity_id(
                    raw_record_id, STEP_EXTRACTOR_VERSION, f"gltf:{reference}"
                ),
                raw_record_id=raw_record_id,
                kind="visualization_gltf",
                media_type="model/gltf-binary",
                payload_reference=reference,
                checksum=reference,
                generator=identity,
                tessellation=TessellationParameters(
                    linear_deflection=config.linear_deflection,
                    angular_deflection=config.angular_deflection,
                    relative=config.relative,
                ),
                coordinate_conversion=CoordinateConversion(**conversion),
                node_map=node_map,
                environment=ExtractionEnvironment(
                    platform=platform.system().lower(),
                    architecture=platform.machine(),
                    occt_version=worker["occt_version"],
                ),
            )
        )
        derivative_payloads[reference] = glb
        levels = [0, 1, 2, 3]
    else:
        outcome_value = "partial"
        warnings.append(
            "visualization derivative not produced: "
            + (gltf.get("error") or "unknown failure")
        )

    manifest = StepExtractionManifest(
        raw_record_id=raw_record_id,
        extractor=identity,
        declared_schemas=parse_declared_schemas(payload),
        unit_contexts=unit_contexts,
        definitions=definitions,
        instances=instances,
        root_instance_ids=root_instance_ids,
        derivatives=derivatives,
        levels_supported=LEVELS_SUPPORTED,
        levels_achieved=levels,
        unsupported_features=unsupported,
        lossy_conversions=lossy,
        warnings=warnings,
    )
    result = ExtractionResult(
        schema_version=1,
        raw_record_id=raw_record_id,
        extractor=identity,
        outcome=outcome_value,
        warnings=[w for w in warnings if "derivative" in w],
        result=StepManifestResult(manifest=manifest),
    )
    return StepExtractionProduct(result=result, derivative_payloads=derivative_payloads)


def _transform(matrix12: list[float], source: str, destination: str) -> TransformSpec:
    matrix = [float(v) for v in matrix12] + [0.0, 0.0, 0.0, 1.0]
    return TransformSpec(
        matrix=matrix,
        layout="row_major_4x4",
        source_frame=source,
        destination_frame=destination,
        handedness="right_handed",
        length_unit_ref=UNIT_CONTEXT_OCCT,
    )


_SI_PREFIX_UNITS = {
    ("MILLI", "METRE"): "millimetre",
    ("CENTI", "METRE"): "centimetre",
    ("MICRO", "METRE"): "micrometre",
    (None, "METRE"): "metre",
}
_LENGTH_STATEMENT = re.compile(rb"[^;]*LENGTH_UNIT\(\)[^;]*;")
_SI_UNIT = re.compile(rb"SI_UNIT\((?:\.(\w+)\.|\$)\s*,\s*\.(\w+)\.\)")
_CONVERSION_NAME = re.compile(rb"CONVERSION_BASED_UNIT\(\s*'([^']+)'")


def _build_unit_contexts(payload: bytes) -> tuple[list[UnitContext], list[str]]:
    """Parse declared length units from the Part 21 data itself.

    Never defaults: no parseable declaration yields an 'unavailable'
    context plus a warning. The OCCT import unit is a separate,
    configuration_supplied context (the reader is pinned to millimetres).
    """
    found: dict[str, str] = {}  # unit name -> source representation
    for statement in _LENGTH_STATEMENT.finditer(payload):
        text = statement.group(0)
        si = _SI_UNIT.search(text)
        if si:
            prefix = si.group(1).decode() if si.group(1) else None
            name = _SI_PREFIX_UNITS.get((prefix, si.group(2).decode()))
            if name:
                found[name] = si.group(0).decode()
                continue
        conversion = _CONVERSION_NAME.search(text)
        if conversion:
            name = conversion.group(1).decode().lower()
            found[name] = conversion.group(0).decode() + "...')"

    warnings: list[str] = []
    contexts = [
        UnitContext(
            context_id=UNIT_CONTEXT_OCCT,
            length_unit="millimetre",
            angle_unit="radian",
            provenance="configuration_supplied",
            source_representation="xstep.cascade.unit=MM (pinned reader configuration)",
        )
    ]
    if len(found) == 1:
        [(unit, source)] = found.items()
        contexts.insert(
            0,
            UnitContext(
                context_id=UNIT_CONTEXT_DECLARED,
                length_unit=unit,
                angle_unit=None,
                provenance="explicitly_declared",
                source_representation=source,
            ),
        )
    elif len(found) > 1:
        warnings.append(
            "multiple distinct declared length units found "
            f"({sorted(found)}); no single declared unit context recorded"
        )
        contexts.insert(
            0,
            UnitContext(
                context_id=UNIT_CONTEXT_DECLARED,
                length_unit=None,
                angle_unit=None,
                provenance="unavailable",
                source_representation="; ".join(sorted(found.values()))[:200],
            ),
        )
    else:
        warnings.append("no declared length unit found in the STEP data")
        contexts.insert(
            0,
            UnitContext(
                context_id=UNIT_CONTEXT_DECLARED,
                length_unit=None,
                angle_unit=None,
                provenance="unavailable",
                source_representation=None,
            ),
        )
    return contexts, warnings


def _parse_glb_nodes(data: bytes) -> list[tuple[int, str | None]]:
    if data[:4] != b"glTF":
        raise ExtractionError("EXTRACT_GLTF_MALFORMED", "derivative is not a glb container")
    chunk_length = struct.unpack_from("<I", data, 12)[0]
    if data[16:20] != b"JSON":
        raise ExtractionError("EXTRACT_GLTF_MALFORMED", "glb JSON chunk missing")
    document = json.loads(data[20 : 20 + chunk_length])
    return [(index, node.get("name")) for index, node in enumerate(document.get("nodes", []))]


def _build_node_map(
    glb: bytes, instance_id_by_path: dict[str, str]
) -> tuple[dict[str, str], list[str]]:
    """Index-keyed sidecar map. Node names carry extractor path ids (set by
    the worker rename); names are matched back to instances and duplicates
    are excluded with a warning — a name is never trusted as identity."""
    nodes = _parse_glb_nodes(glb)
    warnings: list[str] = []
    name_counts: dict[str, int] = {}
    for _, name in nodes:
        if name:
            name_counts[name] = name_counts.get(name, 0) + 1

    node_map: dict[str, str] = {}
    for index, name in nodes:
        if not name or name not in instance_id_by_path:
            continue
        if name_counts[name] > 1:
            warnings.append(
                f"glTF node name {name!r} appears {name_counts[name]} times; "
                "those nodes were left unmapped (flattened shared-subassembly "
                "mapping is not supported in DS-002)"
            )
            continue
        node_map[str(index)] = instance_id_by_path[name]
    return dict(sorted(node_map.items(), key=lambda kv: int(kv[0]))), sorted(set(warnings))
