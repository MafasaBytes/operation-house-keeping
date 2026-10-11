"""Transport-free independent retained-record reconstruction.

Recomputes the two fixed successful API events from pinned inputs. Uses owning
public contracts, identity functions and adapter extraction, never a connector,
runner, transport callback or retained SQLite database.
"""
from datetime import timedelta
from email.utils import format_datetime
from urllib.parse import urlsplit
from contextlib import nullcontext
from fractions import Fraction
import copy
import json
from .t1_contracts import canonical_bytes, instant, sha, refuse
from .t1_memory_store import RawStore


def raw_records(admission, root):
    from backend.data_sources.adapters.moonraker import MoonrakerAdapter
    from backend.data_sources.contracts import RawRecord, AcquisitionAttempt, ApiSourceLocator, ExtractionResult, ApiObservationsResult, IngestionRun
    from backend.data_sources.provenance import derive_keyed_record_id, derive_entity_id
    from .t1_carrier import PATHS
    from .t1_oracle import receipt_values, _decimal
    a = admission
    j = a.root('J')
    c, w = a.get(j['context']), a.get(j['world'])
    comparands = receipt_values(j, a.root('E'), a.get)
    preset = json.loads(a.objects[c['preset']['sha256']], parse_float=Fraction)
    marker = dict(logical_run_id=j['logical_run_id'], simulation_target_sha256=a.references['J']['sha256'],
                  simulation_permission_sha256=a.references['G']['sha256'], world_sha256=j['world']['sha256'])
    def wire(value):
        if value is None: return b'null'
        if type(value) is bool: return b'true' if value else b'false'
        if isinstance(value, (int, Fraction)): return _decimal(Fraction(value)).encode('ascii')
        if isinstance(value, str): return json.dumps(value, ensure_ascii=False).encode('utf-8')
        if isinstance(value, list): return b'[' + b','.join(wire(v) for v in value) + b']'
        if isinstance(value, dict): return b'{' + b','.join(wire(k) + b':' + wire(value[k]) for k in sorted(value)) + b'}'
        raise TypeError('independent carrier domain')
    bodies = []
    for name in ('server_info', 'printer_objects'):
        body = copy.deepcopy(preset['responses'][name]['body'])
        if name == 'printer_objects':
            body['result']['status']['extruder']['temperature'] = Fraction(comparands['r'])
        body['_application_simulation'] = marker
        bodies.append(wire(body))
    origin = c['source_definition']['configuration']['base_url']
    start = instant(j['t0'])
    tick = lambda k: start + timedelta(seconds=k)
    headers = {'Content-Type': 'application/json', 'Date': format_datetime(tick(5), usegmt=True)}
    raw = RawStore(root)
    adapter = MoonrakerAdapter()
    plan = adapter.plan()
    if tuple(item.path_and_query for item in plan) != PATHS:
        refuse('SIM_DERIVATION_MISMATCH', 7, '/evidence/transcripts/transport')
    wall, transport = [], []
    # Fixed fresh-store successful sweep: runner(1), connector(2..4),
    # runner(5), connector(6..8), runner(9..10).
    for k in range(1, 11):
        wall.append(dict(caller='runner' if k in (1, 5, 9, 10) else 'connector', ordinal=k, tick=k))
    mono = [dict(caller='connector', ordinal=k, tick=k) for k in range(1, 8)]
    run_id = 'run-printer-1-0001'
    for position, (item, body) in enumerate(zip(plan, bodies)):
        began, ended, captured = ((2, 4, 5) if position == 0 else (6, 8, 9))
        checksum = raw.put_payload(body)
        record_id = derive_keyed_record_id('printer-1', item.item_key, checksum)
        canonical = 'GET ' + item.path_and_query
        fingerprint = 'sha256:' + sha((origin + ' ' + canonical).encode())
        locator = ApiSourceLocator(adapter_id=adapter.adapter_id, endpoint_id=item.endpoint_id,
            item_key=item.item_key, request_fingerprint=fingerprint, request_canonical=canonical,
            source_content_type='application/json', extraction_route=adapter.extraction_route)
        envelope = RawRecord(record_id=record_id, source_id='printer-1', source_native_id=None,
            ingestion_run_id=run_id, captured_at=tick(captured), source_observed_at=None,
            content_type='application/json', payload_checksum=checksum, immutable_payload_reference=checksum,
            provenance={'acquisition_mode': 'poll', 'connector_type': 'http_api'}, quality_flags=[], api_locator=locator)
        raw.put_envelope(envelope)
        raw.put_attempt(AcquisitionAttempt(attempt_id=derive_entity_id(run_id, 'attempt', item.item_key + ':0'),
            ingestion_run_id=run_id, source_id='printer-1', item_key=item.item_key, adapter_id=adapter.adapter_id,
            endpoint_id=item.endpoint_id, sweep_position=position, started_at=tick(began), finished_at=tick(ended),
            received_at=tick(ended), outcome='succeeded', request_fingerprint=fingerprint, request_canonical=canonical,
            target_origin=origin, status_code=200, allowlisted_headers=headers, transport_security='plaintext_http_explicit',
            response_size_bytes=len(body), retries_used=0, payload_checksum=checksum, raw_record_id=record_id,
            payload_reused=False, failure=None))
        extracted = adapter.extract(body, record_id, item.item_key)
        raw.put_extraction(ExtractionResult(raw_record_id=record_id, extractor=extracted.extractor,
            outcome='succeeded', warnings=[], result=ApiObservationsResult(manifest=extracted)))
        parts = urlsplit(item.path_and_query)
        transport.append(dict(ordinal=position + 1, origin=origin, path=parts.path, query=parts.query,
            request_header_names=[], response_status=200, response_headers=sorted(headers.items())))
    run = IngestionRun(run_id=run_id, source_id='printer-1', started_at=tick(1), finished_at=tick(10),
        status='succeeded', records_seen=2, records_accepted=2, records_duplicate=0, records_quarantined=0,
        records_partial=0, attempts_planned=2, attempts_succeeded=2, attempts_failed=0, error_summary=None)
    raw.put_run(run)
    return raw, dict(run=canonical_bytes(run.model_dump(mode='json')), wall_clock=canonical_bytes(wall),
                    monotonic=canonical_bytes(mono), transport=canonical_bytes(transport))


def reconstruct(*, admission, workspace, observe=None):
    from pathlib import Path
    from .t1_acquisition import classify
    from .t1_package import safe_new_dir
    root = safe_new_dir(workspace, '/argv/scratch-dir')
    a = admission
    raw, records = raw_records(a, root / 'raw')
    root.mkdir()
    j = a.root('J')
    model = a.get(a.get(j['execution_target'])['model'])
    baseline = a.get(model['baseline_evidence'])
    phase = observe if observe is not None else lambda _name: nullcontext()
    with phase('transport_free_classification'):
        evidence, snapshot, projection, logical = classify(a.get(j['context']), raw, root / 'temporal.db',
                                                         j, baseline, a.references['J']['sha256'])
    return dict(records, public_evidence=evidence, snapshot=snapshot, projection=projection, logical=logical,
                store=raw, raw_root=raw.base_dir, db_path=root / 'temporal.db', admission=a)
