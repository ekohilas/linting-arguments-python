"""Structural validation of the function def x call catalog.

Asserts STRUCTURE ONLY -- never a lint-rule verdict. The catalog is a
verdict-free corpus; a human decides per rule which cases should fire. So this
runner checks that every case is well-formed, uniquely identified, and parses
under the real toolchain (matching the `astroid.extract_node` convention in
`test/tests.py`). Inferability and plugin behaviour are *recorded, not asserted*.

Run:  uv run pytest test/test_catalog.py
"""

import astroid
import pytest

from catalog import all_cases
from catalog._schema import marked_source, validate, validity_of
from linting_arguments_python import my_plugin

CASES = all_cases()
IDS = [case.id for case in CASES]


def test_catalog_is_non_empty():
    assert CASES, "no cases collected from catalog modules"


def test_ids_are_globally_unique():
    seen = {}
    duplicates = []
    for case in CASES:
        if case.id in seen:
            duplicates.append(case.id)
        seen[case.id] = True
    assert not duplicates, f"duplicate case ids: {sorted(set(duplicates))}"


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_case_schema_is_valid(case):
    errors = validate(case)
    assert not errors, "; ".join(errors)


@pytest.mark.parametrize("case", CASES, ids=IDS)
def test_case_parses_and_marks_a_call(case):
    source = marked_source(case)
    validity = validity_of(case)

    if validity == "syntax_error":
        with pytest.raises(astroid.AstroidError):
            astroid.extract_node(source)
        return

    node = astroid.extract_node(source)
    # A stray list can come back if multiple `#@` markers slip in; we mark exactly one.
    assert not isinstance(node, list), f"{case.id}: expected a single marked node"
    assert isinstance(node, astroid.nodes.Call), (
        f"{case.id}: marked node is {type(node).__name__}, expected Call"
    )


def test_smoke_record_inferability_and_plugin(capsys):
    """Record (do NOT assert) inference + plugin behaviour for every runnable case.

    This surfaces regressions and mis-tagged inferability without baking verdicts
    into the corpus. Always passes. View with `pytest -s`.
    """
    report = []
    for case in CASES:
        if validity_of(case) == "syntax_error":
            continue
        try:
            node = astroid.extract_node(marked_source(case))
        except astroid.AstroidError as exc:
            report.append(f"{case.id}: PARSE-FAILED ({exc.__class__.__name__})")
            continue
        if not isinstance(node, astroid.nodes.Call):
            continue

        try:
            inferred = next(node.func.infer())
            inferred_kind = type(inferred).__name__
            if inferred is astroid.Uninferable:
                inferred_kind = "Uninferable"
        except astroid.InferenceError:
            inferred_kind = "InferenceError"

        try:
            plugin_result = my_plugin.check_call_arguments(function_call=node)
        except Exception as exc:  # plugin is intentionally incomplete; record only
            plugin_result = f"raised {exc.__class__.__name__}"

        report.append(
            f"{case.id}: inferred={inferred_kind} "
            f"tagged={case.tags.get('inferability')} plugin={plugin_result}"
        )

    print("\n--- catalog smoke report ---")
    print("\n".join(report))
