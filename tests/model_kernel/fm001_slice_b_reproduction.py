"""Deterministic, disposable FM-001 Slice B query witness."""

import argparse
import json

import backend.model_kernel as kernel
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.fl001_slice_a_helpers import AS_DESIGNED, FLOW_A, PORT_A
from tests.model_kernel.builders import VAR_A
from tests.model_kernel.test_flow_measurement_slice_a import (
    association, foundation, withdrawal,
)


def witness_bytes(*, reverse: bool = False) -> bytes:
    records, support = foundation()
    aligned = association(support, orientation="aligned", note="aligned active")
    inactive = association(support, orientation="aligned", note="aligned inactive")
    event = withdrawal(inactive)
    other = tuple(association(support, orientation=value, note=value)
                  for value in (
                      "opposite", "unsigned_magnitude", "not_applicable"))
    members = (*records, aligned, inactive, event, *other)
    if reverse:
        members = tuple(reversed(members))
    loaded = validate_record_collection(
        "test-model", {record.record_id: record for record in members})
    queries = kernel.ModelQueries(loaded)
    results = {
        "exact": tuple(
            queries.flow_measurement_association(
                FLOW_A, VAR_A, PORT_A, AS_DESIGNED, orientation).model_dump(
                    mode="json")
            for orientation in (
                "aligned", "opposite", "unsigned_magnitude",
                "not_applicable")),
        "flow": queries.flow_measurement_associations_for_flow(
            FLOW_A, context=AS_DESIGNED).model_dump(mode="json"),
        "variable": queries.flow_measurement_associations_for_variable(
            VAR_A, context=AS_DESIGNED).model_dump(mode="json"),
        "port": queries.flow_measurement_associations_at_port(
            PORT_A, context=AS_DESIGNED).model_dump(mode="json"),
        "assertions": tuple(
            queries.flow_measurement_assertion(record_id).model_dump(mode="json")
            for record_id in sorted((
                aligned.record_id, inactive.record_id, event.record_id,
                *(record.record_id for record in other)))),
    }
    return json.dumps(
        results, ensure_ascii=False, sort_keys=True,
        separators=(",", ":")).encode("utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reverse", action="store_true")
    args = parser.parse_args()
    print(witness_bytes(reverse=args.reverse).decode("utf-8"))


if __name__ == "__main__":
    main()
