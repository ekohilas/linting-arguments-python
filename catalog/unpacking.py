"""Category: unpacking at the call site (call axis C2).

Varies iterable/mapping unpacking in the call: `f(*seq)`, `f(**mapping)`, mixed
`f(1, *rest, k=2, **more)`, and known-length/literal unpacking vs opaque
(uninferable) unpacking. Definition held to small canonical signatures.

The load-bearing distinction here is *inferability of the unpacked value*:

  - literal / known-length unpacking (`unpack_literal_known`) — a tuple/list
    literal or a fixed-arity helper whose element count astroid can resolve.
    An arg-name / prefer-keyword / positional->keyword rule can, in principle,
    map each unpacked element onto a concrete parameter and act.

  - opaque unpacking (`unpack_opaque`) — `*name`, `*get_seq()`, `**kwargs`,
    `**get_kwargs()` where the length/keys are NOT statically known
    (`inferability: inferable_partial`). Any autofix that renames args, converts
    positional->keyword, or checks arity MUST bail: it cannot know how many
    parameters the star consumes nor which keywords the double-star supplies, so
    rewriting risks changing call semantics. Arity is likewise `arity_unknown`.
"""

from catalog._schema import Case

CATEGORY = "unpacking"

CASES = [
    # --- star_seq: iterable unpacking ------------------------------------
    Case(
        id="unpacking.star_seq.tuple_var_known_len",
        definition="def function(a, b): ...",
        call="pair = (1, 2)\nfunction(*pair)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_expr"],
            "unpacking": ["star_seq", "unpack_literal_known"],
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "`*pair` where pair is a 2-tuple literal bound just above. astroid can "
            "infer length 2 -> maps onto (a, b). A positional->keyword rule could "
            "in principle expand this to function(a=1, b=2), but only because the "
            "length is statically known."
        ),
    ),
    Case(
        id="unpacking.star_seq.list_literal_known_len",
        definition="def function(a, b): ...",
        call="function(*[1, 2])",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal_container"],
            "unpacking": ["star_seq", "unpack_literal_known"],
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Inline list literal of known length 2. Same inferable situation as the "
            "tuple case; length is visible at the call site."
        ),
    ),
    Case(
        id="unpacking.star_seq.range_known_len",
        definition="def function(a, b, c): ...",
        call="function(*range(3))",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_call_result"],
            "unpacking": ["star_seq", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "`*range(3)` has a length obvious to a human (3) but astroid does not "
            "constant-fold range() into a known-length sequence, so element count is "
            "not statically resolved. Treated as opaque: arity_unknown; an autofix "
            "cannot safely map elements onto a/b/c."
        ),
    ),
    Case(
        id="unpacking.star_seq.opaque_call_result",
        definition="def function(a, b): ...",
        call="def get_seq():\n    return (1, 2)\nfunction(*get_seq())",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_call_result"],
            "unpacking": ["star_seq", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "`*get_seq()` — even though the helper returns a 2-tuple, a rule should "
            "treat the unpacked length as unknown (return values can vary, inference "
            "may be incomplete). Autofix must bail: renaming/keyword conversion "
            "cannot enumerate the elements safely."
        ),
    ),
    Case(
        id="unpacking.star_seq.opaque_name",
        definition="def function(a, b): ...",
        call="function(*rest)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": ["star_seq", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "`*rest` where rest is an undefined/free name — no binding to infer a "
            "length from. Fully opaque; arity_unknown. Canonical bail case for any "
            "arg-name or positional->keyword rule."
        ),
    ),
    # --- double_star_map: mapping unpacking ------------------------------
    Case(
        id="unpacking.double_star_map.dict_literal_known_keys",
        definition="def function(a, b): ...",
        call='function(**{"a": 1, "b": 2})',
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw_value_literal"],
            "unpacking": ["double_star_map", "unpack_literal_known"],
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Dict literal with statically-visible string keys 'a','b' matching the "
            "parameter names. A rule could in principle rewrite to function(a=1, b=2). "
            "Known keys are what make this actionable."
        ),
    ),
    Case(
        id="unpacking.double_star_map.dict_var_known_keys",
        definition="def function(a, b): ...",
        call='mapping = {"a": 1, "b": 2}\nfunction(**mapping)',
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw_value_literal"],
            "unpacking": ["double_star_map", "unpack_literal_known"],
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Dict literal bound to a name just above; keys still statically known via "
            "inference. Borderline: a conservative rule may already treat a named "
            "dict as opaque even though astroid can resolve it here."
        ),
    ),
    Case(
        id="unpacking.double_star_map.opaque_kwargs_name",
        definition="def function(a, b): ...",
        call="function(**kwargs)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw"],
            "unpacking": ["double_star_map", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "`**kwargs` — free name, keys unknown. The keyword set supplied is "
            "invisible, so arity and name-matching are undecidable. Autofix must bail: "
            "it cannot know whether 'a'/'b' are covered or which extra keys exist."
        ),
    ),
    Case(
        id="unpacking.double_star_map.opaque_call_result",
        definition="def function(a, b): ...",
        call='def get_kwargs():\n    return {"a": 1, "b": 2}\nfunction(**get_kwargs())',
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw_value_literal"],
            "unpacking": ["double_star_map", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "`**get_kwargs()` — keys produced dynamically by a call; not statically "
            "known. Opaque even though the helper body reveals them, since return "
            "values may vary. Autofix bails."
        ),
    ),
    # --- mixed_unpacking -------------------------------------------------
    Case(
        id="unpacking.mixed_unpacking.full_signature",
        definition="def function(a, /, b, *args, c, **kw): ...",
        call="rest = (2, 9)\nextra = {'d': 4}\nfunction(1, *rest, c=3, **extra)",
        tags={
            "definition_kind": [
                "posonly", "pos_or_kw", "var_positional", "kw_only", "var_keyword",
            ],
            "param_count": "many",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal", "pos_expr", "kw", "kw_value_literal"],
            "unpacking": ["mixed_unpacking", "star_seq", "double_star_map", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_positional_then_keyword",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Positional literal + `*rest` + keyword + `**extra` against a signature "
            "spanning every parameter kind. `*rest` feeds b then *args; `**extra` "
            "feeds **kw. Even with literal helpers the interaction of star + varargs "
            "makes the per-parameter mapping ambiguous; treat as opaque/arity_unknown. "
            "Any rewrite must bail."
        ),
    ),
    Case(
        id="unpacking.mixed_unpacking.opaque_both_stars",
        definition="def function(a, /, b, *args, c, **kw): ...",
        call="function(1, *rest, c=3, **extra)",
        tags={
            "definition_kind": [
                "posonly", "pos_or_kw", "var_positional", "kw_only", "var_keyword",
            ],
            "param_count": "many",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal", "pos_var_name_mismatch", "kw", "kw_value_literal"],
            "unpacking": ["mixed_unpacking", "star_seq", "double_star_map", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_positional_then_keyword",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Same signature but rest/extra are free names — doubly opaque. Neither the "
            "positional fill of b/*args nor the keyword fill of **kw is knowable. "
            "The canonical 'do nothing' case for arity + keyword rules."
        ),
    ),
    # --- star_seq into signatures with defaults --------------------------
    Case(
        id="unpacking.star_seq.into_defaults_known_len",
        definition="def function(a, b, c=0): ...",
        call="pair = (1, 2)\nfunction(*pair)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "default_immutable",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_expr"],
            "unpacking": ["star_seq", "unpack_literal_known"],
            "arity": "arity_defaults_omitted",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Known-length `*pair` (len 2) into a signature where c has a default. "
            "Fills a,b; c falls back to its default -> arity_defaults_omitted. Only "
            "decidable because the length is inferable."
        ),
    ),
    Case(
        id="unpacking.star_seq.into_defaults_opaque",
        definition="def function(a, b, c=0): ...",
        call="function(*args)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "default_immutable",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_var_name_mismatch"],
            "unpacking": ["star_seq", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Opaque `*args` into a defaulted signature. Cannot tell whether c is "
            "supplied or defaulted, nor whether arity is satisfied -> arity_unknown."
        ),
    ),
    # --- double_star into **kwargs sink ----------------------------------
    Case(
        id="unpacking.double_star_map.into_var_keyword_known",
        definition="def function(**keyword_parameters): ...",
        call='function(**{"x": 1, "y": 2})',
        tags={
            "definition_kind": ["var_keyword"],
            "param_count": "zero",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw_value_literal"],
            "unpacking": ["double_star_map", "unpack_literal_known"],
            "arity": "arity_absorbed_by_kwargs",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Known-key dict unpacked into a `**kwargs` sink. Keys are absorbed with no "
            "declared parameter to name-match against; a prefer-keyword rule has no "
            "concrete target params here even though keys are visible."
        ),
    ),
    Case(
        id="unpacking.double_star_map.into_var_keyword_opaque",
        definition="def function(**keyword_parameters): ...",
        call="function(**kwargs)",
        tags={
            "definition_kind": ["var_keyword"],
            "param_count": "zero",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["kw"],
            "unpacking": ["double_star_map", "unpack_opaque"],
            "arity": "arity_absorbed_by_kwargs",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Opaque `**kwargs` forwarded straight into a `**kwargs` sink — the classic "
            "wrapper/passthrough. Keys unknown but always legal (absorbed). No rule "
            "can or should act."
        ),
    ),
    # --- over/under-filling arity via unpacking --------------------------
    Case(
        id="unpacking.star_seq.overfill_known_len",
        definition="def function(a, b): ...",
        call="function(*[1, 2, 3])",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal_container"],
            "unpacking": ["star_seq", "unpack_literal_known"],
            "arity": "arity_too_many_positional",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
            "validity": "runtime_error",
        },
        notes=(
            "Known-length 3 unpacked into a 2-param signature — provably too many "
            "positionals; raises TypeError at runtime. Because length is inferable an "
            "arity rule CAN flag it. Contrast the opaque cases where it cannot."
        ),
    ),
    Case(
        id="unpacking.star_seq.underfill_known_len",
        definition="def function(a, b, c): ...",
        call="function(*(1,))",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal_container"],
            "unpacking": ["star_seq", "unpack_literal_known"],
            "arity": "arity_too_few",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
            "validity": "runtime_error",
        },
        notes=(
            "Known-length 1 unpacked into a 3-param signature — provably too few; "
            "missing b, c at runtime. Inferable length makes this decidable for an "
            "arity rule."
        ),
    ),
    Case(
        id="unpacking.star_seq.overfill_opaque_undecidable",
        definition="def function(a, b): ...",
        call="function(*get_seq())",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_call_result"],
            "unpacking": ["star_seq", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Might over- or under-fill (a,b) but the length is opaque -> arity_unknown. "
            "An arity rule must NOT emit too-few/too-many here; the mirror of the two "
            "known-length runtime_error cases above."
        ),
    ),
    Case(
        id="unpacking.double_star_map.duplicate_known_key",
        definition="def function(a, b): ...",
        call='function(1, **{"a": 2})',
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal", "kw_value_literal"],
            "unpacking": ["double_star_map", "unpack_literal_known"],
            "arity": "arity_duplicate",
            "ordering": "order_positional_then_keyword",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
            "validity": "runtime_error",
        },
        notes=(
            "Positional `1` fills a, then `**{'a': 2}` supplies key 'a' again -> "
            "'multiple values for argument a' TypeError. Detectable only because the "
            "unpacked key is a known literal. With opaque **kwargs this collision is "
            "invisible."
        ),
    ),
    Case(
        id="unpacking.double_star_map.duplicate_opaque_undecidable",
        definition="def function(a, b): ...",
        call="function(1, **kwargs)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": ["pos_literal", "kw"],
            "unpacking": ["double_star_map", "unpack_opaque"],
            "arity": "arity_unknown",
            "ordering": "order_positional_then_keyword",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Same shape as the duplicate case but with opaque `**kwargs`: a possible "
            "'multiple values for a' collision that cannot be proven. arity_unknown; "
            "an autofix/arity rule must bail."
        ),
    ),
]
