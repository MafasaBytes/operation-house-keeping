"""Approved S6 terminal-only failure envelope; never retains semantic output.

Caller success/retention limits are not changed. No exception text or cause chain
is serialized. Encoding and fallback do not call the workflow or filesystem.
"""
import json
import re

from applications.bounded_decision_workflow.errors import WorkflowDiagnostic
from applications.bounded_decision_workflow.input import BUILD_LIMITS

_FIELDS = ('bundle_state', 'code', 'exit_code', 'message_key', 'retry_class', 'stage', 'target')
_STAGES = frozenset(('usage', 'path_file_safety', 'wire_resource', 'lexical_schema',
    'commitment_public_reconstruction', 'profile_cardinality_edition',
    'semantic_calculation', 'output_resource', 'collision', 'retention_io', 'internal_failure'))
_STATES = frozenset(('absent', 'optional_refusal', 'incomplete',
    'complete_visible_durability_unknown', 'incomplete_or_absent', 'unknown'))
_FALLBACK = b'{"bundle_state":"unknown","code":"INTERNAL_ERROR","exit_code":7,"message_key":"internal_error","retry_class":"investigate","stage":"internal_failure","target":"application"}\n'


def _encode(diagnostic):
    if type(diagnostic) is not WorkflowDiagnostic:
        raise ValueError('diagnostic type')
    # len(str) is O(1): reject huge fields before encoding or regex matching.
    for name in _FIELDS:
        value = getattr(diagnostic, name)
        if name == 'exit_code':
            if type(value) is not int or value not in (2, 3, 4, 5, 6, 7):
                raise ValueError('diagnostic exit')
        elif type(value) is not str or not 0 < len(value) <= 512:
            raise ValueError('diagnostic field')
    if (re.fullmatch('[A-Z][A-Z0-9_]*', diagnostic.code) is None
            or diagnostic.message_key != diagnostic.code.lower()
            or diagnostic.stage not in _STAGES or diagnostic.bundle_state not in _STATES):
        raise ValueError('diagnostic tokens')

    # Leave room for LF; check BEFORE every append. json.dumps sees at most one
    # Unicode character, so its escaped temporary is at most eight bytes, not an
    # arbitrarily large field/chunk. No asdict/deepcopy of hostile field objects.
    cap = min(BUILD_LIMITS['output_stdout_stderr_bytes'] - 1,
              BUILD_LIMITS['output_diagnostic_bytes'])
    out = bytearray()

    def append(chunk):
        if len(out) + len(chunk) > cap:
            raise ValueError('diagnostic envelope')
        out.extend(chunk)

    def string(value):
        append(b'"')
        for character in value:
            append(json.dumps(character, ensure_ascii=False)[1:-1].encode('utf-8'))
        append(b'"')

    append(b'{')
    for i, name in enumerate(_FIELDS):
        if i: append(b',')
        string(name); append(b':')
        value = getattr(diagnostic, name)
        if name == 'exit_code': append(str(value).encode('ascii'))
        else: string(value)
    append(b'}')
    return bytes(out) + b'\n'


def diagnostic_line(diagnostic):
    """One bounded attempt, then a literal fallback (no recursive encoding)."""
    try:
        return _encode(diagnostic), diagnostic.exit_code
    except Exception:
        return _FALLBACK, 7


def emit_failure(diagnostic, stream):
    """At most one write and one flush. A broken sink cannot promise delivery."""
    wire, status = diagnostic_line(diagnostic)
    try:
        if stream.write(wire) != len(wire):
            return 7
        stream.flush()
    except Exception:
        return 7
    return status
