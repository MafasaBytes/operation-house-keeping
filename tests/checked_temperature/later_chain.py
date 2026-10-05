"""TEST-SIDE builder: a coherent LATER synthetic evidence chain (amendment C1.3).

Every layer is rebuilt through existing public functions at a later declared
time. No backend contract is altered and no validation is relaxed:

- data_sources ingestion of a scripted Moonraker response, with an injected
  clock and an HTTP Date header at the later time;
- temporal projection;
- identity-binding assertions and source-property interpretations whose
  applicability windows cover the new receipt (new records, new hashes);
- semantic compatibility, constraint evaluation and state classification at
  the later as_of, over the unchanged baseline model revision.

Synthetic: a declared-time chain built by tests, not a physical acquisition or
authenticated chronology.
"""
import copy
import email.utils
import functools
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from tests.checked_temperature.fixtures import canon, public_evidence_bytes

_BASE = {'dir': None}
WINDOW = timedelta(hours=1)


def set_base(path):
    _BASE['dir'] = Path(path)


class _Clock:
    """Deterministic injected clock: one second per call, as the accepted FakeClock."""

    def __init__(self, start):
        self._now = start

    def __call__(self):
        self._now += timedelta(seconds=1)
        return self._now


def _iso(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


@functools.lru_cache(maxsize=None)
def later_evidence_bytes(value, start='2026-10-05T09:01:00Z', as_of='2026-10-05T09:05:00Z'):
    from backend.data_sources.adapters.moonraker import MoonrakerAdapter
    from backend.data_sources.catalog import InMemorySourceCatalog
    from backend.data_sources.connectors import HttpApiConnector, LocalFileConnector, StaticCredentialResolver
    from backend.data_sources.connectors.http_api import TransportResponse
    from backend.data_sources.raw_store import FilesystemRawStore
    from backend.data_sources.runtime import IngestionRunner
    from backend.temporal_state.projector import TemporalProjector
    from backend.temporal_state.queries import TemporalQueries
    from backend.temporal_state.store import TemporalStore
    from backend.identity_binding.canonical import build_record as ib_build
    from backend.identity_binding.contracts import AppliesScope, AuthorityRef as IbAuthority, BindingAssertion, \
        DeclaredBoundary
    from backend.source_interpretation import (InterpretationResolver, InterpretationStore,
                                               ObservationRoleInterpretation, QuantityKindInterpretation,
                                               SourcePropertyInterpretation, UnitInterpretation,
                                               build_record as interpretation_build)
    from backend.constraint_evaluation import ConstraintEvaluationQueries
    from backend.state_classification import StateClassificationQueries, StateClassificationResult
    from tests.data_sources.test_ingestion_runner_api import FIXTURES, make_source
    from tests.data_sources.test_http_api_connector import ScriptedTransport
    from tests.behavior_evaluation.helpers import E1, semantic_queries
    from tests.model_state.helpers import PROP_TARGET, PROP_TEMP, SUBJECT, entity_declaration, var_declaration
    from tests.model_kernel.builders import VAR_A, VAR_B, observation_role, quantity_kind
    from tests.model_kernel.bh001_slice_a_helpers import semantic_lock
    from tests.state_classification.helpers import AS_OPERATED, STATE_A, condition_sources, state_model

    t0 = datetime.fromisoformat(start)
    cutoff = datetime.fromisoformat(as_of)
    root = _BASE['dir'] / ('chain-%s-%s' % (value.replace('.', '_'), _iso(t0).replace(':', '')))
    root.mkdir(parents=True)
    # 1. Source boundary: scripted Moonraker response at the later time.
    body = json.loads((FIXTURES / 'moonraker_printer_objects.json').read_bytes())
    body['result']['status']['extruder']['temperature'] = json.loads(value)
    date = email.utils.format_datetime(t0 + timedelta(seconds=5), usegmt=True)

    def response(data):
        return TransportResponse(status=200, headers={'Content-Type': 'application/json', 'Date': date}, body=data)
    script = {'/server/info': response((FIXTURES / 'moonraker_server_info.json').read_bytes()),
              '/printer/objects/query': response(json.dumps(body).encode())}
    connector = HttpApiConnector(adapters={'moonraker': MoonrakerAdapter()}, transport=ScriptedTransport(script),
                                 credential_resolver=StaticCredentialResolver({}), clock=_Clock(t0))
    catalog = InMemorySourceCatalog()
    catalog.register(make_source())
    raw = FilesystemRawStore(root / 'ds' / 'raw_store')
    runner = IngestionRunner(catalog=catalog, store=raw,
                             connectors={'local_file': LocalFileConnector(), 'http_api': connector},
                             clock=_Clock(t0))
    assert runner.run('printer-1').status == 'succeeded'
    temporal_store = TemporalStore(root / 'temporal.db', evidence_root=raw.base_dir)
    TemporalProjector(raw, temporal_store).project('printer-1')
    temporal = TemporalQueries(temporal_store)
    # 2. Unchanged baseline model revision (constraint A upper 50, as the committed generator).
    model = state_model(root, upper_a='50')[0]
    baseline = json.loads(public_evidence_bytes())
    revision = baseline['snapshot']['state']['material']['revision']['revision_id']
    assert model.load().revision.revision_id == revision, 'model revision differs from the baseline'
    # 3. Bindings and interpretations whose windows cover the later receipt.
    applies = AppliesScope(axis='ingestion_received_at',
                           start_boundary=DeclaredBoundary(kind='declared', at=t0 - WINDOW),
                           end_boundary=DeclaredBoundary(kind='declared', at=t0 + WINDOW),
                           interval_semantics='half_open')
    recorded = t0 - timedelta(minutes=30)
    ib_authority = IbAuthority(kind='test_fixture', agent='gate1_c1_later_chain', method='manual_declaration')
    bindings = (entity_declaration(E1, 'Demo entity'), var_declaration(VAR_A, E1, 'Variable A'),
                var_declaration(VAR_B, E1, 'Variable B'),
                ib_build(BindingAssertion, binding_kind='property', subject=SUBJECT, property=PROP_TEMP,
                         target_anchor_id=VAR_A, applies=applies, recorded_at=recorded, authority=ib_authority,
                         note=''),
                ib_build(BindingAssertion, binding_kind='property', subject=SUBJECT, property=PROP_TARGET,
                         target_anchor_id=VAR_B, applies=applies, recorded_at=recorded, authority=ib_authority,
                         note=''))
    istore = InterpretationStore(root / 'interpretations' / 'demo-printer')
    for prop in (PROP_TEMP, PROP_TARGET):
        role = 'measured' if prop == PROP_TEMP else 'reported'
        for interpretation in (
                QuantityKindInterpretation(dimension='quantity_kind', quantity_kind=quantity_kind()),
                ObservationRoleInterpretation(dimension='observation_role', observation_role=observation_role(role)),
                UnitInterpretation(dimension='unit', unit=semantic_lock(VAR_A).signature.unit)):
            istore.append(interpretation_build(SourcePropertyInterpretation, subject=SUBJECT, property=prop,
                                               interpretation=interpretation, applies=applies, supersedes=(),
                                               recorded_at=recorded, authority=ib_authority, note=''))
    semantic = semantic_queries(root, model=model, temporal=temporal, binding_records=bindings,
                                interpretations=InterpretationResolver(istore.load()))
    # 4. Classification at the later as_of through the public facade.
    result = StateClassificationQueries(ConstraintEvaluationQueries(semantic)).state_classification(
        STATE_A, context=AS_OPERATED, as_of=cutoff, condition_sources=condition_sources())
    snapshot = json.loads(canon(result.model_dump(mode='json')))
    assert StateClassificationResult.model_validate_json(canon(snapshot)) == result
    evidence = copy.deepcopy(baseline)
    evidence['question']['as_of'] = _iso(cutoff)
    evidence['id'] = 'E-later-' + value.replace('.', '_')
    evidence['snapshot'] = snapshot
    return canon(evidence)


def occurrence_finished_at(evidence_bytes):
    e = json.loads(evidence_bytes)
    b = e['binding']
    c = e['snapshot']['constraint_evaluations'][b['constraint_evaluation_index']]['semantic_compatibility'][
        'candidates'][b['semantic_candidate_index']]
    return c['value_candidate']['state_candidate']['bound']['observed']['occurrence']['finished_at']


def occurrence_received_at(evidence_bytes):
    e = json.loads(evidence_bytes)
    b = e['binding']
    c = e['snapshot']['constraint_evaluations'][b['constraint_evaluation_index']]['semantic_compatibility'][
        'candidates'][b['semantic_candidate_index']]
    return c['value_candidate']['state_candidate']['bound']['observed']['occurrence']['received_at']


def with_finished_at(evidence_bytes, new, tag):
    """Move every copy of the bound occurrence's finished_at (occurrence and attempt copies),
    nothing else rebuilt. The owning validators accept this (amendment C1 TC5b)."""
    old = occurrence_finished_at(evidence_bytes)
    text = json.dumps(json.loads(evidence_bytes)).replace('"finished_at": "%s"' % old, '"finished_at": "%s"' % new)
    e = json.loads(text)
    e['id'] = 'E-finished-moved-' + tag
    return e
