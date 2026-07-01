# Function definition × call catalog

A **verdict-free**, tag-annotated enumeration of every distinct way a Python
function can be **defined** and **called**. This is the shared test-case corpus
for the argument lint rules this project will grow (enforce `*` on defs; prefer
keyword args at call sites; warn when an argument's variable name ≠ the parameter
name; auto-fix positional → keyword).

Cases carry **dimension tags, not pass/fail verdicts**. A human reviews the
catalog and decides, per rule, which tag combinations should fire. This keeps one
corpus reusable across many rules.

## Layout

```
catalog/
  _schema.py                    # Case dataclass + controlled vocabulary + validate()
  __init__.py                   # all_cases() registry
  README.md                     # this file — the authoring contract
  param_kinds.py                # signature shapes & counts               (exemplar)
  defaults_and_annotations.py   # defaults (incl. mutable/sentinel) & annotations
  callable_kinds.py             # method/classmethod/static/lambda/async/property/ctor/partial/overload/decorated
  arg_forms.py                  # per-argument literal vs name-match/mismatch, attr/expr/subscript, kw value forms
  unpacking.py                  # *seq / **map / mixed / known vs opaque
  arity_and_ordering.py         # exact/too-few/too-many/duplicate/reorder/illegal-order
  call_target_forms.py          # bare/attr/super/subscript/alias/import/instantiation/self
  source_and_inferability.py    # stdlib/builtin/third-party/dynamic/uninferable/stub
  cross_cutting.py              # redundant kw, shadowing, reserved-ish names, prebound partial, overload dispatch
```

**One category file = one owner.** Files are disjoint and cases are appended, so
concurrent authors never collide.

## Authoring rules

1. Each module exposes `CASES: list[Case]`.
2. **ID prefix must equal the category** (e.g. `unpacking.*` only in `unpacking.py`).
   Namespacing keeps IDs globally unique without coordination.
3. Every case must carry at minimum `call_target`, `source`, `inferability`,
   plus the axes central to your category.
4. **Tags must come from the vocabulary** in `_schema.py`. Need a new value?
   Add it to `VOCABULARY` first (coordinate — the vocabulary is the shared contract).
5. **No verdicts.** Never encode "this should warn/pass". Put reasoning in `notes`.
6. **Hold non-owned axes at a canonical value** to minimise cross-file duplication —
   e.g. the arg-forms file keeps the signature to a plain `def function(parameter): ...`
   unless the case is specifically about signature interplay.
7. Write snippets at column 0 inside the strings (the runner also `dedent`s defensively).
   The **last line of `call`** is the call under test; the runner appends `#@`.
8. If a snippet is a deliberate **syntax error** (e.g. positional arg after keyword),
   tag `validity: syntax_error`. If it parses but would raise at runtime (bad arity),
   tag `validity: runtime_error`. Otherwise omit `validity` (defaults to `runnable`).

## Worked example

```python
from catalog._schema import Case

CASES = [
    Case(
        id="param_kinds.posonly.single.call_positional_literal",
        definition="def function(position_only_parameter, /): ...",
        call="function(None)",
        tags={
            "definition_kind": ["posonly"],
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
            "Positional-only param invoked positionally. A 'prefer keyword' rule "
            "likely should NOT fire — keyword form is illegal for pos-only params. "
            "Left for the human to decide per rule."
        ),
    ),
]
```

## Verification

```shell
uv run pytest test/test_catalog.py
```

The runner asserts **structure only, never rule verdicts**: schema validity,
globally unique IDs, that every snippet parses via `astroid.extract_node` and
yields a `Call` (or fails to parse for `syntax_error` cases). Inferability and
plugin behaviour are *recorded, not asserted* (see the smoke test), so the corpus
stays verdict-free while regressions still surface.
