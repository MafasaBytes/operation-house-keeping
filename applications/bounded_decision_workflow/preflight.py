"""Bounded lexical scan before allocating a JSON object graph (S6).

This checks wire grammar/resources only, never public content or model semantics.
String tokens and object-key sets are bounded before decoding/retention.
"""
import json
import re

from applications.bounded_decision_workflow.errors import WorkflowDiagnostic, WorkflowInputError
from applications.bounded_decision_workflow.input import BUILD_LIMITS


def diagnostic(code, *, status=3):
    retry = "reduce_input" if status == 4 else "correct_input"
    return WorkflowInputError(WorkflowDiagnostic(code, "lexical_schema", "input_file",
                                                code.lower(), retry, status))


def scan(wire, limits=BUILD_LIMITS):
    """Count keys separately from nodes; root depth is one. No parsed graph."""
    try:
        text = wire.decode("utf-8")
    except UnicodeError as e:
        raise diagnostic("JSON_UTF8_INVALID") from e
    pos = nodes = keys = scalars = deepest = max_string = 0
    length = len(text)

    def space():
        nonlocal pos
        while pos < length and text[pos] in " \r\n\t": pos += 1

    def string():
        nonlocal pos, max_string
        start = pos
        pos += 1
        # A decoded UTF-8 byte can require at most six JSON escape bytes.
        while pos < length:
            if pos - start > 6 * limits["input_max_string_bytes"] + 1:
                raise diagnostic("JSON_STRING_LIMIT_EXCEEDED", status=4)
            c = text[pos]; pos += 1
            if c == '"':
                try: value = json.loads(text[start:pos])
                except ValueError as e: raise diagnostic("JSON_SYNTAX_INVALID") from e
                try: size = len(value.encode("utf-8"))
                except UnicodeError as e: raise diagnostic("JSON_UTF8_INVALID") from e
                max_string = max(max_string, size)
                if size > limits["input_max_string_bytes"]:
                    raise diagnostic("JSON_STRING_LIMIT_EXCEEDED", status=4)
                return value
            if c == "\\": pos += 1
        raise diagnostic("JSON_SYNTAX_INVALID")

    def value(depth):
        nonlocal pos, nodes, keys, scalars, deepest
        space(); nodes += 1; deepest = max(deepest, depth)
        if depth > limits["input_json_depth"]: raise diagnostic("JSON_DEPTH_LIMIT_EXCEEDED", status=4)
        if nodes > limits["input_json_nodes_per_file"]: raise diagnostic("JSON_NODE_LIMIT_EXCEEDED", status=4)
        if pos >= length: raise diagnostic("JSON_SYNTAX_INVALID")
        c = text[pos]
        if c == '"': string(); scalars += 1; return
        if c in "[{":
            pos += 1; space(); close = "}" if c == "{" else "]"
            seen = set()
            if pos < length and text[pos] == close: pos += 1; return
            while True:
                space()
                if c == "{":
                    if pos >= length or text[pos] != '"': raise diagnostic("JSON_SYNTAX_INVALID")
                    key = string(); keys += 1
                    if key in seen: raise diagnostic("JSON_DUPLICATE_KEY")
                    seen.add(key); space()
                    if pos >= length or text[pos] != ":": raise diagnostic("JSON_SYNTAX_INVALID")
                    pos += 1
                value(depth + 1); space()
                if pos < length and text[pos] == close: pos += 1; return
                if pos >= length or text[pos] != ",": raise diagnostic("JSON_SYNTAX_INVALID")
                pos += 1
        for literal in ("true", "false", "null"):
            if text.startswith(literal, pos): pos += len(literal); scalars += 1; return
        match = re.match(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?", text[pos:])
        if match is None: raise diagnostic("JSON_SYNTAX_INVALID")
        pos += len(match[0]); scalars += 1

    value(1); space()
    if pos != length: raise diagnostic("JSON_SYNTAX_INVALID")
    return {"nodes": nodes, "keys": keys, "scalars": scalars, "depth": deepest, "max_string_bytes": max_string}
