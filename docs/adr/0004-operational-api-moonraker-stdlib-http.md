# ADR-0004: Moonraker showcase over vendor-neutral API contracts, stdlib HTTP transport, no worker isolation

Date: 2026-08-07
Status: Accepted (project owner; two amendment rounds incorporated)

## Context

DS-004 needs one real operational source with current-state measurements,
bounded read-only snapshot acquisition, deterministic offline testing, and
zero clean-checkout burden — feeding the future temporal/state layer
without anticipating it.

## Target decision

**Moonraker (Klipper)** as the product-specific adapter
(`adapter_id="moonraker"`, route `api:moonraker:v1`) over fully
vendor-neutral acquisition/observation contracts.

Evaluated against Home Assistant (runner-up: friendlier timestamps/units,
but a smart-home aggregator rather than one engineered system), Prometheus
(monitoring metrics, weak equipment semantics), MQTT/OPC UA (stream-only —
violates bounded-snapshot-first), and public cloud APIs (external network,
non-deterministic). Moonraker is one coherent engineered system —
subsystems (`extruder`, `heater_bed`, `toolhead`) with commanded-vs-
measured values — and its awkward truths (host-monotonic `eventtime`,
undeclared units) exercise the honesty machinery instead of flattering
it. Moonraker's GPL-3 license is irrelevant at this boundary: we speak
HTTP only; fixtures are hand-authored from public documentation.

## Transport decision

Python stdlib (`urllib.request` + `ssl` + `socket.getaddrinfo`
screening), injectable transport for tests. Zero new dependencies →
availability rung honestly trivial, clean checkout unchanged. The Task 0
spike proved redirect refusal, proxy-environment isolation via an
explicit handler list, fail-closed certificate verification, streamed
gzip expansion capping, and deadline enforcement — all on stdlib.

**Accepted limitation (owner decision):** a DNS-rebinding window remains
between pre-connect address validation and the stdlib connection by
hostname. Mitigations: per-request re-resolution and full address-set
policy validation, pinned scheme/host/port, refused redirects, disabled
proxies, no response-derived URLs. IP-pinned connections are not built in
DS-004 unless a practical bypass emerges.

## Isolation decision

No worker subprocess: extraction is hardened stdlib JSON (size, depth,
node, string caps; duplicate-key and NaN rejection; strict UTF-8) on
already-bounded bytes — no native parser attack surface. Conditional on
the Task 0 parser/transport checks, which passed 15/15.

## Security posture (fixed by amendment)

HTTPS always verified; unverified HTTPS unsupported. Plaintext HTTP only
by explicit configuration to loopback/approved private-LAN targets,
stamped in evidence. Credentials via an injected `CredentialResolver`;
resolved values live only in memory during request construction. No
documented Moonraker client quota identified; 429/`Retry-After` handled
conservatively.

## Consequences

- Occurrence evidence (`AcquisitionAttempt`) is first-class and separate
  from content-addressed payloads; the temporal layer joins them by
  `raw_record_id`.
- Vendor-aware extraction routes prevent generic-JSON overreach; a second
  adapter (e.g. Home Assistant) would prove contract neutrality.
- `validated` for the Moonraker target requires real Moonraker software
  (virtual Klipper stack acceptable, digest-pinned, unprivileged,
  loopback-only); the deterministic fake server remains the test oracle
  but never grants `validated`.
