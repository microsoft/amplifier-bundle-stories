"""SCRATCH ONLY -- one deliberate ruff finding, to prove the LINT job can go RED."""

import os  # noqa-free on purpose: unused import, ruff F401


def undefined_name_here() -> str:
    return this_name_does_not_exist  # ruff F821
