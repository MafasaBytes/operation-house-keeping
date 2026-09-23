"""The historical vertical fixture was an unbound storage fixture, not proof.

Its exact original bytes remain in Git. The real carriage/replay tests live in
 test_delivery_contract_mapping.py; this negative control prevents reinstating
 the former caller-matrix path.
"""
import pytest
from applications.bounded_decision_workflow.measurement_delivery import evaluate_semantic_bundle


def test_unbound_caller_survivors_cannot_supply_computation(tmp_path):
    with pytest.raises(TypeError):
        evaluate_semantic_bundle(tmp_path/'out',b'{}',{},b'{}',b'{}',support_rows=[],candidates=[
            {'id':'T1','branches':[{'survivors':['H1']}]}])
