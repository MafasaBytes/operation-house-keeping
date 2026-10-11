"""Public-interface composition of fresh synthetic and reconstruction stores.

No backend ledger is created. All model/binding/interpretation material comes
from C and is revalidated by its owning public interfaces.
"""
import copy
from contextlib import nullcontext
from pathlib import Path
from urllib.parse import urlsplit

from .t1_contracts import canonical_bytes, instant, refuse


def context_components(context):
    from pydantic import TypeAdapter
    from backend.model_kernel import ModelQueryMaterial
    from backend.identity_binding.contracts import LedgerRecord
    from backend.identity_binding.contracts import IdentityBindingError
    from backend.identity_binding.store import validate_record_collection as bindings
    from backend.source_interpretation.contracts import InterpretationRecord
    from backend.source_interpretation.errors import SourceInterpretationError
    from backend.source_interpretation.store import validate_record_collection as interpretations
    model = ModelQueryMaterial.model_validate(context['material']).loaded()
    try:
        binding_records = TypeAdapter(list[LedgerRecord]).validate_python(context['bindings'])
        binding = bindings(context['binding_set_id'], {r.record_id: r for r in binding_records})
    except (ValueError, IdentityBindingError):
        refuse('SIM_CONTEXT_MISMATCH', 6, '/C/bindings')
    try:
        interpretation_records = TypeAdapter(list[InterpretationRecord]).validate_python(context['interpretations'])
        interpretation = interpretations(context['interpretation_set_id'],
                                         {r.record_id: r for r in interpretation_records})
    except (ValueError, SourceInterpretationError):
        refuse('SIM_CONTEXT_MISMATCH', 6, '/C/interpretations')
    return model, binding, interpretation


def validate_context(context, start, end):
    from backend.data_sources.contracts import SourceDefinition
    try:
        SourceDefinition.model_validate(context['source_definition'])
        origin = urlsplit(context['source_definition']['configuration']['base_url'])
        if origin.hostname != '127.0.0.1' or origin.port is not None and not 0 < origin.port <= 65535:
            raise ValueError('origin')
    except ValueError:
        refuse('SIM_MEASUREMENT_LOCATOR_MISMATCH', 6, '/C/source_definition')
    try:
        _model, binding, interpretation = context_components(context)
    except ValueError:
        refuse('SIM_CONTEXT_MISMATCH', 6, '/C/material')
    # Applicability is evaluated on effective scopes, not merely record assertions.
    for field, loaded, records in (('bindings', binding, context['bindings']),
                                    ('interpretations', interpretation, context['interpretations'])):
        for i, record in enumerate(records):
            scope = loaded.effective_applies.get(record['record_id'])
            if scope is None:
                continue  # Anchor declarations have no temporal applies scope.
            lo, hi = scope.start_boundary, scope.end_boundary
            if (lo.kind == 'declared' and lo.at > start) or (hi.kind == 'declared' and hi.at <= end):
                refuse('SIM_CONTEXT_MISMATCH', 6, '/C/' + field + '/' + str(i) + '/applies')


def classify(context, raw, db_path, target, baseline, target_digest, *, memory=False):
    from pydantic import TypeAdapter
    from backend.temporal_state.store import TemporalStore
    from backend.temporal_state.projector import TemporalProjector
    from backend.temporal_state.queries import TemporalQueries
    from backend.identity_binding.resolver import BindingResolver
    from backend.source_interpretation import InterpretationResolver
    from backend.model_state import ModelStateQueries
    from backend.observation_compatibility import ObservationCompatibilityQueries
    from backend.semantic_compatibility import SemanticCompatibilityQueries
    from backend.constraint_evaluation import ConstraintEvaluationQueries
    from backend.state_classification import StateClassificationQueries, StateClassificationResult, StateConditionSource
    from backend.model_kernel.contracts import AssertionContext
    model, binding, interpretations = context_components(context)
    # Constructor writes: always a NEW diagnostic DB, never a retained DB or baseline store.
    if memory:
        from .t1_temporal_memory import MemoryTemporalStore
        store = MemoryTemporalStore(db_path, evidence_root=raw.base_dir)
    else:
        store = TemporalStore(db_path, evidence_root=raw.base_dir)
    try:
        projection = TemporalProjector(raw, store).project('printer-1')
        if projection.halted is not None:
            refuse('SIM_DERIVATION_MISMATCH', 7, '/evidence/projection')
        temporal = TemporalQueries(store)
        state = ModelStateQueries(model, BindingResolver(binding), temporal)
        compatibility = SemanticCompatibilityQueries(ObservationCompatibilityQueries(state),
                                                      InterpretationResolver(interpretations))
        result = StateClassificationQueries(ConstraintEvaluationQueries(compatibility)).state_classification(
            context['state_anchor_id'], context=TypeAdapter(AssertionContext).validate_python(context['assertion_context']),
            as_of=instant(target['question_as_of']),
            condition_sources=tuple(StateConditionSource.model_validate(x) for x in context['condition_sources']))
        snapshot = result.model_dump(mode='json')
        # Explicit owning public round trip; no truth label is added.
        StateClassificationResult.model_validate(snapshot)
        evidence = copy.deepcopy(baseline)
        evidence['id'] = 'E-t1-' + target_digest[:59]
        evidence['question']['as_of'] = target['question_as_of']
        evidence['snapshot'] = snapshot
        # Filesystem connections are short-lived; a logical-memory adapter has
        # one private connection, closed by finally after the last dump.
        logical = store.ordered_logical_dump()
        return canonical_bytes(evidence), canonical_bytes(snapshot), canonical_bytes(projection.model_dump(mode='json')), canonical_bytes(logical)
    finally:
        if memory:
            store.close()


def produce(*, objects, prior_files, pins, prior_pins, build, workspace, observe=None, output_only=False, publication=None):
    """Re-admit immediately before any production, including arithmetic/allocation."""
    from .t1_records import preflight
    phase = observe if observe is not None else lambda _name: nullcontext()
    with phase('admission_validation'):
        admitted = preflight(objects=objects, prior_files=prior_files, pins=pins,
                             prior_pins=prior_pins, build=build)
    from backend.data_sources.adapters.moonraker import MoonrakerAdapter
    from backend.data_sources.catalog import InMemorySourceCatalog
    from backend.data_sources.contracts import SourceDefinition
    from backend.data_sources.connectors import HttpApiConnector, StaticCredentialResolver
    from backend.data_sources.raw_store import FilesystemRawStore
    from backend.data_sources.runtime import IngestionRunner
    from .t1_carrier import Clocks, Transport, derive
    j = admitted.root('J')
    c, w = admitted.get(j['context']), admitted.get(j['world'])
    model = admitted.get(admitted.get(j['execution_target'])['model'])
    baseline = admitted.get(model['baseline_evidence'])
    rule = admitted.get(j['rule'])
    bounds = j['resource_bounds']
    bodies = derive(admitted.objects[c['preset']['sha256']], w, j,
                    {'J': admitted.references['J']['sha256'], 'G': admitted.references['G']['sha256'],
                     'W': j['world']['sha256']})
    root = Path(workspace)
    if not output_only:
        root.mkdir()
    clocks = Clocks(j['t0'], wall_limit=bounds['wall_clock_calls'], monotonic_limit=bounds['monotonic_calls'])
    transport = Transport(c['source_definition']['configuration']['base_url'], bodies, j['t0'],
                          max_response_bytes=min(16384, bounds['response_bytes']))
    connector = HttpApiConnector(adapters={'moonraker': MoonrakerAdapter()}, transport=transport,
        credential_resolver=StaticCredentialResolver({}), clock=clocks.wall('connector'),
        monotonic=clocks.monotonic('connector'), request_timeout_seconds=rule['transport']['request_timeout_seconds'],
        sweep_deadline_seconds=rule['transport']['sweep_deadline_seconds'],
        max_response_bytes=min(16384, bounds['response_bytes']), max_retries=0,
        resolve_addresses=lambda host: ['127.0.0.1'] if host == '127.0.0.1' else [])
    catalog = InMemorySourceCatalog()
    catalog.register(SourceDefinition.model_validate(c['source_definition']))
    if output_only:
        from .t1_memory_store import RawStore
        raw = RawStore(root / 'evidence/raw', publication=publication)
        db = root / 'evidence/db/temporal.db'
        db.parent.mkdir(parents=True, exist_ok=True)
    else:
        raw = FilesystemRawStore(root / 'raw')
        db = root / 'temporal.db'
    with phase('backend_acquisition'):
        run = IngestionRunner(catalog=catalog, store=raw, connectors={'http_api': connector},
                              clock=clocks.wall('runner')).run('printer-1')
    if run.status != 'succeeded' or len(transport.calls) != 2:
        refuse('SIM_DERIVATION_MISMATCH', 7, '/evidence/run')
    with phase('classification'):
        artifacts = classify(c, raw, db, j, baseline, admitted.references['J']['sha256'])
    return {'public_evidence': artifacts[0], 'snapshot': artifacts[1], 'projection': artifacts[2],
            'logical': artifacts[3], 'run': canonical_bytes(run.model_dump(mode='json')),
            'wall_clock': canonical_bytes(clocks.wall_calls), 'monotonic': canonical_bytes(clocks.monotonic_calls),
            'transport': canonical_bytes(transport.calls), 'raw_root': raw.base_dir,
            'admission': admitted, 'store': raw, 'db_path': db}
