import astroid
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

def transform_function_call(function_call: nodes.Call) -> None:
    # TODO: use update_call_arguments()
    ...

# TODO: register transform
# astroid.MANAGER.register_transform(astroid.Call, transform_function_call)

def update_call_arguments(function_call: nodes.Call) -> tuple[list[nodes.NodeNG], list[nodes.Keyword]]:
    """
    Returns what a function call's arguments and keyword arguments should be after
    updating arguments to use keywords instead.
    """
    current_arguments = function_call.args
    current_keywords = function_call.keywords
    # TODO
    updated_arguments = []
    updated_keywords = []
    return updated_arguments, updated_keywords


def check_call_arguments(function_call: nodes.Call) -> bool:
    """
    TODO
    """
    # TODO: add return type
    function_name = function_call.func
    function_definition = next(function_name.infer())
    return check_call_against_definition(function_call, function_definition)

def check_call_against_definition(
        function_call: nodes.Call,
        function_definition: nodes.FunctionDef,
) -> bool:
    """
    TODO
    """
    function_arguments_object = function_definition.args
    num_positional_parameters = len(function_arguments_object.posonlyargs)
    num_non_positional_parameters = len(function_arguments_object.args)

    call_args = function_call.args

    # skip the arguments that are positional, and only take the remaining possible arguments that can be named
    updateable_args = call_args[num_positional_parameters:num_positional_parameters + num_non_positional_parameters]

    has_unnamed_arguments = bool(updateable_args)
    return not has_unnamed_arguments



    # call_kwargs = function_call.keywords
    # non_positional_function_params =
    # def_pos_args
    # def_args
    # def_arguments
    """
    def function(pp, /, p, *l, kp, **kps): ...

    function(1, a2, 3, a4, kp=5, p3=6) #@
    """
    # return True