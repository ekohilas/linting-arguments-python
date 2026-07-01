"""A pylint checker that enforces keyword-only function arguments via ``*``.

The checker flags any function definition that allows more leading positional
(non-keyword) arguments than a configurable threshold. With the default
threshold of ``0`` every argument must appear after a ``*`` marker, i.e. every
function must be keyword-only.
"""

from typing import TYPE_CHECKING, Union

from astroid import nodes
from pylint.checkers import BaseChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter

# Dunder methods the interpreter invokes with positional arguments (``a == b``
# calls ``a.__eq__(b)``, ``obj[k]`` calls ``obj.__getitem__(k)``, and so on).
# A ``*`` marker would break these, so they are exempt from the requirement.
_POSITIONAL_DUNDERS = frozenset(
    {
        # Rich comparisons.
        "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__",
        # Numeric operators (normal, reflected and in-place).
        "__add__", "__radd__", "__iadd__", "__sub__", "__rsub__", "__isub__",
        "__mul__", "__rmul__", "__imul__",
        "__matmul__", "__rmatmul__", "__imatmul__",
        "__truediv__", "__rtruediv__", "__itruediv__",
        "__floordiv__", "__rfloordiv__", "__ifloordiv__",
        "__mod__", "__rmod__", "__imod__", "__divmod__", "__rdivmod__",
        "__pow__", "__rpow__", "__ipow__",
        "__lshift__", "__rlshift__", "__ilshift__",
        "__rshift__", "__rrshift__", "__irshift__",
        "__and__", "__rand__", "__iand__", "__or__", "__ror__", "__ior__",
        "__xor__", "__rxor__", "__ixor__",
        # Container protocol.
        "__getitem__", "__setitem__", "__delitem__", "__contains__",
        # Descriptor protocol.
        "__get__", "__set__", "__delete__",
        # Attribute access.
        "__getattr__", "__getattribute__", "__setattr__", "__delattr__",
        # Class subscription (``Cls[int]`` -> ``Cls.__class_getitem__(int)``).
        "__class_getitem__",
    }
)

_DefNode = Union[nodes.FunctionDef, nodes.AsyncFunctionDef, nodes.Lambda]


class KeywordOnlyArgumentsChecker(BaseChecker):
    """Flag functions that do not enforce keyword-only arguments via ``*``."""

    name = "keyword-only-arguments"
    msgs = {
        "W9011": (
            "Function %r allows %d positional argument(s) but at most %d are "
            "permitted; add a '*' marker to enforce keyword-only arguments.",
            "missing-keyword-only-marker",
            "Functions should enforce keyword-only arguments using a '*' marker "
            "beyond the configured number of leading positional arguments.",
        ),
    }
    options = (
        (
            "max-positional-arguments",
            {
                "default": 0,
                "type": "int",
                "metavar": "<int>",
                "help": (
                    "Maximum number of leading positional arguments allowed "
                    "before a '*' keyword-only marker is required. 0 means every "
                    "argument must be keyword-only."
                ),
            },
        ),
        (
            "check-lambdas",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Also enforce the rule on lambda expressions.",
            },
        ),
    )

    @staticmethod
    def _implicit_first_arg_count(node: _DefNode) -> int:
        # 'self'/'cls' occupy args[0] for bound methods and classmethods and are
        # never keyword-passable, so they must not count as positional.
        return 1 if getattr(node, "type", "function") in ("method", "classmethod") else 0

    @staticmethod
    def _is_exempt(node: _DefNode) -> bool:
        if node.name in _POSITIONAL_DUNDERS:
            return True
        decorators = getattr(node, "decorators", None)
        if decorators is not None:
            for decorator in decorators.nodes:
                # ``@x.setter`` / ``@x.deleter`` receive their value positionally
                # (``obj.x = v`` -> ``fset(obj, v)``), so they cannot be keyword-only.
                if isinstance(decorator, nodes.Attribute) and decorator.attrname in (
                    "setter",
                    "deleter",
                ):
                    return True
        return False

    def _check(self, node: _DefNode) -> None:
        if self._is_exempt(node):
            return
        arguments = node.args
        num_positional = max(
            len(arguments.posonlyargs)
            + len(arguments.args)
            - self._implicit_first_arg_count(node),
            0,
        )
        allowed = self.linter.config.max_positional_arguments
        if num_positional > allowed:
            self.add_message(
                "missing-keyword-only-marker",
                node=node,
                args=(node.name, num_positional, allowed),
            )

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        self._check(node)

    # ``async def`` produces a distinct AsyncFunctionDef node that pylint
    # dispatches separately, so the same check is reused for it.
    visit_asyncfunctiondef = visit_functiondef

    def visit_lambda(self, node: nodes.Lambda) -> None:
        if self.linter.config.check_lambdas:
            self._check(node)


def register(linter: "PyLinter") -> None:
    """Auto-register the checker (pylint plugin entry point).

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(KeywordOnlyArgumentsChecker(linter))
