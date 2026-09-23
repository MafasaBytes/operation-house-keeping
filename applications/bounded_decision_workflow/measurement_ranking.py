"""Slice 4: prior-free bounded minimax over a qualified matrix."""

from dataclasses import dataclass
import json


@dataclass(frozen=True, slots=True)
class MeasurementScore:
    measurement_id: str
    worst_survivors: int
    reduction: int
    survivor_multiset: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class MeasurementRanking:
    disposition: str
    best: tuple[str, ...] | None
    scores: tuple[MeasurementScore, ...]
    reason: str | None


class MeasurementRankingError(ValueError):
    def __init__(self, code, target):
        super().__init__(code)
        self.code = code
        self.target = target


def canonical_survivor_multiset(branches):
    """Canonicalize branches while preserving empty arrays and multiplicity."""
    arrays = [tuple(branch.get("survivors", ())) for branch in branches]
    return tuple(sorted(arrays))


def rank_measurements(hypothesis_ids, candidates):
    """Rank only a complete qualified nominated set using prior-free minimax.

    ``candidates`` is an application-owned, already qualified matrix.  Any
    incomplete/denied/conflicting/inapplicable candidate withholds the complete
    nominated set; it is never silently removed.
    """
    hypotheses = tuple(sorted(hypothesis_ids))
    if not hypotheses:
        return MeasurementRanking("withheld", None, (), "zero_hypotheses")
    if not candidates:
        return MeasurementRanking("withheld", None, (), "zero_measurements")
    ids = [candidate.get("id") for candidate in candidates]
    if len(set(ids)) != len(ids):
        raise MeasurementRankingError("DUPLICATE_MEASUREMENT_ID", "measurements")

    scores = []
    for candidate in sorted(candidates, key=lambda item: item["id"]):
        status = candidate.get("status", "complete")
        if status != "complete":
            return MeasurementRanking("withheld", None, (),
                                      "whole_nominated_set_withheld:" + str(status))
        branches = candidate.get("branches")
        if not isinstance(branches, list) or not branches:
            return MeasurementRanking("withheld", None, (), "missing_outcome_branches")
        for branch in branches:
            if branch.get("state", "qualified") != "qualified":
                return MeasurementRanking("withheld", None, (),
                                          "whole_nominated_set_withheld:" + str(branch.get("state")))
            survivors = branch.get("survivors", [])
            if any(item not in hypotheses for item in survivors):
                raise MeasurementRankingError("SURVIVOR_NOT_NOMINATED", candidate["id"])
        multiset = canonical_survivor_multiset(branches)
        worst = max((len(values) for values in multiset), default=0)
        scores.append(MeasurementScore(candidate["id"], worst,
                                       len(hypotheses) - worst, multiset))

    minimum = min(score.worst_survivors for score in scores)
    best = tuple(score.measurement_id for score in scores
                 if score.worst_survivors == minimum)
    return MeasurementRanking("ranked", best, tuple(scores), None)


def serialize_ranking(result):
    """Stable diagnostic serialization; no scores are inferred from costs."""
    return json.dumps({
        "disposition": result.disposition,
        "best": result.best,
        "reason": result.reason,
        "scores": [{"measurement_id": score.measurement_id,
                    "worst_survivors": score.worst_survivors,
                    "reduction": score.reduction,
                    "survivor_multiset": score.survivor_multiset}
                   for score in result.scores],
    }, sort_keys=True, separators=(",", ":"), default=list)
