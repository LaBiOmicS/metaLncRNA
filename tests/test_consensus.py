from metalncrna.consensus import AMBIGUOUS, UNCLASSIFIED, vote
from metalncrna.tools import CODING, NONCODING, Call

C, N = Call(CODING), Call(NONCODING)


def test_majority():
    v = vote({"a": C, "b": C, "c": N})
    assert (v.label, v.coding, v.noncoding, v.voters) == (CODING, 2, 1, 3)
    assert v.agreement == 2 / 3


def test_noncoding_majority():
    assert vote({"a": N, "b": N, "c": C}).label == NONCODING


def test_tie_is_ambiguous():
    v = vote({"a": C, "b": N})
    assert v.label == AMBIGUOUS and v.agreement is None


def test_no_votes():
    assert vote({}).label == UNCLASSIFIED


def test_abstentions_do_not_count():
    # 6 of 7 tools voted: 4 noncoding vs 2 coding -> noncoding with 4/6 agreement.
    v = vote({"a": N, "b": N, "c": N, "d": N, "e": C, "f": C})
    assert v.label == NONCODING and v.voters == 6 and v.agreement == 4 / 6
