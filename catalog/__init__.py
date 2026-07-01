"""Catalog of Python function definition x call cases.

A verdict-free, tag-annotated enumeration of the ways a function can be defined
and called, used as the shared test-case corpus for the argument lint rules.
See ``catalog/README.md`` for the authoring contract.
"""

from importlib import import_module
from typing import List

from catalog._schema import Case, marked_source, validate, validity_of  # noqa: F401

# One module per independent category. Each exposes ``CASES: list[Case]``.
CATEGORY_MODULES = [
    "param_kinds",
    "defaults_and_annotations",
    "callable_kinds",
    "arg_forms",
    "unpacking",
    "arity_and_ordering",
    "call_target_forms",
    "source_and_inferability",
    "cross_cutting",
]


def all_cases() -> List[Case]:
    """Import every category module and return the concatenated list of cases."""
    cases: List[Case] = []
    for name in CATEGORY_MODULES:
        module = import_module(f"catalog.{name}")
        cases.extend(module.CASES)
    return cases
