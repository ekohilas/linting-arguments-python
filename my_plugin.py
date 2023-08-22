from astroid import nodes
from typing import TYPE_CHECKING, Optional

from pylint.checkers import BaseChecker

if TYPE_CHECKING:
    from pylint.lint import PyLinter


class ArgumentChecker(BaseChecker):

    name = "unique-returns"
    msgs = {
        "W0001": (
            "Returns a non-unique constant.",
            "non-unique-returns",
            "All constants returned in a function should be unique.",
        ),
    }
    options = (
        (
            "ignore-ints",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y or n>",
                "help": "Allow returning non-unique integers",
            },
        ),
    )

    def __init__(self, linter: Optional["PyLinter"] = None) -> None:
        super().__init__(linter)
        self._function_stack = []

    def visit_functiondef(self, node: nodes.FunctionDef) -> None:
        self._function_stack.append([])

    def leave_functiondef(self, node: nodes.FunctionDef) -> None:
        self._function_stack.pop()

    def visit_return(self, node: nodes.Return) -> None:
        if not isinstance(node.value, nodes.Const):
            return
        for other_return in self._function_stack[-1]:
            if node.value.value == other_return.value.value and not (
                    self.linter.config.ignore_ints and node.value.pytype() == int
            ):
                self.add_message("non-unique-returns", node=node)

        self._function_stack[-1].append(node)

    def register(linter: "PyLinter") -> None:
        """This required method auto registers the checker during initialization.
        :param linter: The linter to register the checker to.
        """
        linter.register_checker(ArgumentChecker(linter))

def check_call_arguments(function_call: nodes.Call):
    function_name = function_call.func
    function_definition = next(function_name.infer())
    check_call_against_definition(function_call, function_definition)

def check_call_against_definition(
        function_call: nodes.Call,
        function_definition: nodes.FunctionDef,
):
    function_args = function_definition.args
    call_args = function_call.args
    call_kwargs = function_call.keywords
    # def_pos_args
    # def_args
    # def_arguments
    """
    def function(pp, /, p, *l, kp, **kps): ...

    print(1, a2, 3, a4, kp=5, p3=6)
    """

    ...