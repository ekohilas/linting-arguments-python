"""Category: call-target reference forms (call axis C5).

Varies how the callable is referenced at the call site: bare name, attribute
(`mod.f` / `obj.method`), `super().method()`, subscript result
(`handlers["k"]()`), call result (`factory()()`), alias/rebinding
(`g = f; g()`), imported name, class instantiation (`Class()`),
`self.method()`, and uninferable targets. Definition held to a canonical form.

This file isolates HOW THE CALLABLE IS REFERENCED, not the argument form: the
argument is kept canonical (a single positional literal or a single keyword)
throughout. The interesting axis is `call_target`, and — because the reference
form determines whether a deep-analysis rule can walk back to the signature —
`inferability` co-varies (recorded in tags + `notes`, never as a verdict).
"""

from catalog._schema import Case

CATEGORY = "call_target_forms"

CASES = [
    # --- target_bare_name --------------------------------------------------
    Case(
        id="call_target_forms.bare_name.module_function",
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
            "Baseline reference form: a bare module-level name resolves directly "
            "to its `def`, so the signature is fully inferable from the call site."
        ),
    ),
    Case(
        id="call_target_forms.bare_name.local_nested",
        definition=(
            "def outer():\n"
            "    def function(parameter): ...\n"
            "    return function(None)"
        ),
        call="outer()",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "nested_function",
            "arg_forms": [],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "The call under test is `outer()`; the nested `function(None)` shows a "
            "bare name resolving to a lexically-enclosed def. Inferable within scope, "
            "but note the marked Call is the outer bare name, not the inner one."
        ),
    ),
    # --- target_attribute --------------------------------------------------
    Case(
        id="call_target_forms.attribute.imported_module",
        definition="import mymodule",
        call="mymodule.function(None)",
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
            "call_target": "target_attribute",
            "source": "same_project_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Attribute access on an imported module (`module.func`). Astroid can "
            "usually resolve the module and the attribute if the module is on the "
            "path; recorded as partial because it depends on the module being "
            "importable/analysable at lint time."
        ),
    ),
    Case(
        id="call_target_forms.attribute.instance_method",
        definition=(
            "class Widget:\n"
            "    def method(self, parameter): ...\n"
            "obj = Widget()"
        ),
        call="obj.method(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Attribute access on an instance (`obj.method`). Astroid infers the type "
            "of `obj` and resolves the bound method; `self` is dropped, so the rule "
            "must offset the signature by one when matching the single argument."
        ),
    ),
    Case(
        id="call_target_forms.attribute.chained",
        definition=(
            "class Inner:\n"
            "    def method(self, parameter): ...\n"
            "class Outer:\n"
            "    def __init__(self):\n"
            "        self.inner = Inner()\n"
            "obj = Outer()"
        ),
        call="obj.inner.method(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Multi-hop attribute chain (`obj.inner.method`). Inference requires "
            "resolving each hop's type (Outer -> attribute inner -> Inner -> method); "
            "partial because attribute-assignment inference is more fragile than a "
            "direct instance attribute lookup."
        ),
    ),
    # --- target_super ------------------------------------------------------
    Case(
        id="call_target_forms.super.zero_arg",
        definition=(
            "class Base:\n"
            "    def method(self, parameter): ...\n"
            "class Derived(Base):\n"
            "    def method(self, parameter):\n"
            "        return super().method(parameter)"
        ),
        call="Derived().method(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "arg_forms": ["pos_var_name_match"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_super",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "`super().method(parameter)` inside `Derived.method`. The marked Call is "
            "the outer `Derived().method(None)` driver, but the case exercises the "
            "super-proxy form; astroid resolves super() to the MRO and finds "
            "Base.method's signature. The internal super call passes the parameter "
            "by matching name."
        ),
    ),
    Case(
        id="call_target_forms.super.explicit_args",
        definition=(
            "class Base:\n"
            "    def method(self, parameter): ...\n"
            "class Derived(Base):\n"
            "    def method(self, parameter):\n"
            "        return super(Derived, self).method(parameter)"
        ),
        call="super(Derived, self).method(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_super",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Two-argument `super(Derived, self)` form used as the call target. "
            "`self` is a free name at module scope in the marked snippet, so the "
            "receiver is not resolvable there; inference of the proxied Base.method "
            "signature is partial in isolation."
        ),
    ),
    # --- target_subscript_result -------------------------------------------
    Case(
        id="call_target_forms.subscript_result.dict_of_functions",
        definition=(
            "def function(parameter): ...\n"
            "handlers = {\"k\": function}"
        ),
        call="handlers[\"k\"](None)",
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
            "call_target": "target_subscript_result",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "The callable is the result of subscripting a dict literal of functions. "
            "Astroid can sometimes infer the value at a constant string key back to "
            "`function`, but subscript inference is best-effort; recorded partial."
        ),
    ),
    Case(
        id="call_target_forms.subscript_result.list_index",
        definition=(
            "def function(parameter): ...\n"
            "callbacks = [function]"
        ),
        call="callbacks[0](None)",
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
            "call_target": "target_subscript_result",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Callable obtained by integer-indexing a list literal. Like the dict "
            "case, astroid may infer the element back to `function`; partial because "
            "list-element inference degrades with any mutation of the list."
        ),
    ),
    Case(
        id="call_target_forms.subscript_result.opaque_key",
        definition=(
            "def function(parameter): ...\n"
            "handlers = {}\n"
            "handlers[compute_key()] = function"
        ),
        call="handlers[compute_key()](None)",
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
            "call_target": "target_subscript_result",
            "source": "same_module_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Subscript with a dynamic (call-result) key into a dict populated at "
            "runtime. `compute_key` is undefined and the key is non-constant, so the "
            "target callable cannot be resolved; arity is therefore unknown."
        ),
    ),
    # --- target_call_result ------------------------------------------------
    Case(
        id="call_target_forms.call_result.factory",
        definition=(
            "def function(parameter): ...\n"
            "def factory():\n"
            "    return function"
        ),
        call="factory()(None)",
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
            "call_target": "target_call_result",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "The callable is the return value of another call (`factory()(...)`). "
            "Astroid can infer the return of a simple factory that returns a known "
            "function, so the inner signature is sometimes recoverable; partial "
            "because it hinges on return-value inference."
        ),
    ),
    Case(
        id="call_target_forms.call_result.decorator_factory",
        definition=(
            "def make_multiplier():\n"
            "    def function(parameter): ...\n"
            "    return function"
        ),
        call="make_multiplier()(None)",
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
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Closure factory: the returned callable is a nested function defined "
            "inside the factory. Signature recoverable via return inference into the "
            "nested def; partial because closures over factory state can confound it."
        ),
    ),
    # --- target_alias ------------------------------------------------------
    Case(
        id="call_target_forms.alias.local_rebind",
        definition=(
            "def function(parameter): ...\n"
            "g = function"
        ),
        call="g(None)",
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
            "Simple rebinding `g = function; g(...)`. Astroid follows the assignment "
            "to the original def, so the signature is fully inferable through the "
            "alias."
        ),
    ),
    Case(
        id="call_target_forms.alias.import_as",
        definition="from mymodule import function as g",
        call="g(None)",
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
            "source": "same_project_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "`from mod import func as g; g(...)`. The alias is an import-time rename; "
            "astroid resolves the aliased name to the source def if the module is "
            "analysable. Partial because it depends on the import being resolvable."
        ),
    ),
    Case(
        id="call_target_forms.alias.conditional_rebind",
        definition=(
            "def function(parameter): ...\n"
            "def other(parameter): ...\n"
            "import random\n"
            "g = function if random.random() > 0.5 else other"
        ),
        call="g(None)",
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
            "inferability": "inferable_partial",
        },
        notes=(
            "Alias bound to one of two functions via a conditional expression. "
            "Astroid infers a union of both defs; since both share the same "
            "signature the arity is consistent, but the target is ambiguous — "
            "partial inference (multiple candidates)."
        ),
    ),
    # --- target_imported ---------------------------------------------------
    Case(
        id="call_target_forms.imported.stdlib_from_import",
        definition="from os.path import join",
        call="join(None)",
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
            "source": "stdlib_not_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Imported stdlib name used bare (`from os.path import join`). The def "
            "lives in another module; astroid resolves it via its stdlib "
            "definition/typeshed. arity_unknown because os.path.join's true "
            "signature is `join(a, *p)`, so a single positional is legal but overall "
            "arity depends on the variadic tail."
        ),
    ),
    Case(
        id="call_target_forms.imported.thirdparty_attribute",
        definition="import third_party_lib",
        call="third_party_lib.function(None)",
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
            "call_target": "target_imported",
            "source": "third_party_not_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Imported third-party name accessed as an attribute. Both a "
            "target_imported and target_attribute flavour; classified as imported "
            "because the source module is external and not editable. Inferability "
            "depends on the package being installed/analysable — partial."
        ),
    ),
    # --- target_class_instantiation ----------------------------------------
    Case(
        id="call_target_forms.class_instantiation.init",
        definition=(
            "class Widget:\n"
            "    def __init__(self, parameter): ..."
        ),
        call="Widget(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "class_constructor",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_class_instantiation",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Calling a class name instantiates it; the effective signature is that "
            "of `__init__` with `self` dropped. Fully inferable — astroid maps the "
            "class-name call to the __init__ params."
        ),
    ),
    Case(
        id="call_target_forms.class_instantiation.new",
        definition=(
            "class Widget:\n"
            "    def __new__(cls, parameter):\n"
            "        return super().__new__(cls)"
        ),
        call="Widget(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "class_constructor",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_class_instantiation",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "Instantiation where the effective signature comes from `__new__` (no "
            "`__init__`). A rule matching call args must pick __new__ here; astroid "
            "handles this less reliably than __init__, so partial."
        ),
    ),
    # --- target_self_method ------------------------------------------------
    Case(
        id="call_target_forms.self_method.instance",
        definition=(
            "class Widget:\n"
            "    def helper(self, parameter): ...\n"
            "    def run(self):\n"
            "        return self.helper(None)"
        ),
        call="Widget().run()",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "arg_forms": [],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_self_method",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "`self.helper(None)` inside a method body. The marked Call is the driver "
            "`Widget().run()`; the case exercises the self-method form. Astroid "
            "infers `self`'s class and resolves the sibling method — fully inferable."
        ),
    ),
    Case(
        id="call_target_forms.self_method.cls_classmethod",
        definition=(
            "class Widget:\n"
            "    @classmethod\n"
            "    def build(cls, parameter): ...\n"
            "    @classmethod\n"
            "    def run(cls):\n"
            "        return cls.build(None)"
        ),
        call="Widget.run()",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "classmethod",
            "arg_forms": [],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_self_method",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "`cls.build(None)` inside a classmethod — the classmethod analogue of "
            "the self-method form. `cls` binds to the class; `cls` is dropped from "
            "the effective signature like `self`. Marked Call is the `Widget.run()` "
            "driver."
        ),
    ),
    # --- target_uninferable ------------------------------------------------
    Case(
        id="call_target_forms.uninferable.getattr_dynamic",
        definition="obj = object()",
        call="getattr(obj, name)(None)",
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
            "call_target": "target_uninferable",
            "source": "dynamically_generated",
            "inferability": "uninferable",
        },
        notes=(
            "`getattr(obj, name)(...)` with a dynamic attribute name. The target is "
            "chosen at runtime and cannot be resolved statically; no signature is "
            "available, so any arg-shape rule must abstain. arity_unknown."
        ),
    ),
    Case(
        id="call_target_forms.uninferable.opaque_return",
        definition="import external_registry",
        call="external_registry.lookup()(None)",
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
            "call_target": "target_uninferable",
            "source": "dynamically_generated",
            "inferability": "uninferable",
        },
        notes=(
            "Callable is the return of an opaque external call "
            "(`external_registry.lookup()`). The returned object's type/signature is "
            "unknown, so the target is uninferable — a target_call_result whose "
            "inner callable cannot be recovered."
        ),
    ),
    Case(
        id="call_target_forms.uninferable.parameter_callback",
        definition=(
            "def run(callback):\n"
            "    return callback(None)"
        ),
        call="run(print)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "arg_forms": [],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_uninferable",
            "source": "same_module_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Inside `run`, `callback(None)` calls a parameter whose value is only "
            "known at the call site. From the definition alone the callee is "
            "uninferable; the marked Call `run(print)` shows a concrete binding, but "
            "the reference form under study (calling a bare parameter) is generically "
            "unresolvable."
        ),
    ),
]
