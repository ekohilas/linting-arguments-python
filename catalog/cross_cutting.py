"""Category: cross-cutting combinations (creative overflow).

Cases that combine axes or don't cleanly belong to one file: redundant keywords
(`f(x=x)`), parameters shadowing builtins (`def f(list): ...`), reserved-ish
parameter names (`type`, `id`, `input`), passing `self` explicitly
(`Class.method(instance, arg)`), pre-bound `functools.partial` positionals,
overload-dispatch ambiguity, keyword colliding with a `**kwargs` key, and the
argument-name-vs-parameter-name mismatch that motivates the talk's warning rule.
"""

from catalog._schema import Case

CATEGORY = "cross_cutting"

CASES = [
    # --- redundant keyword: f(x=x) --------------------------------------------
    Case(
        id="cross_cutting.redundant_keyword.matching_param",
        definition="def function(width): ...",
        call=(
            "width = 10\n"
            "function(width=width)"
        ),
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_var_match"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "The talk's central tension: `function(width=width)` names the param AND "
            "the value variable is identical to it. Maximal safety, maximal redundancy. "
            "A 'safety without the redundancy' rule might suggest dropping the keyword; "
            "an anti-mismatch rule sees a perfect match."
        ),
    ),
    Case(
        id="cross_cutting.redundant_keyword.no_matching_param",
        definition="def function(**keyword_parameters): ...",
        call=(
            "width = 10\n"
            "function(width=width)"
        ),
        tags={
            "definition_kind": ["var_keyword"],
            "param_count": "zero",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_var_match"],
            "unpacking": "none",
            "arity": "arity_absorbed_by_kwargs",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Same `f(x=x)` redundancy, but the key is NOT a declared parameter — it is "
            "absorbed by **kwargs. No param to match the variable name against, so the "
            "keyword is load-bearing (it becomes the dict key) and cannot be dropped."
        ),
    ),
    # --- parameter names shadowing builtins -----------------------------------
    Case(
        id="cross_cutting.shadow_builtin.list_param.call_keyword",
        definition="def function(list): ...",
        call="function(list=[1])",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Parameter name `list` shadows the builtin. A 'prefer keyword' rule would "
            "make the call site literally spell `list=...`, cementing the shadow at the "
            "call site. Interacts with any builtin-shadowing lint (e.g. W0622)."
        ),
    ),
    Case(
        id="cross_cutting.shadow_builtin.list_param.call_positional",
        definition="def function(list): ...",
        call="function([1])",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal_container"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Same builtin-shadowing param `list`, but called positionally. The shadow is "
            "invisible at the call site here — converting to keyword would surface it."
        ),
    ),
    # --- reserved-ish / dunder-ish param names --------------------------------
    Case(
        id="cross_cutting.reserved_ish_names.type_id_input.call_keyword",
        definition="def function(type, id, input): ...",
        call="function(type='a', id=1, input='x')",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "All three params shadow builtins (`type`, `id`, `input`). Common in real "
            "APIs (requests, dataclasses). Keyword form is idiomatic here despite the "
            "shadowing; the names are effectively reserved-by-convention."
        ),
    ),
    Case(
        id="cross_cutting.dunder_ish_name.class_.call_keyword",
        definition="def function(cls, self): ...",
        call="function(cls=object, self=None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "A plain module function whose params are named `cls` and `self` — the "
            "conventional method-receiver names, but on a free function. Passing them by "
            "keyword is legal yet reads oddly; a receiver-aware rule must not assume "
            "these are implicit."
        ),
    ),
    # --- passing self / cls explicitly ----------------------------------------
    Case(
        id="cross_cutting.explicit_self.unbound_class_access",
        definition=(
            "class Shape:\n"
            "    def method(self, arg):\n"
            "        ...\n"
            "instance = Shape()"
        ),
        call="Shape.method(instance, 5)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "arg_forms": ["pos_var_name_match", "pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "`self` passed EXPLICITLY via the class object. Signature-wise `self` is a "
            "real positional param here; a rule counting args must include the receiver. "
            "Contrast with the bound-call form below where `self` is implicit."
        ),
    ),
    Case(
        id="cross_cutting.explicit_self.bound_instance_access",
        definition=(
            "class Shape:\n"
            "    def method(self, arg):\n"
            "        ...\n"
            "instance = Shape()"
        ),
        call="instance.method(5)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_self_method",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Same method, bound call: `self` is supplied implicitly by the descriptor. "
            "The call passes ONE arg but the signature has TWO params. Any arity/keyword "
            "rule must offset the receiver — the mirror image of the explicit-self case."
        ),
    ),
    Case(
        id="cross_cutting.explicit_cls.classmethod_via_class",
        definition=(
            "class Shape:\n"
            "    @classmethod\n"
            "    def make(cls, arg):\n"
            "        ...\n"
        ),
        call="Shape.make.__func__(Shape, 5)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "classmethod",
            "arg_forms": ["pos_var_name_match", "pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Reaching through `.__func__` to call the classmethod's raw function with "
            "`cls` passed EXPLICITLY. Pathological but legal; defeats the descriptor's "
            "implicit-cls binding. Inference through `__func__` is only partial."
        ),
    ),
    # --- functools.partial: prebound positionals ------------------------------
    Case(
        id="cross_cutting.partial.prebound_positional.call_remaining",
        definition=(
            "import functools\n"
            "def function(first, second, third): ...\n"
            "bound = functools.partial(function, 1)"
        ),
        call="bound(2, 3)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "functools_partial",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "`partial` pre-binds `first`. The partial's effective signature is "
            "`(second, third)` even though the underlying def has three params. A rule "
            "walking the original signature will miscount unless it models partial."
        ),
    ),
    Case(
        id="cross_cutting.partial.prebound_keyword.override_at_call",
        definition=(
            "import functools\n"
            "def function(first, second, third): ...\n"
            "bound = functools.partial(function, second=2)"
        ),
        call="bound(1, third=3)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "functools_partial",
            "arg_forms": ["pos_literal", "kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_positional_then_keyword",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "`partial` pre-binds `second` as a keyword; the call supplies `first` "
            "positionally and `third` by keyword. `second` is already satisfied — a rule "
            "must not flag it as missing, and could still override it (partial keywords "
            "are overridable)."
        ),
    ),
    Case(
        id="cross_cutting.partial.prebound_positional.call_too_many",
        definition=(
            "import functools\n"
            "def function(first, second): ...\n"
            "bound = functools.partial(function, 1)"
        ),
        call="bound(2, 3)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "functools_partial",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_too_many_positional",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
            "validity": "runtime_error",
        },
        notes=(
            "Partial binds `first`; the two-param def now effectively takes one arg, but "
            "the call passes two -> TypeError at runtime. The overflow is only visible if "
            "the linter accounts for the pre-bound positional."
        ),
    ),
    # --- typing.overload dispatch ambiguity -----------------------------------
    Case(
        id="cross_cutting.overload.dispatch_ambiguous",
        definition=(
            "from typing import overload\n"
            "@overload\n"
            "def function(value: int) -> int: ...\n"
            "@overload\n"
            "def function(value: str) -> str: ...\n"
            "def function(value): return value"
        ),
        call="function(x)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": ["annotated_simple", "return_annotation"],
            "callable_kind": "typing_overload",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Two `@overload` signatures plus the implementation; the arg `x` is of "
            "unknown type, so which overload applies is ambiguous to a linter. The "
            "arg-form is a name mismatch against the param `value` under every overload. "
            "Runtime dispatches to the single impl regardless."
        ),
    ),
    Case(
        id="cross_cutting.overload.differing_param_names",
        definition=(
            "from typing import overload\n"
            "@overload\n"
            "def function(width: int) -> int: ...\n"
            "@overload\n"
            "def function(height: str) -> str: ...\n"
            "def function(value): return value"
        ),
        call="function(value=5)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": ["annotated_simple", "return_annotation"],
            "callable_kind": "typing_overload",
            "arg_forms": ["kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "The overloads disagree on the PARAMETER NAME (`width` vs `height`), while "
            "the implementation names it `value`. Calling `value=5` matches only the "
            "impl signature, not either overload. Which signature a keyword-name rule "
            "should trust is genuinely ambiguous."
        ),
    ),
    # --- keyword colliding with what would go into **kwargs -------------------
    Case(
        id="cross_cutting.kwargs_collision.explicit_and_kwargs",
        definition="def function(name, **kwargs): ...",
        call="function(name='a', flag=True)",
        tags={
            "definition_kind": ["pos_or_kw", "var_keyword"],
            "param_count": "boundary",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_absorbed_by_kwargs",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "`name` binds the declared param; `flag` — an arbitrary caller-chosen key — "
            "overflows into **kwargs. A name-match rule can check `name` but has NO "
            "declared param to match `flag` against; it is legitimately free-form."
        ),
    ),
    Case(
        id="cross_cutting.kwargs_collision.same_key_via_double_star",
        definition="def function(name, **kwargs): ...",
        call=(
            "extras = {'name': 'from_dict'}\n"
            "function(name='explicit', **extras)"
        ),
        tags={
            "definition_kind": ["pos_or_kw", "var_keyword"],
            "param_count": "boundary",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_literal"],
            "unpacking": "double_star_map",
            "arity": "arity_duplicate",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Explicit `name=` collides with a `name` key inside the `**extras` mapping -> "
            "TypeError 'got multiple values for keyword argument' at runtime IF the dict "
            "actually contains that key. Statically the dict is a known literal here, so "
            "the duplicate is in principle detectable; opaque dicts would hide it."
        ),
    ),
    # --- keyword-only passed positionally (runtime error) ---------------------
    Case(
        id="cross_cutting.kwonly_passed_positionally.runtime_error",
        definition="def function(*, keyword_only): ...",
        call="function(5)",
        tags={
            "definition_kind": ["bare_star", "kw_only"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_too_many_positional",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
            "validity": "runtime_error",
        },
        notes=(
            "A keyword-only param supplied positionally -> TypeError 'takes 0 positional "
            "arguments but 1 was given'. Parses fine; fails at call time. The inverse of "
            "the 'prefer keyword' rule's happy path."
        ),
    ),
    # --- positional-only passed by keyword ------------------------------------
    Case(
        id="cross_cutting.posonly_passed_by_keyword.runtime_error",
        definition="def function(position_only, /): ...",
        call="function(position_only=5)",
        tags={
            "definition_kind": ["posonly"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_unexpected_keyword",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
            "validity": "runtime_error",
        },
        notes=(
            "Positional-only param addressed by keyword -> TypeError 'got some positional-"
            "only arguments passed as keyword arguments'. A naive 'prefer keyword' rule "
            "that ignores the `/` would wrongly rewrite pos-only calls into this."
        ),
    ),
    Case(
        id="cross_cutting.posonly_by_keyword_absorbed_by_kwargs",
        definition="def function(position_only, /, **kwargs): ...",
        call="function(1, position_only=2)",
        tags={
            "definition_kind": ["posonly", "var_keyword"],
            "param_count": "boundary",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal", "kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_absorbed_by_kwargs",
            "ordering": "order_positional_then_keyword",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "The subtle exception: with `**kwargs` present, `position_only=2` does NOT "
            "error — it lands in kwargs as a string key while the positional `1` binds "
            "the pos-only param. So the same keyword form is a runtime error without "
            "kwargs but legal with them."
        ),
    ),
    # --- the talk's rectangle progression -------------------------------------
    Case(
        id="cross_cutting.rectangle.kwonly.reordered_keywords",
        definition="def rectangle(*, width, height): ...",
        call=(
            "width = 4\n"
            "height = 3\n"
            "rectangle(height=height, width=width)"
        ),
        tags={
            "definition_kind": ["bare_star", "kw_only"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw", "kw_value_var_match"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_kw_reordered",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "The talk's ideal end-state: `*` forces keyword-only, so `rectangle(height="
            "height, width=width)` is unambiguous even though the keywords are reordered "
            "relative to the signature. Every value var matches its key. Fully safe."
        ),
    ),
    Case(
        id="cross_cutting.rectangle.positional.value_mismatch",
        definition="def rectangle(width, height): ...",
        call=(
            "width = 4\n"
            "rectangle(width, width)"
        ),
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_var_name_match", "pos_var_name_mismatch"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "The bug the talk warns about: `rectangle(width, width)` — the second "
            "positional passes `width` into the `height` param. Positionally legal, "
            "silently wrong. First arg's var matches its param; second arg's var name "
            "(`width`) mismatches the param (`height`)."
        ),
    ),
    Case(
        id="cross_cutting.rectangle.positional.mixed_keyword_mismatch",
        definition="def rectangle(width, height): ...",
        call=(
            "width = 4\n"
            "rectangle(width, height=width)"
        ),
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": [
                "pos_var_name_match", "kw", "kw_value_var_mismatch",
            ],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_positional_then_keyword",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Mixed form: `width` positional (var matches param), then `height=width` — "
            "the keyword names `height` correctly but the VALUE variable is `width`. The "
            "keyword pins the binding (no swap bug), yet the value-name mismatch is "
            "exactly what a name-match rule flags."
        ),
    ),
    # --- deeply nested / expression arguments ---------------------------------
    Case(
        id="cross_cutting.nested_arg.deeply_nested_expr",
        definition="def function(value): ...",
        call=(
            "data = {'items': [[0, 1], [2, 3]]}\n"
            "function(data['items'][1][0] + len(str(data)))"
        ),
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_expr"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "A deeply nested subscript+call+arithmetic expression as the sole argument. "
            "There is no variable name to compare against the param — a name-match rule "
            "has nothing to latch onto, and a keyword-suggestion has no obvious key."
        ),
    ),
    Case(
        id="cross_cutting.nested_arg.walrus_in_argument",
        definition="def function(value): ...",
        call="function((n := 5))",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_expr"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Walrus assignment inside the argument: `function((n := 5))` both binds `n` "
            "and passes 5. The arg is an expression with a side effect; naive rewriting "
            "to `value=(n := 5)` preserves it, but the arg is not a plain name."
        ),
    ),
    Case(
        id="cross_cutting.nested_arg.bare_genexp_sole_arg",
        definition="def function(iterable): ...",
        call=(
            "y = [1, 2, 3]\n"
            "function(x for x in y)"
        ),
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_expr"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Bare generator expression as the SOLE argument — the one context where "
            "parentheses may be omitted (`function(x for x in y)`). If a rule rewrites "
            "this to `iterable=(x for x in y)` it must re-add the parens; and a genexp "
            "cannot be combined with any other argument."
        ),
    ),
    # --- multiple axes at once: imported classmethod + mismatched keywords ----
    Case(
        id="cross_cutting.imported_classmethod.mismatched_keyword_vars",
        definition=(
            "from decimal import Decimal\n"
            "w = '4'\n"
            "h = '3'"
        ),
        call="Decimal.from_float(value=w)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "classmethod",
            "arg_forms": ["kw", "kw_value_var_mismatch"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_imported",
            "source": "stdlib_not_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Multiple axes: an IMPORTED stdlib CLASSMETHOD (`Decimal.from_float`) called "
            "with a KEYWORD whose value variable (`w`) mismatches the param name "
            "(`value`). Signature comes from a non-editable C-adjacent source, so "
            "inference is only partial — a name-match rule can still see the keyword "
            "vs. value-var discrepancy. (Value type is wrong for from_float, but that's "
            "a type concern, not an arity one.)"
        ),
    ),
    Case(
        id="cross_cutting.dunder_call.instance_as_target",
        definition=(
            "class Multiplier:\n"
            "    def __call__(self, factor): ...\n"
            "double = Multiplier()"
        ),
        call="double(factor=2)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "dunder_call",
            "arg_forms": ["kw", "kw_value_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "The call target is an instance with `__call__`; the effective signature is "
            "`__call__` minus `self`. A rule must resolve `double(...)` to `__call__`'s "
            "params (`factor`), not treat `double` as an opaque callable."
        ),
    ),
]
