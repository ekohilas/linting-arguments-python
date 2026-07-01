"""Tests for :class:`ArgumentNameChecker`.

Each test states the code being linted inline and asserts either that it is
clean or that specific positional arguments are flagged.  Two helpers keep the
tests focused on *what* is being linted rather than the mechanics of driving
the checker:

* ``assertClean(source)`` -- the call raises no warning.
* ``assertFlags(source, (index, variable, parameter), ...)`` -- the call raises
  exactly one ``argument-name-mismatch`` warning per given tuple, where
  ``index`` is the position of the offending argument, ``variable`` is the name
  that was passed, and ``parameter`` is the parameter name it failed to match.

The call under test is always the node marked with ``#@``.
"""

import astroid
import pylint.testutils

from linting_arguments_python.argument_name_checker import ArgumentNameChecker


class TestArgumentNameChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = ArgumentNameChecker

    # ------------------------------------------------------------------ helpers

    def assertClean(self, source):
        """Assert that the marked call in `source` produces no warning."""
        call = astroid.extract_node(source)
        with self.assertNoMessages():
            self.checker.visit_call(call)

    def assertFlags(self, source, *expected):
        """Assert that the marked call flags exactly the given arguments.

        Each entry in `expected` is a ``(index, variable, parameter)`` tuple
        describing one expected ``argument-name-mismatch`` warning.
        """
        call = astroid.extract_node(source)
        messages = [
            pylint.testutils.MessageTest(
                msg_id="argument-name-mismatch",
                node=call.args[index],
                args=(variable, parameter),
            )
            for index, variable, parameter in expected
        ]
        with self.assertAddsMessages(*messages, ignore_position=True):
            self.checker.visit_call(call)

    # ---------------------------------------------------------- plain functions

    def test_matching_names_are_clean(self):
        self.assertClean(
            """
            def transfer(source, destination): ...

            transfer(source, destination) #@
            """
        )

    def test_single_mismatch_is_flagged(self):
        self.assertFlags(
            """
            def greet(name): ...

            greet(username) #@
            """,
            (0, "username", "name"),
        )

    def test_swapped_arguments_flag_both_positions(self):
        self.assertFlags(
            """
            def transfer(source, destination): ...

            transfer(destination, source) #@
            """,
            (0, "destination", "source"),
            (1, "source", "destination"),
        )

    def test_only_the_mismatching_argument_is_flagged(self):
        self.assertFlags(
            """
            def transfer(source, destination): ...

            transfer(source, target) #@
            """,
            (1, "target", "destination"),
        )

    # --------------------------------------------- non-variable positional args

    def test_literal_arguments_are_ignored(self):
        self.assertClean(
            """
            def configure(host, port): ...

            configure("localhost", 8080) #@
            """
        )

    def test_none_literal_is_ignored(self):
        self.assertClean(
            """
            def register(handler): ...

            register(None) #@
            """
        )

    def test_attribute_arguments_are_ignored(self):
        self.assertClean(
            """
            def transfer(source, destination): ...

            transfer(config.source, config.destination) #@
            """
        )

    def test_call_expression_arguments_are_ignored(self):
        self.assertClean(
            """
            def transfer(source, destination): ...

            transfer(open_source(), open_destination()) #@
            """
        )

    # ------------------------------------------------------- keyword arguments

    def test_keyword_arguments_are_never_flagged(self):
        self.assertClean(
            """
            def transfer(source, destination): ...

            transfer(source=origin, destination=target) #@
            """
        )

    def test_matching_positional_with_keyword_is_clean(self):
        self.assertClean(
            """
            def transfer(source, destination): ...

            transfer(source, destination=target) #@
            """
        )

    def test_positional_is_checked_even_when_keywords_follow(self):
        self.assertFlags(
            """
            def transfer(source, destination): ...

            transfer(origin, destination=target) #@
            """,
            (0, "origin", "source"),
        )

    # ---------------------------------------------------------- default values

    def test_omitted_default_parameter_is_clean(self):
        self.assertClean(
            """
            def connect(host, port=8080): ...

            connect(host) #@
            """
        )

    def test_mismatch_against_parameter_with_default(self):
        self.assertFlags(
            """
            def connect(host, port=8080): ...

            connect(server, port) #@
            """,
            (0, "server", "host"),
        )

    # ------------------------------------------------------- positional-only

    def test_positional_only_matching_is_clean(self):
        self.assertClean(
            """
            def transfer(source, /): ...

            transfer(source) #@
            """
        )

    def test_positional_only_mismatch_is_flagged(self):
        self.assertFlags(
            """
            def transfer(source, /): ...

            transfer(destination) #@
            """,
            (0, "destination", "source"),
        )

    # --------------------------------------------------------------- varargs

    def test_arguments_absorbed_by_star_args_are_ignored(self):
        self.assertClean(
            """
            def collect(first, *rest): ...

            collect(first, second, third) #@
            """
        )

    def test_named_parameter_before_star_args_is_still_checked(self):
        self.assertFlags(
            """
            def collect(first, *rest): ...

            collect(other, second, third) #@
            """,
            (0, "other", "first"),
        )

    def test_only_star_args_means_nothing_to_check(self):
        self.assertClean(
            """
            def collect(*items): ...

            collect(alpha, beta) #@
            """
        )

    def test_star_splat_stops_positional_matching(self):
        self.assertClean(
            """
            def transfer(source, destination): ...

            transfer(*pair) #@
            """
        )

    def test_argument_before_star_splat_is_still_checked(self):
        self.assertFlags(
            """
            def transfer(source, destination): ...

            transfer(origin, *rest) #@
            """,
            (0, "origin", "source"),
        )

    # ------------------------------------------------------- keyword-only args

    def test_keyword_only_parameter_passed_by_keyword_is_clean(self):
        self.assertClean(
            """
            def render(*, template): ...

            render(template=layout) #@
            """
        )

    # ---------------------------------------------------------------- methods

    def test_instance_method_matching_is_clean(self):
        self.assertClean(
            """
            class Mover:
                def transfer(self, source, destination): ...

            Mover().transfer(source, destination) #@
            """
        )

    def test_instance_method_swap_is_flagged(self):
        self.assertFlags(
            """
            class Mover:
                def transfer(self, source, destination): ...

            Mover().transfer(destination, source) #@
            """,
            (0, "destination", "source"),
            (1, "source", "destination"),
        )

    def test_classmethod_matching_is_clean(self):
        self.assertClean(
            """
            class Mover:
                @classmethod
                def transfer(cls, source, destination): ...

            Mover.transfer(source, destination) #@
            """
        )

    def test_classmethod_swap_is_flagged(self):
        self.assertFlags(
            """
            class Mover:
                @classmethod
                def transfer(cls, source, destination): ...

            Mover.transfer(destination, source) #@
            """,
            (0, "destination", "source"),
            (1, "source", "destination"),
        )

    def test_staticmethod_matching_is_clean(self):
        self.assertClean(
            """
            class Mover:
                @staticmethod
                def transfer(source, destination): ...

            Mover.transfer(source, destination) #@
            """
        )

    def test_staticmethod_mismatch_is_flagged(self):
        self.assertFlags(
            """
            class Mover:
                @staticmethod
                def transfer(source, destination): ...

            Mover.transfer(source, target) #@
            """,
            (1, "target", "destination"),
        )

    # ------------------------------------------------------------ constructors

    def test_constructor_matching_is_clean(self):
        self.assertClean(
            """
            class Point:
                def __init__(self, x, y): ...

            Point(x, y) #@
            """
        )

    def test_constructor_swap_is_flagged(self):
        self.assertFlags(
            """
            class Point:
                def __init__(self, x, y): ...

            Point(y, x) #@
            """,
            (0, "y", "x"),
            (1, "x", "y"),
        )

    def test_dataclass_constructor_swap_is_flagged(self):
        self.assertFlags(
            """
            import dataclasses

            @dataclasses.dataclass
            class Point:
                x: int
                y: int

            Point(y, x) #@
            """,
            (0, "y", "x"),
            (1, "x", "y"),
        )

    def test_class_without_init_has_nothing_to_check(self):
        self.assertClean(
            """
            class Marker: ...

            Marker(value) #@
            """
        )

    # ---------------------------------------------------------------- lambdas

    def test_lambda_matching_is_clean(self):
        self.assertClean(
            """
            transfer = lambda source, destination: None

            transfer(source, destination) #@
            """
        )

    def test_lambda_swap_is_flagged(self):
        self.assertFlags(
            """
            transfer = lambda source, destination: None

            transfer(destination, source) #@
            """,
            (0, "destination", "source"),
            (1, "source", "destination"),
        )

    # --------------------------------------------------- unresolvable callees

    def test_unknown_function_is_ignored(self):
        self.assertClean(
            """
            undefined_function(value) #@
            """
        )

    def test_builtin_without_argument_info_is_ignored(self):
        self.assertClean(
            """
            print(value) #@
            """
        )

    # ------------------------------------------------------- combined signature

    def test_full_signature_matching_is_clean(self):
        self.assertClean(
            """
            def function(first, /, second, *rest, keyword, **extra): ...

            function(first, second, third, keyword=named) #@
            """
        )

    def test_full_signature_mismatch_is_flagged(self):
        self.assertFlags(
            """
            def function(first, /, second, *rest, keyword, **extra): ...

            function(uno, second, third, keyword=named) #@
            """,
            (0, "uno", "first"),
        )
