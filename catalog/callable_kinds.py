"""Category: callable kinds & decoration (definition axes D5/D6).

Varies what *kind* of callable the definition is: module function, instance
method, classmethod, staticmethod, nested/closure, lambda, async def, generator,
property getter/setter, __call__ object, class constructor, dataclass __init__,
namedtuple, abstractmethod, functools.partial, functools.wraps-decorated,
typing.overload, signature-rewriting decorators. Also decoration variants.

Non-central axes (signature shape, arg forms, arity, ordering) are held to a
canonical minimal form -- a single positional-or-keyword parameter passed one
positional literal -- so this file isolates the *callable kind*.

Edge note on invocation-vs-call: properties and subscript/operator dunders are
triggered by attribute access / operators / subscription, none of which produce
an astroid ``Call`` node. Those cases invoke the underlying function object
directly (e.g. the setter function, or ``obj.__getitem__(k)``) so the last line
is a genuine ``Call``; the limitation is documented per-case in ``notes``.
"""

from catalog._schema import Case

CATEGORY = "callable_kinds"

CASES = [
    Case(
        id="callable_kinds.module_function",
        definition="def function(parameter):\n    return parameter",
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes="Baseline callable kind: a plain module-level function.",
    ),
    Case(
        id="callable_kinds.instance_method.via_instance",
        definition=(
            "class Class:\n"
            "    def method(self, parameter):\n"
            "        return parameter"
        ),
        call="Class().method(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Instance method called via an instance. `self` is bound implicitly, "
            "so the single explicit argument maps to `parameter`."
        ),
    ),
    Case(
        id="callable_kinds.instance_method.via_self",
        definition=(
            "class Class:\n"
            "    def method(self, parameter):\n"
            "        return parameter\n"
            "    def caller(self):\n"
            "        return self.method(None)"
        ),
        call="Class().caller()",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "instance_method",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_self_method",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Instance method invoked as `self.method(...)` from within another "
            "method. The last-line Call is `Class().caller()` (the outer trigger); "
            "the `self.method(None)` call it wraps is the target of interest -- a "
            "rule walking the body sees the self-bound call form."
        ),
    ),
    Case(
        id="callable_kinds.classmethod",
        definition=(
            "class Class:\n"
            "    @classmethod\n"
            "    def method(cls, parameter):\n"
            "        return parameter"
        ),
        call="Class.method(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "classmethod",
            "decoration": "decorator_transparent",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "@classmethod binds `cls` implicitly. Called on the class; the explicit "
            "argument maps to `parameter`. astroid models the descriptor transparently."
        ),
    ),
    Case(
        id="callable_kinds.staticmethod",
        definition=(
            "class Class:\n"
            "    @staticmethod\n"
            "    def method(parameter):\n"
            "        return parameter"
        ),
        call="Class.method(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "staticmethod",
            "decoration": "decorator_transparent",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "@staticmethod: no implicit first parameter, so the signature maps 1:1 "
            "with the call, unlike instance/class methods."
        ),
    ),
    Case(
        id="callable_kinds.nested_function",
        definition=(
            "def outer():\n"
            "    def inner(parameter):\n"
            "        return parameter\n"
            "    return inner(None)"
        ),
        call="outer()",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "nested_function",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Nested function (closure). The inner call `inner(None)` is the target; "
            "the last-line Call `outer()` is the enclosing trigger since the nested "
            "def is only reachable inside `outer`."
        ),
    ),
    Case(
        id="callable_kinds.closure_returned",
        definition=(
            "def make(captured):\n"
            "    def inner(parameter):\n"
            "        return captured + parameter\n"
            "    return inner"
        ),
        call="make(1)(2)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "nested_function",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_call_result",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Closure returned and immediately called: `make(1)(2)`. The outer Call "
            "result is the callable, so the target is a call-result, and the "
            "returned closure captures `captured`."
        ),
    ),
    Case(
        id="callable_kinds.lambda",
        definition="function = lambda parameter: parameter",
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "lambda",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Lambda bound to a name. Lambdas cannot have annotations and their "
            "params are always positional-or-keyword; still callable by keyword."
        ),
    ),
    Case(
        id="callable_kinds.async_def",
        definition=(
            "async def function(parameter):\n"
            "    return parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "async_def",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Async function. Calling it returns a coroutine (not awaited here); the "
            "argument-binding semantics are identical to a sync def for lint purposes."
        ),
    ),
    Case(
        id="callable_kinds.generator",
        definition=(
            "def function(parameter):\n"
            "    yield parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "generator",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Generator function (contains `yield`). Calling it builds a generator "
            "object; argument binding is ordinary, only the return semantics differ."
        ),
    ),
    Case(
        id="callable_kinds.async_generator",
        definition=(
            "async def function(parameter):\n"
            "    yield parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "async_generator",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Async generator (`async def` + `yield`). Returns an async-generator "
            "object; argument binding is ordinary."
        ),
    ),
    Case(
        id="callable_kinds.property_getter",
        definition=(
            "class Class:\n"
            "    @property\n"
            "    def value(self):\n"
            "        return None"
        ),
        call="Class().value.__get__(Class(), Class)",
        tags={
            "definition_kind": ["no_params"],
            "param_count": "zero",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "property_getter",
            "decoration": "decorator_transparent",
            "arg_forms": ["pos_expr"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "INVOCATION-VS-CALL LIMITATION: a property getter is triggered by "
            "attribute access (`obj.value`), which is an astroid `Attribute`, not a "
            "`Call`. To yield a real Call we invoke the descriptor's `__get__` "
            "directly. A rule targeting the *user-facing* getter would never see a "
            "Call at all -- documented here as the closest call form."
        ),
    ),
    Case(
        id="callable_kinds.property_setter",
        definition=(
            "class Class:\n"
            "    @property\n"
            "    def value(self):\n"
            "        return self._value\n"
            "    @value.setter\n"
            "    def value(self, parameter):\n"
            "        self._value = parameter"
        ),
        call="Class.value.fset(Class(), None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "property_setter",
            "decoration": "parametrized_decorator",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "INVOCATION-VS-CALL LIMITATION: a setter fires on assignment "
            "(`obj.value = x`), which is an `Assign`, never a `Call`. We call the "
            "underlying function via the property's `fset` slot to get a genuine "
            "Call. `@value.setter` is a decorator produced by another descriptor, "
            "tagged parametrized_decorator as the closest fit."
        ),
    ),
    Case(
        id="callable_kinds.property_deleter",
        definition=(
            "class Class:\n"
            "    @property\n"
            "    def value(self):\n"
            "        return self._value\n"
            "    @value.deleter\n"
            "    def value(self):\n"
            "        del self._value"
        ),
        call="Class.value.fdel(Class())",
        tags={
            "definition_kind": ["no_params"],
            "param_count": "zero",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "property_deleter",
            "decoration": "parametrized_decorator",
            "arg_forms": ["pos_expr"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "INVOCATION-VS-CALL LIMITATION: a deleter fires on `del obj.value`, a "
            "`Delete` node, never a `Call`. We invoke the underlying function via "
            "the property's `fdel` slot. Only `self` is bound, no other args."
        ),
    ),
    Case(
        id="callable_kinds.dunder_call",
        definition=(
            "class Class:\n"
            "    def __call__(self, parameter):\n"
            "        return parameter\n"
            "instance = Class()"
        ),
        call="instance(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "dunder_call",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Callable instance via `__call__`. Call site `instance(None)` looks like "
            "a plain function call, but resolution routes through the class's "
            "`__call__`; `self` is bound implicitly."
        ),
    ),
    Case(
        id="callable_kinds.class_constructor",
        definition=(
            "class Class:\n"
            "    def __init__(self, parameter):\n"
            "        self.parameter = parameter"
        ),
        call="Class(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "class_constructor",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_class_instantiation",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Class instantiation `Class(None)` dispatches to `__init__`; the call "
            "site's arguments bind to `__init__` params (minus `self`)."
        ),
    ),
    Case(
        id="callable_kinds.dataclass_init",
        definition=(
            "from dataclasses import dataclass\n"
            "@dataclass\n"
            "class Class:\n"
            "    parameter: int"
        ),
        call="Class(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "annotated_simple",
            "callable_kind": "dataclass_init",
            "decoration": "decorator_transparent",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_class_instantiation",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "@dataclass synthesizes `__init__` from annotated class attributes. The "
            "signature is generated, not written -- a rule must derive params from "
            "the field annotations. astroid has a dataclass brain for this."
        ),
    ),
    Case(
        id="callable_kinds.namedtuple_new",
        definition=(
            "from collections import namedtuple\n"
            "Class = namedtuple('Class', ['parameter'])"
        ),
        call="Class(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "namedtuple_new",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_class_instantiation",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "namedtuple factory. Construction dispatches to a synthesized `__new__` "
            "whose fields come from the string spec -- the signature is dynamically "
            "generated, so inferability is partial (astroid brain reconstructs it)."
        ),
    ),
    Case(
        id="callable_kinds.dunder_other",
        definition=(
            "class Class:\n"
            "    def __getitem__(self, key):\n"
            "        return key"
        ),
        call="Class().__getitem__(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "dunder_other",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "INVOCATION-VS-CALL LIMITATION: `__getitem__` is normally triggered by "
            "subscription (`obj[k]`), a `Subscript` node, not a `Call`. Invoking it "
            "explicitly as `obj.__getitem__(None)` produces a real Call. A rule "
            "wanting to catch subscript-driven dunders must handle Subscript "
            "separately -- it will not appear as a Call in idiomatic code."
        ),
    ),
    Case(
        id="callable_kinds.abstractmethod",
        definition=(
            "from abc import ABC, abstractmethod\n"
            "class Base(ABC):\n"
            "    @abstractmethod\n"
            "    def method(self, parameter):\n"
            "        ...\n"
            "class Concrete(Base):\n"
            "    def method(self, parameter):\n"
            "        return parameter"
        ),
        call="Concrete().method(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "abstractmethod",
            "decoration": "decorator_transparent",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_attribute",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "@abstractmethod declares a required signature on the ABC; the concrete "
            "override is what actually runs. A rule may want to check the call "
            "against the abstract declaration or the concrete impl (they match here)."
        ),
    ),
    Case(
        id="callable_kinds.functools_partial",
        definition=(
            "import functools\n"
            "def function(first, parameter):\n"
            "    return (first, parameter)\n"
            "partial_function = functools.partial(function, 0)"
        ),
        call="partial_function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "few",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "functools_partial",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_partial",
        },
        notes=(
            "functools.partial pre-binds `first=0`; the remaining call supplies "
            "`parameter`. The effective signature is shorter than the underlying "
            "function's -- a rule must account for the pre-bound argument. astroid "
            "has partial support but reconstruction is partial."
        ),
    ),
    Case(
        id="callable_kinds.functools_wraps_decorated",
        definition=(
            "import functools\n"
            "def decorator(wrapped):\n"
            "    @functools.wraps(wrapped)\n"
            "    def wrapper(parameter):\n"
            "        return wrapped(parameter)\n"
            "    return wrapper\n"
            "@decorator\n"
            "def function(parameter):\n"
            "    return parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "functools_wraps_decorated",
            "decoration": "decorator_transparent",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "@functools.wraps copies metadata (incl. __wrapped__) from the original "
            "onto the wrapper, so introspection can recover the true signature. Here "
            "the wrapper's signature happens to match, so it is transparent."
        ),
    ),
    Case(
        id="callable_kinds.typing_overload",
        definition=(
            "from typing import overload\n"
            "@overload\n"
            "def function(parameter: int) -> int: ...\n"
            "@overload\n"
            "def function(parameter: str) -> str: ...\n"
            "def function(parameter):\n"
            "    return parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "annotated_with_default",
            "callable_kind": "typing_overload",
            "decoration": "multiple_decorators",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "@typing.overload declares multiple type-only signatures; only the final "
            "undecorated implementation actually runs. A rule must pick which "
            "signature to check against -- overloads are for the type checker, not "
            "runtime dispatch. `annotated_with_default` is the closest annotation "
            "tag for the overload-annotated variants (no true default present)."
        ),
    ),
    Case(
        id="callable_kinds.signature_rewriting_decorator",
        definition=(
            "def decorator(wrapped):\n"
            "    def wrapper(*args, **kwargs):\n"
            "        return wrapped(*args, **kwargs)\n"
            "    return wrapper\n"
            "@decorator\n"
            "def function(parameter):\n"
            "    return parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "signature_rewriting_decorator",
            "decoration": "decorator_opaque",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Decorator replaces the function with a `(*args, **kwargs)` wrapper and "
            "does NOT use functools.wraps, so the true signature is hidden. Any "
            "arity/keyword rule sees only *args/**kwargs and cannot validate against "
            "`parameter` -- inferability uninferable, arity unknown."
        ),
    ),
    Case(
        id="callable_kinds.decoration.multiple",
        definition=(
            "def first(wrapped):\n"
            "    return wrapped\n"
            "def second(wrapped):\n"
            "    return wrapped\n"
            "@first\n"
            "@second\n"
            "def function(parameter):\n"
            "    return parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "decoration": "multiple_decorators",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Two stacked identity decorators, both transparent (return the function "
            "unchanged), so the signature survives. Isolates the multiple_decorators "
            "decoration axis while keeping the callable a plain module function."
        ),
    ),
    Case(
        id="callable_kinds.decoration.parametrized",
        definition=(
            "def decorator_factory(option):\n"
            "    def decorator(wrapped):\n"
            "        return wrapped\n"
            "    return decorator\n"
            "@decorator_factory(option=True)\n"
            "def function(parameter):\n"
            "    return parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "decoration": "parametrized_decorator",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "same_module_editable",
            "inferability": "inferable_full",
        },
        notes=(
            "Parametrized decorator (`@decorator_factory(option=True)`): the "
            "decorator expression is itself a call. This transparent factory returns "
            "the function unchanged, isolating the parametrized_decorator axis."
        ),
    ),
    Case(
        id="callable_kinds.decoration.opaque_uninferable",
        definition=(
            "import external_unresolvable_module\n"
            "@external_unresolvable_module.decorate\n"
            "def function(parameter):\n"
            "    return parameter"
        ),
        call="function(None)",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "module_function",
            "decoration": "decorator_opaque",
            "arg_forms": ["pos_literal"],
            "unpacking": "none",
            "arity": "arity_unknown",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "third_party_not_editable",
            "inferability": "uninferable",
        },
        notes=(
            "Decorator from an unresolvable third-party module: astroid cannot infer "
            "what it returns, so the post-decoration callable is opaque. A rule "
            "cannot know whether the signature was preserved -- uninferable / arity "
            "unknown."
        ),
    ),
    Case(
        id="callable_kinds.c_builtin",
        definition="",
        call="len([None])",
        tags={
            "definition_kind": ["pos_or_kw"],
            "param_count": "one",
            "defaults": "no_default",
            "annotations": "unannotated",
            "callable_kind": "c_builtin",
            "decoration": "undecorated",
            "arg_forms": ["pos_literal_container"],
            "unpacking": "none",
            "arity": "arity_exact",
            "ordering": "order_canonical",
            "call_target": "target_bare_name",
            "source": "c_builtin_no_signature",
            "inferability": "inferable_partial",
        },
        notes=(
            "C-implemented builtin (`len`) has no introspectable Python signature. "
            "astroid knows it exists but not its precise parameter spec, so "
            "inferability is partial and source is the no-signature builtin."
        ),
    ),
]
