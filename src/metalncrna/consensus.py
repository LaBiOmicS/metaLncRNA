"""Majority vote over the tools' own coding/noncoding verdicts.

* Only tools that actually reported on a sequence vote for it (abstentions do not count).
* More coding than noncoding votes -> coding; the reverse -> noncoding; a tie -> ambiguous.
* No votes at all -> unclassified.
"""

from __future__ import annotations

from dataclasses import dataclass

from .tools import CODING, NONCODING, Call

AMBIGUOUS = "ambiguous"
UNCLASSIFIED = "unclassified"


@dataclass(frozen=True)
class Verdict:
    label: str
    coding: int
    noncoding: int

    @property
    def voters(self) -> int:
        return self.coding + self.noncoding

    @property
    def agreement(self) -> float | None:
        """Fraction of voters that agree with the consensus (None if there is no majority)."""
        if self.label == CODING:
            return self.coding / self.voters
        if self.label == NONCODING:
            return self.noncoding / self.voters
        return None


def vote(calls: dict[str, Call]) -> Verdict:
    c = sum(1 for call in calls.values() if call.label == CODING)
    n = sum(1 for call in calls.values() if call.label == NONCODING)
    if c == n == 0:
        label = UNCLASSIFIED
    elif c > n:
        label = CODING
    elif n > c:
        label = NONCODING
    else:
        label = AMBIGUOUS
    return Verdict(label, c, n)
