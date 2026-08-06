"""STEP extraction worker. Runs ONLY as a subprocess under the worker
harness; this is the sole module allowed to import OCP.

    python -m backend.data_sources.extractors.step.worker \
        <input.step> <output_dir> <config_json>

Always writes ``worker_result.json`` into the output dir and exits 0 for
handled outcomes (including parse failure — reported as data). A non-zero
exit or signal means an unhandled crash, which the parent maps to
EXTRACT_WORKER_CRASHED.

Error messages written here must not contain filesystem paths.
"""

import importlib.metadata
import json
import sys
from pathlib import Path


def entry_of(label) -> str:
    from OCP.TCollection import TCollection_AsciiString
    from OCP.TDF import TDF_Tool

    ascii_string = TCollection_AsciiString()
    TDF_Tool.Entry_s(label, ascii_string)
    return ascii_string.ToCString()


def name_of(label) -> str | None:
    from OCP.TCollection import TCollection_AsciiString
    from OCP.TDataStd import TDataStd_Name

    attr = TDataStd_Name()
    if label.FindAttribute(TDataStd_Name.GetID_s(), attr):
        return TCollection_AsciiString(attr.Get()).ToCString()
    return None


def rename(label, new_name: str) -> None:
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name

    TDataStd_Name.Set_s(label, TCollection_ExtendedString(new_name))


def matrix12_of(location) -> list[float]:
    trsf = location.Transformation()
    return [trsf.Value(row, col) for row in range(1, 4) for col in range(1, 5)]


def read_document(input_path: Path):
    from OCP.IFSelect import IFSelect_ReturnStatus
    from OCP.Interface import Interface_Static
    from OCP.STEPCAFControl import STEPCAFControl_Reader
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDocStd import TDocStd_Document

    Interface_Static.SetCVal_s("xstep.cascade.unit", "MM")
    doc = TDocStd_Document(TCollection_ExtendedString("XmlOcaf"))
    reader = STEPCAFControl_Reader()
    reader.SetNameMode(True)
    status = reader.ReadFile(str(input_path))
    if status != IFSelect_ReturnStatus.IFSelect_RetDone:
        raise ValueError("STEP file could not be read (Part 21 parse failure)")
    if not reader.Transfer(doc):
        raise ValueError("STEP data could not be transferred to a document")
    return doc


def traverse(doc):
    from OCP.TDF import TDF_Label, TDF_LabelSequence
    from OCP.XCAFDoc import XCAFDoc_DocumentTool

    shapes = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    free = TDF_LabelSequence()
    shapes.GetFreeShapes(free)

    free_roots = []
    definitions: dict[str, dict] = {}
    occurrences: list[dict] = []
    labels_to_rename: list = []

    def visit_definition(label):
        path = entry_of(label)
        if path in definitions:
            return
        definitions[path] = {
            "path": path,
            "name": name_of(label),
            "is_assembly": bool(shapes.IsAssembly_s(label)),
        }
        components = TDF_LabelSequence()
        shapes.GetComponents_s(label, components)
        for i in range(1, components.Length() + 1):
            component = components.Value(i)
            referred = TDF_Label()
            shapes.GetReferredShape_s(component, referred)
            occurrences.append(
                {
                    "path": entry_of(component),
                    "name": name_of(component),
                    "ref_path": entry_of(referred),
                    "parent_def_path": path,
                    "matrix12": matrix12_of(shapes.GetLocation_s(component)),
                }
            )
            labels_to_rename.append(component)
            visit_definition(referred)

    for i in range(1, free.Length() + 1):
        root = free.Value(i)
        free_roots.append({"path": entry_of(root), "name": name_of(root)})
        labels_to_rename.append(root)
        visit_definition(root)

    return shapes, free, free_roots, definitions, occurrences, labels_to_rename


def write_gltf(doc, shapes, free, labels_to_rename, output_dir: Path, config: dict):
    """Rename labels to their entry strings (unique) and export a glb.

    Returns (gltf_info, coordinate_conversion, warnings).
    """
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.Message import Message_ProgressRange
    from OCP.RWGltf import RWGltf_CafWriter
    from OCP.TColStd import TColStd_IndexedDataMapOfStringString
    from OCP.TCollection import TCollection_AsciiString

    warnings: list[str] = []
    for label in labels_to_rename:
        rename(label, entry_of(label))

    for i in range(1, free.Length() + 1):
        shape = shapes.GetShape_s(free.Value(i))
        BRepMesh_IncrementalMesh(
            shape,
            config["linear_deflection"],
            config["relative"],
            config["angular_deflection"],
            True,
        )

    glb_path = output_dir / "scene.glb"
    writer = RWGltf_CafWriter(TCollection_AsciiString(str(glb_path)), True)

    conversion = {
        "source_frame": "step_model_space_mm_z_up",
        "target_frame": "gltf_y_up_right_handed",
        "target_length_unit": "metre",
        "converter": "RWGltf_CafWriter with explicit mm->m scale and Z-up input",
    }
    try:
        converter = writer.ChangeCoordinateSystemConverter()
        converter.SetInputLengthUnit(0.001)  # document millimetres -> glTF metres
        from OCP.RWMesh import RWMesh_CoordinateSystem

        converter.SetInputCoordinateSystem(RWMesh_CoordinateSystem.RWMesh_CoordinateSystem_Zup)
    except Exception as error:  # pragma: no cover - depends on binding surface
        conversion["converter"] = "RWGltf_CafWriter defaults (explicit configuration unavailable)"
        warnings.append(
            "coordinate-system converter could not be configured explicitly "
            f"({type(error).__name__}); writer defaults were used"
        )

    ok = writer.Perform(doc, TColStd_IndexedDataMapOfStringString(), Message_ProgressRange())
    if not ok or not glb_path.exists():
        return (
            {"ok": False, "file": None, "error": "glTF writer reported failure"},
            conversion,
            warnings,
        )
    return {"ok": True, "file": "scene.glb", "error": None}, conversion, warnings


def main() -> int:
    input_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    config = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {
        "linear_deflection": 0.1,
        "angular_deflection": 0.5,
        "relative": False,
    }

    ocp_version = importlib.metadata.version("cadquery-ocp")
    result: dict = {
        "status": "ok",
        "error": None,
        "toolchain": f"cadquery-ocp {ocp_version}",
        "occt_version": ".".join(ocp_version.split(".")[:3]),
        "free_roots": [],
        "definitions": [],
        "occurrences": [],
        "gltf": {"ok": False, "file": None, "error": "not attempted"},
        "coordinate_conversion": None,
        "warnings": [],
    }

    try:
        doc = read_document(input_path)
        shapes, free, free_roots, definitions, occurrences, to_rename = traverse(doc)
        result["free_roots"] = free_roots
        result["definitions"] = sorted(definitions.values(), key=lambda d: d["path"])
        result["occurrences"] = sorted(occurrences, key=lambda o: o["path"])
        try:
            gltf, conversion, gltf_warnings = write_gltf(
                doc, shapes, free, to_rename, output_dir, config
            )
            result["gltf"] = gltf
            result["coordinate_conversion"] = conversion
            result["warnings"].extend(gltf_warnings)
        except Exception as error:
            result["gltf"] = {
                "ok": False,
                "file": None,
                "error": f"derivative generation failed ({type(error).__name__}: {error})",
            }
    except ValueError as error:
        result["status"] = "parse_failed"
        result["error"] = str(error)
    except Exception as error:  # unexpected but handled: still report as data
        result["status"] = "parse_failed"
        result["error"] = f"unexpected extraction failure ({type(error).__name__})"

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "worker_result.json").write_text(
        json.dumps(result, sort_keys=True, indent=1), "utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
