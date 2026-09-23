"""
The judge: decides whether one answer counts as correct.

`run_eval.py` finds this file automatically and uses `judge` to fill the Run
columns in the run log. Deciding what "correct" means is the point, so the rule
here is the one already written down at the top of `questions.py`, before any
results existed:

    an answer counts as correct if it contains the `expects` string, compared
    in lowercase.

It is deliberately literal. An answer that names the right fact in different
words will be marked fail, and that is the rule working as written rather than
a bug — if it turns out I cannot measure what I meant to measure, that is a
finding for Milestone 2, not a reason to quietly loosen the rule mid-unit.

`retrieval_contains` is the same test applied to the retrieved chunks instead
of the answer. Criterion 1 is about what retrieval brought back, not about what
the model wrote with it, so the two need measuring separately.
"""

from store import Result


def judge(question: str, expects: str, answer: str, results: list[Result]) -> bool:
    """True when the answer contains the expected string, ignoring case."""
    if not expects:
        return False
    return expects.lower() in (answer or "").lower()


def retrieval_contains(expects: str, results: list[Result]) -> bool:
    """True when any retrieved chunk contains the expected string.

    This is criterion 1: 'the retrieved chunks include one that contains the
    answer'. It can pass while `judge` fails — that combination means the
    chunks were there and generation did not use them, which is the split
    Milestone 3 asks me to diagnose.
    """
    if not expects:
        return False
    needle = expects.lower()
    return any(needle in r.text.lower() for r in results)
