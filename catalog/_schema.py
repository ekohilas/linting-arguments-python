"""Shared schema and controlled vocabulary for the function def x call catalog.

The catalog is a *verdict-free* enumeration of the ways a Python function can be
DEFINED and CALLED. Each :class:`Case` pairs a ``definition`` snippet with a
``call`` snippet and tags it along orthogonal dimensions.

A human later decides, per prospective lint rule, which tag combinations should
raise a violation -- so cases carry NO pass/fail verdicts, only dimension tags
and free-text ``notes``. (A per-rule ``verdicts`` annotation may be layered on
later without changing this structure; see ``catalog/README.md``.)

Every category module (``param_kinds.py``, ``unpacking.py``, ...) exposes a
module-level ``CASES: list[Case]``. IDs are namespaced with the category name so
they stay globally unique with zero coordination between parallel authors.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass
from typing import List, Mapping, Sequence, Union

TagValue = Union[str, Sequence[str]]


@dataclass(frozen=True)
class Case:
    """One point in the definition x call space.

    Attributes:
        id: Globally unique, category-namespaced, e.g. ``"unpacking.star_seq.known_len"``.
        definition: Source that establishes the callable (``def``/``class``/``import``).
            May be ``""`` when the callable is a builtin used directly (e.g. ``len``).
        call: The call statement(s). May include helper lines (e.g. ``x = None``); the
            *last* line must be the call under test -- the runner marks it with ``#@``.
        tags: Mapping of axis -> value(s) drawn from :data:`VOCABULARY`. A value may be
            a single string or a sequence of strings (for combinable axes).
        notes: Reviewer-facing rationale / ambiguity. Never a verdict.
    """

    id: str
    definition: str
    call: str
    tags: Mapping[str, TagValue]
    notes: str = ""


# --- Controlled vocabulary -------------------------------------------------
# axis -> set of permitted values. Some axes are single-valued, some combinable
# (a Case may list several). `validate` accepts either a str or a sequence.

VOCABULARY: Mapping[str, frozenset] = {
    # --- Definition axes ---
    "definition_kind": frozenset({
        "posonly", "pos_or_kw", "var_positional", "bare_star",
        "kw_only", "var_keyword", "no_params",
    }),
    "param_count": frozenset({"zero", "one", "few", "many", "boundary"}),
    "defaults": frozenset({
        "no_default", "default_immutable", "default_mutable",
        "default_callable", "default_sentinel", "default_expr", "default_on_kwonly",
    }),
    "annotations": frozenset({
        "unannotated", "annotated_simple", "annotated_complex",
        "annotated_with_default", "return_annotation",
    }),
    "callable_kind": frozenset({
        "module_function", "instance_method", "classmethod", "staticmethod",
        "nested_function", "lambda", "async_def", "generator", "async_generator",
        "property_getter", "property_setter", "property_deleter",
        "dunder_call", "class_constructor", "dataclass_init", "namedtuple_new",
        "dunder_other", "abstractmethod", "functools_partial",
        "functools_wraps_decorated", "typing_overload",
        "signature_rewriting_decorator", "c_builtin",
    }),
    "decoration": frozenset({
        "undecorated", "decorator_transparent", "decorator_opaque",
        "multiple_decorators", "parametrized_decorator",
    }),
    # --- Call axes ---
    "arg_forms": frozenset({
        "pos_literal", "pos_var_name_match", "pos_var_name_mismatch",
        "pos_attribute", "pos_subscript", "pos_call_result", "pos_expr",
        "pos_literal_container", "kw", "kw_value_var_match",
        "kw_value_var_mismatch", "kw_value_literal", "kw_value_attr_matches_key",
    }),
    "unpacking": frozenset({
        "none", "star_seq", "double_star_map", "mixed_unpacking",
        "unpack_literal_known", "unpack_opaque",
    }),
    "arity": frozenset({
        "arity_exact", "arity_defaults_omitted", "arity_too_few",
        "arity_too_many_positional", "arity_unexpected_keyword",
        "arity_duplicate", "arity_absorbed_by_varargs",
        "arity_absorbed_by_kwargs", "arity_unknown",
    }),
    "ordering": frozenset({
        "order_canonical", "order_kw_reordered",
        "order_positional_then_keyword", "order_illegal_positional_after_keyword",
    }),
    "call_target": frozenset({
        "target_bare_name", "target_attribute", "target_super",
        "target_subscript_result", "target_call_result", "target_alias",
        "target_imported", "target_class_instantiation", "target_self_method",
        "target_uninferable",
    }),
    # --- Environment / source axes ---
    "source": frozenset({
        "same_module_editable", "same_project_editable", "stdlib_not_editable",
        "third_party_not_editable", "c_builtin_no_signature",
        "dynamically_generated", "stub_only",
    }),
    "inferability": frozenset({
        "inferable_full", "inferable_partial", "uninferable",
    }),
    # --- Optional: whether the snippet is expected to parse / run ---
    # Absent => treated as "runnable". "syntax_error" cases are expected to
    # FAIL to parse (e.g. positional arg after keyword); "runtime_error" cases
    # parse fine but would raise TypeError when actually executed.
    "validity": frozenset({"runnable", "runtime_error", "syntax_error"}),
}

# Axes every case must carry -- the ones most rules branch on.
REQUIRED_AXES = frozenset({"call_target", "source", "inferability"})


def validate(case: Case) -> List[str]:
    """Return a list of human-readable problems with ``case`` (empty == valid)."""
    errors: List[str] = []
    if not isinstance(case.id, str) or not case.id:
        errors.append("id must be a non-empty string")
    if not isinstance(case.definition, str):
        errors.append(f"{case.id}: definition must be a string")
    if not isinstance(case.call, str) or not case.call.strip():
        errors.append(f"{case.id}: call must be a non-empty string")
    if not isinstance(case.tags, Mapping):
        errors.append(f"{case.id}: tags must be a mapping")
        return errors

    for axis, value in case.tags.items():
        if axis not in VOCABULARY:
            errors.append(f"{case.id}: unknown axis {axis!r}")
            continue
        allowed = VOCABULARY[axis]
        values = [value] if isinstance(value, str) else list(value)
        for v in values:
            if v not in allowed:
                errors.append(f"{case.id}: {axis}={v!r} not in vocabulary")

    for axis in REQUIRED_AXES:
        if axis not in case.tags:
            errors.append(f"{case.id}: missing required axis {axis!r}")

    return errors


def validity_of(case: Case) -> str:
    """Return the ``validity`` tag, defaulting to ``"runnable"``."""
    return str(case.tags.get("validity", "runnable"))


def marked_source(case: Case) -> str:
    """Build the full snippet with astroid's ``#@`` marker on the call line.

    Mirrors the existing ``astroid.extract_node`` convention used in
    ``test/tests.py``: definition + call, with the final (call) line marked so
    ``extract_node`` returns the ``Call`` node.
    """
    parts = []
    definition = textwrap.dedent(case.definition).strip("\n")
    if definition.strip():
        parts.append(definition)
    call = textwrap.dedent(case.call).strip("\n")
    parts.append(call)
    source = "\n".join(parts)
    lines = source.split("\n")
    lines[-1] = lines[-1] + "  #@"
    return "\n".join(lines)
