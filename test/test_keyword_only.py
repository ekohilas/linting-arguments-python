"""Tests for the keyword-only arguments checker.

The tests are grouped into one class per configuration so that each class reads
as a focused specification of how the checker behaves under that setting. Nodes
are extracted with :func:`astroid.extract_node` using the ``#@`` marker, and
messages are asserted with pylint's ``CheckerTestCase`` helpers.
"""

import astroid
import pylint.testutils

from linting_arguments_python import keyword_only_checker


def _expected_message(node, *, name, positional, allowed):
    """Build the message a violating definition should produce."""
    return pylint.testutils.MessageTest(
        msg_id="missing-keyword-only-marker",
        node=node,
        args=(name, positional, allowed),
    )


class TestDefaultAllKeywordOnly(pylint.testutils.CheckerTestCase):
    """With the default threshold of 0, every argument must be keyword-only."""

    CHECKER_CLASS = keyword_only_checker.KeywordOnlyArgumentsChecker
    CONFIG = {"max_positional_arguments": 0}

    # --- Plain functions --------------------------------------------------

    def test_keyword_only_function_passes(self):
        node = astroid.extract_node("def function(*, parameter): ... #@")
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_function_with_no_arguments_passes(self):
        node = astroid.extract_node("def function(): ... #@")
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_single_positional_argument_is_flagged(self):
        node = astroid.extract_node("def function(parameter): ... #@")
        with self.assertAddsMessages(
            _expected_message(node, name="function", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    def test_two_positional_arguments_are_flagged(self):
        node = astroid.extract_node("def function(first, second): ... #@")
        with self.assertAddsMessages(
            _expected_message(node, name="function", positional=2, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    def test_positional_only_argument_is_flagged(self):
        node = astroid.extract_node("def function(parameter, /): ... #@")
        with self.assertAddsMessages(
            _expected_message(node, name="function", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    def test_default_valued_positional_argument_is_flagged(self):
        node = astroid.extract_node("def function(parameter=None): ... #@")
        with self.assertAddsMessages(
            _expected_message(node, name="function", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    # --- Variadic parameters ---------------------------------------------

    def test_var_positional_only_passes(self):
        node = astroid.extract_node("def function(*args): ... #@")
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_var_positional_with_keyword_only_passes(self):
        node = astroid.extract_node("def function(*args, keyword): ... #@")
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_var_keyword_only_passes(self):
        node = astroid.extract_node("def function(**kwargs): ... #@")
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    # --- Methods ----------------------------------------------------------

    def test_method_with_only_self_passes(self):
        node = astroid.extract_node(
            """
            class Class:
                def method(self): ... #@
            """
        )
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_method_positional_argument_is_flagged(self):
        node = astroid.extract_node(
            """
            class Class:
                def method(self, parameter): ... #@
            """
        )
        with self.assertAddsMessages(
            _expected_message(node, name="method", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    def test_method_keyword_only_argument_passes(self):
        node = astroid.extract_node(
            """
            class Class:
                def method(self, *, parameter): ... #@
            """
        )
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_classmethod_positional_argument_is_flagged(self):
        node = astroid.extract_node(
            """
            class Class:
                @classmethod
                def method(cls, parameter): ... #@
            """
        )
        with self.assertAddsMessages(
            _expected_message(node, name="method", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    def test_staticmethod_counts_its_first_argument(self):
        node = astroid.extract_node(
            """
            class Class:
                @staticmethod
                def method(parameter): ... #@
            """
        )
        with self.assertAddsMessages(
            _expected_message(node, name="method", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    def test_dunder_init_is_still_checked(self):
        node = astroid.extract_node(
            """
            class Class:
                def __init__(self, parameter): ... #@
            """
        )
        with self.assertAddsMessages(
            _expected_message(node, name="__init__", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    # --- Exempt protocol methods -----------------------------------------

    def test_comparison_dunder_is_exempt(self):
        node = astroid.extract_node(
            """
            class Class:
                def __eq__(self, other): ... #@
            """
        )
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_getitem_dunder_is_exempt(self):
        node = astroid.extract_node(
            """
            class Class:
                def __getitem__(self, key): ... #@
            """
        )
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_property_setter_is_exempt(self):
        node = astroid.extract_node(
            """
            class Class:
                @property
                def value(self): ...

                @value.setter
                def value(self, new_value): ... #@
            """
        )
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_property_deleter_is_exempt(self):
        node = astroid.extract_node(
            """
            class Class:
                @property
                def value(self): ...

                @value.deleter
                def value(self): ... #@
            """
        )
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    # --- Async functions --------------------------------------------------

    def test_async_positional_argument_is_flagged(self):
        node = astroid.extract_node("async def function(parameter): ... #@")
        with self.assertAddsMessages(
            _expected_message(node, name="function", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_asyncfunctiondef(node)

    def test_async_keyword_only_argument_passes(self):
        node = astroid.extract_node("async def function(*, parameter): ... #@")
        with self.assertNoMessages():
            self.checker.visit_asyncfunctiondef(node)

    # --- Reported location ------------------------------------------------

    def test_message_is_reported_at_the_function_definition(self):
        node = astroid.extract_node("def function(parameter): ... #@")
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="missing-keyword-only-marker",
                node=node,
                args=("function", 1, 0),
                line=1,
                col_offset=0,
                end_line=1,
                end_col_offset=12,
            ),
        ):
            self.checker.visit_functiondef(node)


class TestAllowOnePositional(pylint.testutils.CheckerTestCase):
    """With a threshold of 1, exactly one leading positional argument is allowed."""

    CHECKER_CLASS = keyword_only_checker.KeywordOnlyArgumentsChecker
    CONFIG = {"max_positional_arguments": 1}

    def test_single_positional_argument_passes(self):
        node = astroid.extract_node("def function(parameter): ... #@")
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_one_positional_then_keyword_only_passes(self):
        node = astroid.extract_node("def function(first, *, second): ... #@")
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_two_positional_arguments_are_flagged(self):
        node = astroid.extract_node("def function(first, second): ... #@")
        with self.assertAddsMessages(
            _expected_message(node, name="function", positional=2, allowed=1),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    def test_positional_only_then_positional_is_flagged(self):
        node = astroid.extract_node("def function(first, /, second): ... #@")
        with self.assertAddsMessages(
            _expected_message(node, name="function", positional=2, allowed=1),
            ignore_position=True,
        ):
            self.checker.visit_functiondef(node)

    def test_method_with_one_positional_passes(self):
        node = astroid.extract_node(
            """
            class Class:
                def method(self, parameter): ... #@
            """
        )
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)

    def test_one_positional_with_var_positional_passes(self):
        node = astroid.extract_node("def function(first, *args): ... #@")
        with self.assertNoMessages():
            self.checker.visit_functiondef(node)


class TestLambdasDisabledByDefault(pylint.testutils.CheckerTestCase):
    """Lambdas are ignored unless ``check-lambdas`` is enabled."""

    CHECKER_CLASS = keyword_only_checker.KeywordOnlyArgumentsChecker
    CONFIG = {"max_positional_arguments": 0, "check_lambdas": False}

    def test_positional_lambda_is_ignored(self):
        node = astroid.extract_node("lambda parameter: parameter #@")
        with self.assertNoMessages():
            self.checker.visit_lambda(node)


class TestLambdasEnabled(pylint.testutils.CheckerTestCase):
    """With ``check-lambdas`` enabled, lambdas follow the same rule."""

    CHECKER_CLASS = keyword_only_checker.KeywordOnlyArgumentsChecker
    CONFIG = {"max_positional_arguments": 0, "check_lambdas": True}

    def test_positional_lambda_is_flagged(self):
        node = astroid.extract_node("lambda parameter: parameter #@")
        with self.assertAddsMessages(
            _expected_message(node, name="<lambda>", positional=1, allowed=0),
            ignore_position=True,
        ):
            self.checker.visit_lambda(node)

    def test_keyword_only_lambda_passes(self):
        node = astroid.extract_node("lambda *, parameter: parameter #@")
        with self.assertNoMessages():
            self.checker.visit_lambda(node)


class TestMessageFormat:
    """Guard against a message template / arguments mismatch.

    ``UnittestLinter`` does not render the template, so the placeholder count is
    never validated by the checker tests above. Formatting it here ensures a real
    pylint run (which does render it) will not raise ``TypeError``.
    """

    def test_template_formats_with_three_arguments(self):
        template = keyword_only_checker.KeywordOnlyArgumentsChecker.msgs["W9011"][0]
        rendered = template % ("function", 1, 0)
        assert "function" in rendered
