# DS-004 Bounded Read-Only Operational API & Telemetry — Design

Date: 2026-08-07
Status: Approved by project owner (amended twice; final amendments
incorporated). Showcase target: Moonraker (Klipper). No further design
approval required unless Task 0 had invalidated an assumption — it did
not (see Spike results).

## What this slice validates

One real operational source supplying current-state measurements through
a bounded, read-only HTTP snapshot sweep — completing the required Source
Profile families and preparing the ground for the later temporal/state
layer, which DS-004 must not anticipate or fabricate.

## Architecture

```
connectors/http_api.py    generic GET-only connector; injectable transport
                          + CredentialResolver; bounded pull-based iterator
                          of AcquisitionSucceeded | AcquisitionFailed
adapters/moonraker.py     endpoint plan, canonical requests + fingerprints,
                          {"result": ...} envelope interpretation, subject
                          and observation selection (all Moonraker-specific)
extractors/operational.py vendor-neutral helpers: hardened bounded JSON,
                          RFC 6901 escaping, canonical serialization,
                          source-time markers
runtime/                  persist-before-next-pull loop, attempt records,
                          content dedup, routes, quarantine, replay, health
(later temporal layer)    joins attempts (occurrences) with per-payload
                          observations via attempt.raw_record_id
```

No worker subprocess: extraction is hardened stdlib JSON on size-capped
bytes; acquisition is bounded network I/O. Confirmed acceptable by the
Task 0 spike (parser and transport checks all green).

## Occurrence vs payload

- **AcquisitionAttempt** — persisted for every attempted item: successes,
  failures, and byte-identical repeats. New write-once store area
  `attempts/`.
- **Payload/RawRecord** — content-addressed as before. A byte-identical
  re-poll creates no new raw record; its new attempt references the
  existing `raw_record_id` with `payload_reused=true`.
- API raw-record identity: `derive_keyed_record_id(source_id, item_key,
  payload_checksum)`. Sweep position is ordering evidence only
  (`sweep_position` on the attempt). DS-001–003 positional identity is
  untouched.
- Temporal-layer join (future): `attempt.raw_record_id →
  observations(raw_record_id)` — occurrence timelines without
  re-extraction. DS-004 performs no cross-payload comparison of any kind
  (`unchanged_value` and `duplicate_event` are explicitly out; replay is
  a pure function of one stored payload).

## Connector boundary

`acquire_events(source) -> Iterator[AcquisitionSucceeded |
AcquisitionFailed]`, pull-based and bounded. The runtime persists payload
→ raw record → successful attempt **before pulling the next event**; a
failure at endpoint two cannot discard endpoint one. A failed event
writes only its failed attempt. `LocalFileConnector` yields one
successful event (positional identity, no attempt evidence) — DS-001–003
behavior and identifiers unchanged.

**Commit order for a successful event** (failure-injection tested):

```
1. payload (content-addressed)
2. RawRecord envelope — or resolve the existing keyed record
3. successful AcquisitionAttempt   <- the commit record
4. extraction + extraction envelope / quarantine
```

A crash before step 3 may leave an uncommitted payload or API envelope;
the store's integrity audit (`find_uncommitted_api_artifacts`) detects
API-keyed envelopes with no committed successful attempt so they are
never mistaken for completed acquisition evidence.

## Endpoint plan (fixed, bounded, no pagination/cursors)

1. `server_info` — `GET /server/info`.
2. `printer_objects` — one object-query snapshot with the corrected
   bounded selection:
   - `extruder`: temperature, target
   - `heater_bed`: temperature, target
   - `toolhead`: homed_axes, position
   - `print_stats`: state, print_duration, total_duration
   - `virtual_sdcard`: progress, is_active

   (`progress` is a `virtual_sdcard` field, not `print_stats`.)

Canonical request: objects and attributes sorted; persisted verbatim as
`request_canonical` plus `request_fingerprint = sha256:<full 64-hex>`.
Optional/configuration-dependent objects (`heater_bed`,
`virtual_sdcard`) omitted by Moonraker are **requested-but-omitted
evidence** (`requested_field_omitted` warnings, documented API behavior)
— never malformed responses, never schema drift. Pagination and cursors
remain reserved contract concepts with no machinery.

## Contracts

**AcquisitionAttempt**: `attempt_id` (deterministic per run:
run_id+item_key+ordinal), `ingestion_run_id`, `source_id`, `item_key`,
`adapter_id`, `endpoint_id`, `sweep_position`, `started_at`/`finished_at`
(always, ingestion clock), `received_at` (**optional — present only when
a response was received**; timeouts never fabricate it), `outcome:
succeeded | failed`, `request_fingerprint` (full tagged sha256),
`request_canonical`, `target_origin` (sanitized scheme://host:port —
provenance survives config changes), `status_code | None`,
`allowlisted_headers` (fixed allowlist, bounded, sanitized),
`transport_security: tls_verified | plaintext_http_explicit`,
`response_size_bytes | None`, `retries_used`, `payload_checksum` /
`raw_record_id` / `payload_reused` (success only), `failure {error_code,
redacted_message} | None`.

**RawRecord.api_locator** (optional, default None; old JSON valid):
`adapter_id`, `endpoint_id`, `item_key`, `request_fingerprint`,
`request_canonical`, `source_content_type | None` (**optional** —
responses may omit it; missing/unexpected content type with valid bounded
JSON ⇒ explicit warning, never a silent rewrite), `extraction_route`
(e.g. `api:moonraker:v1`). Response bytes exist **only** in the payload
store — never in attempts, locators, or run reports (attempts carry size
and checksum only).

**SourceTimeMarker** (discriminated by `kind`):
`wall_clock {value: aware datetime, basis}` |
`monotonic {value: exact number lexeme as string, unit: "seconds",
clock_id, origin: "unknown", pointer}` | `unavailable {reason}`.
Moonraker observations carry `monotonic` markers from
`/result/eventtime`; `server_info` observations carry `unavailable`.
Ingestion timestamps are aware wall-clock and never presented as
comparable to eventtime.

**OperationalObservation**: `observation_id`
(raw_record_id+extractor_version+pointer), `raw_record_id`,
`json_pointer` (RFC 6901, `~`→`~0`, `/`→`~1`, tested against hostile
names), `subject_identifier` (source-native), **`value_json`**
(deterministic canonical JSON text of the selected property) +
`json_type (object|array|string|number|boolean|null)`, `declared_unit:
None` (Moonraker declares none), `semantics: "snapshot"`, `source_time:
SourceTimeMarker`, `quality_flags`.

**Canonical value serialization** (amendment 2, spike-proven): payloads
parse with `parse_int=int, parse_float=Decimal` (bounded lossless number
tokens); the canonical serializer emits numeric lexemes as JSON numbers
(never quoted), strings as JSON strings, arrays in order, object keys
sorted, no whitespace. `[1.0, 2.0]` is distinguishable from
`["1.0","2.0"]`; exponent input `1e3` canonicalizes to the JSON number
`1E+3`; toolhead position survives as a numeric array. The immutable
payload + pointer remain source truth; `value_json` is an
extractor-produced canonical representation.

Granularity: one observation per selected property at
`/result/status/{escaped-object}/{escaped-property}`; arrays stay arrays
(no inferred axis splitting). `server_info`: fixed selected top-level
properties (`klippy_connected`, `klippy_state`), subject `server`.

**ApiExtractionManifest**: observations, per-item summaries,
`levels_supported=[0,1,2]` (L0 raw responses; L1 request/response/
envelope structure; L2 field-level observations), warnings,
`unsupported_features`. Joins the `ExtractionResult` union as
`ApiObservationsResult (kind="api_observations")`.

**ApiHealthEvidence** (typed; no string-encoded values):
`consecutive_attempt_failures: int`, `last_attempt_error_code: str |
None`, `last_status_code: int | None`, `last_retry_after_seconds: float |
None`, `clock_skew_seconds: float | None`, `plaintext_http_explicit:
bool`, `last_successful_attempt_at: datetime | None`. Attached to
`SourceHealth` as optional `api_evidence` (default None; old JSON valid).

## Run accounting and status precedence (amendment 5)

`IngestionRun` gains `attempts_planned/succeeded/failed` (ge 0, default
0 — old JSON valid). Existing counters keep their meanings exactly;
acquisition failure overloads nothing. `RunStatus` gains
`completed_with_acquisition_failures`. Precedence (documented + tested):

```
1. failed                                (no meaningful acquisition progress)
2. completed_with_quarantine             (≥1 retrieved record quarantined,
                                          even if attempts also failed)
3. completed_with_acquisition_failures   (≥1 attempt failed, no quarantine)
4. succeeded
```

Attempt counters always expose combined cases; the status never hides an
acquisition failure. Old persisted JSON remains readable.

## Extraction routing

Media type stays `application/json` as a *reported fact*; dispatch uses
the explicit route stored on the raw record (`api:moonraker:v1`).
Arbitrary JSON is never given Moonraker semantics. Replay reads the
stored route — fully offline.

## Hardened JSON parsing (spike-proven)

Byte-size cap; nesting depth ≤ 64; node count ≤ 100k; string length ≤
64 kB; **duplicate object keys rejected** (provenance would be
ambiguous); NaN/Infinity rejected; strict UTF-8 (failure ⇒ quarantine);
iterative depth/node audit. Malformed/unusable envelope ⇒ quarantine
`EXTRACT_API_MALFORMED_JSON` (raw preserved); unknown optional keys ⇒
`schema_drift` warnings; omitted requested fields ⇒
`requested_field_omitted` (see Endpoint plan).

## Network security policy (amendments 8, 10)

HTTPS verified normally, always; **unverified HTTPS does not exist**.
Plaintext HTTP only with explicit configuration, restricted to loopback
or approved private-LAN targets, stamped `plaintext_http_explicit`.
Scheme/host/port pinned for the sweep; redirects refused
(`ACQUIRE_REDIRECT_REFUSED`); proxy-environment inheritance disabled
(explicit handler list — spike-proven against a poisoned `HTTP_PROXY`);
URLs never derived from response content. Every request re-resolves the
configured hostname immediately before connection and validates **all**
returned addresses: link-local (incl. 169.254.169.254 metadata),
multicast, and unspecified always rejected; loopback and RFC-1918
per policy; **IPv6 unique-local (fc00::/7) handled explicitly** (allowed
only under the private-LAN policy, never by accident). Residual stdlib
DNS-rebinding window between resolution and connection is an accepted,
documented DS-004 limitation (owner decision; Task 0 showed no cheap
practical bypass elimination without custom IP-pinned connections).
Credentials via an injected `CredentialResolver` protocol; resolved
values exist only in memory during request construction and all
persisted strings pass the existing scrub/sanitize policy. Rate limits:
no documented client quota identified for Moonraker; 429/`Retry-After`
handled conservatively with typed evidence. Bounds: per-request timeout,
total sweep deadline, response-size cap, bounded gzip expansion
(spike-proven), retry limit with `retries_used`.

## Validation semantics (amendments 7, 11)

Transport-stub + loopback tests ⇒ connector/adapter
implemented/**experimental**. `validated` requires an accepted run
against **actual Moonraker software** (virtual Klipper/printer stack
acceptable; fake server explicitly insufficient). Virtual-stack safety
conditions: version/commit pinned; images pinned by digest; no
privileged containers, host networking, or device passthrough; loopback
binding only; isolated temporary data directory; exact versions and
configuration recorded; no credentials or host paths in committed
fixtures. If a safe real-software stack cannot be established, DS-004
completes honestly at experimental/`next` with the missing evidence
stated. Source Profile v2 enables `operational_api_or_telemetry`
(required/next); availability = stdlib (trivially honest); the
`validated` rung is never weakened.

### Task 0 spike results (2026-08-07 — gate PASSED, 15/15)

WSL2 Ubuntu x86_64, CPython 3.13.11, stdlib-only transport against a
loopback `http.server` (+ ad-hoc TLS server with a self-signed cert):
envelope GET ✓; redirect refusal via explicit no-redirect handler ✓;
poisoned `HTTP_PROXY`/`http_proxy` ignored with an explicit handler
list ✓; address classification incl. IPv6 ULA and metadata endpoint ✓;
pre-connect `getaddrinfo` screening usable ✓; self-signed HTTPS fails
closed (`CERTIFICATE_VERIFY_FAILED`) ✓; 50 MB gzip bomb capped at the
configured expansion limit during streaming read ✓; total-sweep deadline
aborts remaining items ✓; incremental persistence keeps endpoint 1
durable after endpoint 2 fails ✓; duplicate-key rejection, NaN
rejection, strict UTF-8, depth bound ✓; canonical number preservation
(`[1.0,2.0,0.3]` vs `["1.0"]`, `1e3 → 1E+3`, int vs non-int) ✓.
The no-worker decision stands.

## Exclusions

No write/command verbs; no WebSocket/MQTT/OPC UA; no polling daemon
(bounded sweeps, external scheduling); no unit conversion or inference;
no component-identity resolution; no temporal/state comparison of any
kind; no alerting; no cloud services; no fixtures captured from real
third-party services.

## Acceptance criteria

All fixture scenarios (see plan §Fixtures) pass; every attempt persisted
incl. byte-identical repeats and per-endpoint failures, correctly
referencing reused raw records; keyed API record ids with DS-001–003 ids
untouched (246-test baseline green); response bytes only in the payload
store; run precedence and attempt counters per this spec; routing via
`api:moonraker:v1`; every observation carries a SourceTimeMarker and
canonical `value_json` with number-type preservation proven; replay pure
and offline after service shutdown; commit-order failure injection with
uncommitted-artifact detection; no secret material in any persisted
artifact; typed health evidence for partial acquisition; dual
clean-checkout verification; validation status honest per above.

## Next open question (after DS-004)

All required Source Profile families are then validated or
evidence-pending: the next milestone decision is the first
normalization/temporal-layer slice (joining attempts with observations)
versus OCR (PDF Level 4) — owner's call with the DS-004 evidence in
hand.
