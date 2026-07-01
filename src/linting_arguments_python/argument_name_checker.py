"""A pylint checker that flags positional arguments whose variable name does
not match the name of the parameter they are bound to.

The rule targets a common and hard-to-spot class of bug: passing local
variables positionally in the wrong order.  When every positional argument is
a plain variable reference, the variable's name is a strong signal of intent,
so a name that disagrees with the parameter it lands on usually means the
arguments were swapped (or that the call should spell the binding out with a
keyword argument).

    def transfer(source, destination): ...

    transfer(source, destination)       # ok:   names line up
    transfer(destination, source)       # flag: arguments look swapped
    transfer(destination=x, source=y)   # ok:   keywords are explicit

Only *positional* arguments that are simple variable references are examined.
Keyword arguments already state the binding explicitly, and literals, calls,
attributes and other expressions carry no variable name to compare against, so
they are left alone.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

import astroid
from astroid import bases, nodes

from pylint.checkers import BaseChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class ArgumentNameChecker(BaseChecker):
    """Flag positional arguments that disagree with their parameter name."""

    name = "argument-name-mismatch"
    msgs = {
        "W9101": (
            "Argument variable %r does not match parameter name %r.",
            "argument-name-mismatch",
            "A variable passed as a positional argument should share the name of "
            "the parameter it is bound to, or be passed as an explicit keyword "
            "argument.  A mismatch is a common sign that arguments were swapped.",
        ),
    }

    def visit_call(self, node: nodes.Call) -> None:
        parameter_names = self._positional_parameter_names(node)
        if not parameter_names:
            return

        for index, argument in enumerate(node.args):
            if isinstance(argument, nodes.Starred):
                # A ``*iterable`` splat consumes an unknown number of positions,
                # so nothing after it can be reliably mapped to a parameter.
                break
            if index >= len(parameter_names):
                # Extra positionals are absorbed by ``*args`` and have no fixed
                # parameter name to compare against.
                break
            if not isinstance(argument, nodes.Name):
                # Only plain variable references carry a name to check.
                continue

            parameter_name = parameter_names[index]
            if argument.name != parameter_name:
                self.add_message(
                    "argument-name-mismatch",
                    node=argument,
                    args=(argument.name, parameter_name),
                )

    def _positional_parameter_names(self, node: nodes.Call) -> Optional[List[str]]:
        """Return the ordered names of the parameters that ``node``'s positional
        arguments bind to, or ``None`` when the callee cannot be resolved.

        Implicit ``self``/``cls`` parameters are removed, so the returned names
        line up one-to-one with the caller's positional arguments.
        """
        try:
            callee = next(node.func.infer())
        except (astroid.InferenceError, StopIteration):
            return None

        if callee is astroid.Uninferable:
            return None

        if isinstance(callee, nodes.ClassDef):
            arguments, implicit = self._constructor_signature(callee)
        elif isinstance(callee, (nodes.Lambda, bases.BoundMethod, bases.UnboundMethod)):
            # ``nodes.FunctionDef`` is itself a ``nodes.Lambda`` subclass.
            arguments, implicit = callee.args, callee.implicit_parameters()
        else:
            return None

        if arguments is None:
            return None

        positional = (arguments.posonlyargs or []) + (arguments.args or [])
        return [parameter.name for parameter in positional][implicit:]

    @staticmethod
    def _constructor_signature(class_def: nodes.ClassDef):
        """Return the ``(arguments, implicit_count)`` of ``class_def.__init__``.

        A constructor always receives ``self`` implicitly at the call site, so
        one leading parameter is dropped regardless of how ``__init__`` reports
        its own binding.
        """
        try:
            init = next(class_def.igetattr("__init__"))
        except (astroid.InferenceError, StopIteration):
            return None, 0

        if not isinstance(init, (nodes.FunctionDef, bases.UnboundMethod, bases.BoundMethod)):
            return None, 0

        return init.args, 1


def register(linter: "PyLinter") -> None:
    """Auto-register the checker when this module is loaded as a pylint plugin.

    :param linter: The linter to register the checker to.
    """
    linter.register_checker(ArgumentNameChecker(linter))
