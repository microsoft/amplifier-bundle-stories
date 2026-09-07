"""SCRATCH ONLY -- one deliberately failing test, to prove this CI can go RED.

This file exists on the scratch branch ci/red-proof-j1e6 and nowhere else. Its
whole job is to make the TEST job fail for a genuine TEST reason, so the job
log reads "N passed, 1 failed" rather than a setup or lint error -- a red run
that fails in setup proves nothing about the suite.

Delete with the branch.
"""

from __future__ import annotations


def test_deliberately_failing_so_the_test_job_goes_red() -> None:
    assert 1 == 2, "deliberate failure: proving the CI test job can go red"
