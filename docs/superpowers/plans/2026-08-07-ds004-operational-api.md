# DS-004 Operational API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Bounded read-only Moonraker snapshot ingestion with per-attempt
occurrence evidence, keyed content-deduplicated raw records, canonical
number-preserving observations with field-level provenance, honest
partial-run accounting, and pure offline replay.

**Authority:** the spec
(`docs/superpowers/specs/2026-08-07-ds004-operational-api-design.md`) for
every contract field, bound, precedence rule, and security requirement;
ADR-0004 for target/transport/isolation decisions. Task 0 (spike) has
already passed 15/15 — recorded in the spec.

## Global Constraints

- All DS-001–003 constraints continue; the 246-test baseline must stay
  green at every commit; no push.
- Zero new runtime dependencies (stdlib transport + parsing).
- Response bytes only ever in the payload store.
- Persist-before-next-pull; successful-attempt commit order
  payload → envelope → attempt → extraction.
- No cross-payload comparison anywhere in DS-004.
- Secrets only via injected CredentialResolver; every persisted string
  passes scrub/sanitize.
- Unverified HTTPS must not exist; plaintext HTTP per policy only.

## Tasks

### Task 1: Contracts + canonicalization
Tests then code: SourceTimeMarker union; AcquisitionAttempt (full tagged
sha256 fingerprint, target_origin, started/finished always +
received_at optional); ApiSourceLocator (optional source_content_type,
extraction_route); OperationalObservation (value_json/json_type);
ApiExtractionManifest + ApiObservationsResult union member;
ApiHealthEvidence + SourceHealth.api_evidence; IngestionRun attempt
counters; RunStatus literal + documented precedence helper; canonical
serializer (Decimal/int lexemes, sorted keys, spike test matrix:
1.0 vs "1.0", int vs non-int, exponents, nested arrays/objects, toolhead
position, replay determinism); RFC 6901 escape/unescape with hostile
names. Commit.

### Task 2: Store — attempts + integrity audit
Tests then code: write-once `attempts/` (put/get/iter by source);
`derive_keyed_record_id`; `find_uncommitted_api_artifacts` (API-keyed
envelopes with no committed successful attempt; payloads referenced by
neither) distinct from derivative orphans; existing audits unchanged.
Commit.

### Task 3: Network policy + transport + HttpApiConnector
Tests (transport stub + loopback) then code: address classification
(loopback/link-local/multicast/unspecified/ULA/private/public) and
policy enforcement; per-request re-resolution; pinned origin; redirect
refusal; no proxy inheritance; TLS verify-only; plaintext-explicit
policy; per-request timeout, sweep deadline, size + gzip caps; retries
with counts; CredentialResolver protocol + header injection;
`acquire_events` generator with planned-item count; LocalFileConnector
adapted to yield one event (ids and tests untouched). Commit.

### Task 4: Hardened parsing + Moonraker adapter + fixtures
Tests then code: bounded strict JSON (dup-key/NaN/UTF-8/depth/nodes/
string caps); adapter endpoint plan (corrected object selection, sorted
canonical query), envelope interpretation, requested-field-omitted
evidence, monotonic markers from /result/eventtime, server_info selected
properties, observation emission with value_json; frozen hand-authored
fixtures (success pair, byte-identical repeat, changed measurement,
malformed, dup-key, NaN, bad UTF-8, depth bomb, hostile names,
no-eventtime, drift, omitted-requested-fields) + FIXTURES.md + golden
expectations. Commit.

### Task 5: Runtime + health + e2e
Tests then code: incremental loop with commit order + failure injection
between every stage; keyed identity path; extraction-route dispatch;
status precedence tests for all four levels; attempt counters; health
`api_evidence` derivation; scripted transport scenarios (timeout, 401
leak test, 429, redirect); byte-identical reuse with distinct attempts;
replay after shutdown; loopback real-socket e2e; secret-leak scan over
all persisted artifacts. Commit.

### Task 6: Virtual Moonraker validation + Profile v2 + verification
Attempt digest-pinned virtual Klipper/Moonraker stack under the spec's
safety conditions; record exact versions or the missing-evidence
statement. Profile v2 (operational family enabled; roadmap_stage
`validated` only on real-software evidence, else `next`). README update;
full suite; dual clean-checkout; evidence report. Commit. No push.
