"""Category: definition source & inferability (environment axes E1/E2/E3).

Varies where the callable comes from and whether astroid can infer its
definition: same-module (editable), same-project, standard library (not
editable), third-party (not editable), C builtins with no introspectable
signature (`len`, `print`), dynamically generated / uninferable, stub-only.
Also inferability (full/partial/uninferable) and multiplicity of inference.

This axis governs whether an auto-fix rule is even *allowed* to act (you cannot
edit stdlib), and mirrors the `next(func.infer())` boundary in
`my_plugin.check_call_arguments`.

Non-owned axes are held canonical: the call is a plain positional literal call
(`arg_forms: pos_literal`, `arity_exact`, `order_canonical`) unless the case is
specifically about a call target that changes inference. The signature, where we
own it, is a plain `def function(parameter): ...`.
"""

from catalog._schema import Case

CATEGORY = "source_and_inferability"

CASES = [
    # --- same_module_editable ---------------------------------------------
    Case(
        id="source_and_inferability.same_module.def_and_call",
        definition="def function(parameter): ...",
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Def and call in one snippet — the fully editable, fully inferable "
            "baseline. `next(func.infer())` yields the FunctionDef directly. An "
            "autofix rule may freely edit both the definition and the call site."
        ),
    ),
    Case(
        id="source_and_inferability.same_module.alias_binding",
        definition=(
            "def function(parameter): ...\n"
            "alias = function"
        ),
        call="alias(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_alias",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Same-module def rebound to another name, called through the alias. "
            "astroid follows the assignment so inference still resolves to the "
            "original FunctionDef; the callable remains editable."
        ),
    ),
    # --- multiplicity: name bound to >1 definition ------------------------
    Case(
        id="source_and_inferability.same_module.conditional_def_ambiguous",
        definition=(
            "import sys\n"
            "if sys.argv:\n"
            "    def function(parameter): ...\n"
            "else:\n"
            "    def function(other_parameter, extra): ...\n"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "MULTIPLICITY: the name `function` is bound to two distinct FunctionDefs "
            "in if/else branches with DIFFERENT signatures. `func.infer()` yields "
            "more than one candidate; `next(...)` takes only the first, so the plugin "
            "sees an arbitrary one of the two. A rule must handle ambiguous inference "
            "before autofixing. Tagged inferable_partial; arity_unknown reflects that "
            "the effective signature depends on which branch inference picks."
        ),
    ),
    Case(
        id="source_and_inferability.same_module.reassigned_after_def",
        definition=(
            "def function(parameter): ...\n"
            "function = lambda x, y: None\n"
        ),
        call="function(None, None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "lambda",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "MULTIPLICITY: the name is a def then rebound to a lambda with a different "
            "arity. Inference may yield both the FunctionDef and the Lambda; `next()` "
            "picks the first in flow order. Documents that a single name can carry "
            "several callable definitions in the same editable module."
        ),
    ),
    # --- same_project_editable --------------------------------------------
    Case(
        id="source_and_inferability.same_project.imported_helper",
        definition="from mypkg.util import helper",
        call="helper(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_imported",
            "source": "same_project_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Callable imported from a sibling module WE OWN (editable). Whether astroid "
            "resolves it depends on `mypkg` being on the path at lint time; in this "
            "isolated snippet `mypkg` does not exist so inference fails (Uninferable / "
            "raises). The editability boundary (we could add `*` to the def) is what "
            "matters here, independent of whether inference happens to succeed."
        ),
    ),
    Case(
        id="source_and_inferability.same_project.imported_module_attr",
        definition="from mypkg import util",
        call="util.helper(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_project_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Same-project callable reached via a module attribute (`util.helper`) rather "
            "than a direct import. Editable in principle; inference requires resolving "
            "`mypkg.util` from disk. Contrasts target_attribute against the direct "
            "target_imported case above."
        ),
    ),
    # --- stdlib_not_editable ----------------------------------------------
    Case(
        id="source_and_inferability.stdlib.json_dumps",
        definition="import json",
        call="json.dumps(obj, indent=2)",
        tags={
            "definition_kind": ["pos_or_kw", "kw_only"],
            "param_count": "few",
            "defaults": "default_immutable",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_var_name_mismatch", "kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_positional_then_keyword",
            "call_target": "target_attribute",
            "source": "stdlib_not_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Stdlib pure-Python function; astroid can typically infer `json.dumps` to a "
            "real FunctionDef with a full signature. But the source is NOT editable — an "
            "autofix rule must not attempt to add `*` to `json.dumps`; it may only rewrite "
            "the call site. `obj` is an undefined name (name-mismatch vs the `obj` param)."
        ),
    ),
    Case(
        id="source_and_inferability.stdlib.os_path_join",
        definition="import os",
        call="os.path.join(a, b)",
        tags={
            "definition_kind": ["pos_or_kw", "var_positional"],
            "param_count": "boundary",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_absorbed_by_varargs",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "stdlib_not_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Stdlib `os.path.join(a, b, *p)` reached through a nested module attribute. "
            "`os.path` is dynamically assigned (posixpath/ntpath) so inference is "
            "platform/brain-dependent — tagged inferable_partial. Non-editable; the "
            "trailing `*p` means later positionals have no keyword form."
        ),
    ),
    Case(
        id="source_and_inferability.stdlib.datetime_constructor",
        definition="import datetime",
        call="datetime.datetime(2020, 1, 1)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "default_immutable",
            "annotations": "unannotated",
            "callable_kind": "class_constructor",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "stdlib_not_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Instantiating a stdlib C-implemented class (`datetime.datetime`). Inference "
            "yields the ClassDef via astroid's brain, but the __init__/__new__ signature "
            "is C-level, so parameter binding is only partially recoverable. Not editable."
        ),
    ),
    Case(
        id="source_and_inferability.stdlib.from_import_function",
        definition="from functools import reduce",
        call="reduce(function, sequence)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_imported",
            "source": "stdlib_not_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Stdlib function brought into scope via `from ... import` and called by bare "
            "name (target_imported, not target_attribute). `functools.reduce` is "
            "pure-Python so astroid infers a full signature; still non-editable."
        ),
    ),
    # --- third_party_not_editable -----------------------------------------
    Case(
        id="source_and_inferability.third_party.requests_get",
        definition="import requests",
        call="requests.get(url)",
        tags={
            "definition_kind": ["pos_or_kw", "var_keyword"],
            "param_count": "boundary",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_absorbed_by_kwargs",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "third_party_not_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Third-party package. The snippet PARSES even though `requests` isn't "
            "installed in this environment — that is the point: inference cannot resolve "
            "an uninstalled/unavailable dependency, so `next(func.infer())` fails or "
            "returns Uninferable. Not editable regardless. `requests.get(url, **kwargs)`."
        ),
    ),
    Case(
        id="source_and_inferability.third_party.numpy_array",
        definition="import numpy",
        call="numpy.array([1, 2])",
        tags={
            "definition_kind": ["pos_or_kw", "kw_only"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "c_builtin",
            "arg_forms": ["pos_literal_container"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "third_party_not_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Third-party C-extension callable (`numpy.array`). Even when numpy IS "
            "installed its array constructor is a C function with no introspectable "
            "Python signature; here numpy is absent so inference simply fails. "
            "Non-editable; documents the C-extension flavour of third-party."
        ),
    ),
    Case(
        id="source_and_inferability.third_party.from_import_alias",
        definition="from pandas import DataFrame as DF",
        call="DF(data)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "class_constructor",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_alias",
            "source": "third_party_not_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Third-party class imported under an alias and instantiated. Combines the "
            "alias target form with an uninferable third-party source (pandas not "
            "installed). Documents `from x import Y as Z` binding for the source axis."
        ),
    ),
    # --- c_builtin_no_signature -------------------------------------------
    Case(
        id="source_and_inferability.c_builtin.len",
        definition="",
        call="len([1, 2])",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "c_builtin",
            "arg_forms": ["pos_literal_container"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "c_builtin_no_signature",
            "inferability": "inferable_partial",
        },
        notes=(
            "C builtin `len`. `definition` is empty (no import needed). astroid HAS a "
            "brain stub so `func.infer()` yields a node, but the underlying signature is "
            "C-level with no keyword-able params — you cannot write `len(obj=[...])`. "
            "inferable_partial: the object infers, the true parameter names do not. "
            "Non-editable; an 'add *' autofix must never target a builtin."
        ),
    ),
    Case(
        id="source_and_inferability.c_builtin.print",
        definition="",
        call='print("x")',
        tags={
            "definition_kind": ["var_positional", "kw_only"],
            "param_count": "boundary",
            "defaults": "default_immutable",
            "annotations": "unannotated",
            "callable_kind": "c_builtin",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_absorbed_by_varargs",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "c_builtin_no_signature",
            "inferability": "inferable_partial",
        },
        notes=(
            "`print(*values, sep=' ', end='\\n', ...)` — a C builtin whose real signature "
            "is variadic with keyword-only options. astroid brain provides a node but the "
            "positional `*values` have no individual parameter names. Not editable."
        ),
    ),
    Case(
        id="source_and_inferability.c_builtin.min_two_args",
        definition="",
        call="min(a, b)",
        tags={
            "definition_kind": ["var_positional", "kw_only"],
            "param_count": "boundary",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "c_builtin",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_absorbed_by_varargs",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "c_builtin_no_signature",
            "inferability": "inferable_partial",
        },
        notes=(
            "`min` is overloaded at the C level (min(iterable) vs min(a, b, *rest, key=...)). "
            "No introspectable Python signature; the two positionals cannot be named. "
            "Documents an overloaded builtin under the c_builtin source."
        ),
    ),
    Case(
        id="source_and_inferability.c_builtin.range",
        definition="",
        call="range(10)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "boundary",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "class_constructor",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_class_instantiation",
            "source": "c_builtin_no_signature",
            "inferability": "inferable_partial",
        },
        notes=(
            "`range` is a C builtin TYPE; calling it is a constructor. Its positional-only "
            "args (`range(stop)` / `range(start, stop, step)`) cannot be passed by keyword, "
            "so no 'prefer keyword' fix applies. Not editable."
        ),
    ),
    Case(
        id="source_and_inferability.c_builtin.sorted",
        definition="",
        call="sorted(seq)",
        tags={
            "definition_kind": ["pos_or_kw", "kw_only"],
            "param_count": "boundary",
            "defaults": "default_immutable",
            "annotations": "unannotated",
            "callable_kind": "c_builtin",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "c_builtin_no_signature",
            "inferability": "inferable_partial",
        },
        notes=(
            "`sorted(iterable, /, *, key=None, reverse=False)` — a C builtin with a "
            "positional-only first arg and keyword-only options. astroid brain infers a "
            "node; the iterable cannot be named. Non-editable."
        ),
    ),
    # --- dynamically_generated --------------------------------------------
    Case(
        id="source_and_inferability.dynamic.factory_result",
        definition=(
            "def make_fn():\n"
            "    def inner(x): ...\n"
            "    return inner\n"
            "f = make_fn()"
        ),
        call="f(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "nested_function",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_call_result",
            "source": "dynamically_generated",
            "inferability": "inferable_partial",
        },
        notes=(
            "Callable built at runtime by a factory (`f = make_fn()`). astroid CAN often "
            "follow the return value to the nested `inner` FunctionDef, so this is a case "
            "where a dynamically-produced callable is still partially inferable. The call "
            "target is the result of a call, not a name."
        ),
    ),
    Case(
        id="source_and_inferability.dynamic.getattr_result",
        definition="obj = object()",
        call='getattr(obj, "method")(None)',
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_uninferable",
            "source": "dynamically_generated",
            "inferability": "uninferable",
        },
        notes=(
            "Callable fetched via `getattr(obj, \"method\")` then invoked. The attribute "
            "name is a runtime string, so astroid cannot resolve which callable this is — "
            "`next(func.infer())` yields Uninferable. Canonical uninferable/dynamic case; "
            "no rule can safely act on the signature."
        ),
    ),
    Case(
        id="source_and_inferability.dynamic.type_created_class",
        definition='Dynamic = type("Dynamic", (), {})',
        call="Dynamic()",
        tags={
            "definition_kind": ["no_params"],
            "param_count": "zero",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "class_constructor",
            "arg_forms": [],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_class_instantiation",
            "source": "dynamically_generated",
            "inferability": "uninferable",
        },
        notes=(
            "Class synthesised at runtime with the 3-arg `type(...)`. There is no ClassDef "
            "node to inspect, so its __init__ signature is uninferable. Documents "
            "dynamically-generated *classes* (constructors), not just functions."
        ),
    ),
    Case(
        id="source_and_inferability.dynamic.decorator_replaces_callable",
        definition=(
            "def decorator(f):\n"
            "    def wrapper(*args, **kwargs): ...\n"
            "    return wrapper\n"
            "@decorator\n"
            "def function(parameter): ...\n"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["var_positional", "var_keyword"],
            "param_count": "zero",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "signature_rewriting_decorator",
            "decoration": "decorator_opaque",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_absorbed_by_varargs",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "dynamically_generated",
            "inferability": "inferable_partial",
        },
        notes=(
            "An opaque decorator that returns a NEW `(*args, **kwargs)` wrapper. The name "
            "`function` is defined in-module (editable) but its EFFECTIVE runtime signature "
            "is the wrapper's — dynamically generated. Inference of the decorated name may "
            "yield the wrapper rather than the original def, so a signature-based fix would "
            "act on the wrong signature. inferable_partial with the ambiguity noted."
        ),
    ),
    # --- stub_only ---------------------------------------------------------
    Case(
        id="source_and_inferability.stub_only.pyi_signature",
        definition="from _stubbed import stubbed_function",
        call="stubbed_function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "annotated_simple",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_imported",
            "source": "stub_only",
            "inferability": "inferable_partial",
        },
        notes=(
            "Callable whose signature exists ONLY in a `.pyi` stub (no editable runtime "
            "body). astroid can read the stub's parameter list, so the signature is "
            "known (inferable_partial — signature only, no body), but there is nothing to "
            "autofix: you cannot add `*` to a stub you don't own, and the .py has no def. "
            "This snippet cannot resolve `_stubbed` in isolation; the tag documents the "
            "stub-only editability boundary."
        ),
    ),
    Case(
        id="source_and_inferability.stub_only.c_ext_with_pyi",
        definition="import _speedups",
        call="_speedups.fast_call(a, b)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "annotated_simple",
            "callable_kind": "c_builtin",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "stub_only",
            "inferability": "inferable_partial",
        },
        notes=(
            "A C-extension module whose ONLY Python-visible signature is a shipped `.pyi` "
            "stub. The real implementation is compiled and non-editable; the stub gives "
            "parameter names but is also not something a lint autofix should rewrite. "
            "Contrasts stub-over-C-extension with the pure stub_only case above."
        ),
    ),
]
