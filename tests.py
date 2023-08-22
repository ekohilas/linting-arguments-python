import astroid
import my_plugin
import pylint.testutils


class TestArgumentChecker(pylint.testutils.CheckerTestCase):
    CHECKER_CLASS = my_plugin.ArgumentChecker

    def test_(self):
        # def function(p1, /, p2, *, p4, **p3): ...

        call = astroid.extract_node(
            """
            def function(pp, /, p, *l, kp, **kps): ...

            function(1, a2, 3, a4, kp=5, p3=6) #@
            """
        )
        assert not my_plugin.check_call_arguments(
            function_call=call,
        )

        # with self.assertNoMessages():
        #     ...
            # self.checker.visit_functiondef(func_node)
            # self.checker.visit_return(return_node_a)
            # self.checker.visit_return(return_node_b)

    def test_function_named_variable_param(self):
        call = astroid.extract_node(
            """
            def function(parameter): ...
            
            argument = None
            function(parameter=argument)
            """
        )
        assert my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_function_unnamed_param(self):
        call = astroid.extract_node(
            """
            def function(parameter): ...
        
            function(None)
            """
        )
        assert not my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_function_named_param(self):
        call = astroid.extract_node(
            """
            def function(parameter): ...
            
            function(parameter=None)
            """
        )
        assert my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_method_unnamed_param(self):
        call = astroid.extract_node(
            """
            class Class:
                def method(self, parameter): ...
            
            Class().method(None)
            """
        )
        assert not my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_method_unnamed_variable_param(self):
        call = astroid.extract_node(
            """
            class Class:
                def method(self, parameter): ...
        
            argument = None
            Class().method(argument)
            """
        )
        assert not my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_method_named_variable_param(self):
        call = astroid.extract_node(
            """
            class Class:
                def method(self, parameter): ...
        
            Class().method(parameter=argument)
            """
        )
        assert my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_classmethod_unnamed_variable_param(self):
        call = astroid.extract_node(
            """
            class Class:
                @classmethod
                def method(cls, parameter): ...
        
            argument = None
            Class.method(argument)
            """
        )
        assert not my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_classmethod_named_variable_param(self):
        call = astroid.extract_node(
            """
            class Class:
                @classmethod
                def method(cls, parameter): ...
        
            argument = None
            Class.method(parameter=argument)
            """
        )
        assert my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_staticmethod_unnamed_param(self):
        call = astroid.extract_node(
            """
            class Class:
                @staticmethod
                def method(parameter): ...
        
            Class.method(None)
            """
        )
        assert not my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_staticmethod_unnamed_variable_param(self):
        call = astroid.extract_node(
            """
            class Class:
                @staticmethod
                def method(parameter): ...
        
            argument = None
            Class.method(argument)
            """
        )
        assert not my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_staticmethod_named_variable_param(self):
        call = astroid.extract_node(
            """
            class Class:
                @staticmethod
                def method(parameter): ...
        
            argument = None
            Class.method(parameter=argument)
            """
        )
        assert my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_staticmethod_named_param(self):
        call = astroid.extract_node(
            """
            class Class:
                @staticmethod
                def method(parameter): ...
        
            Class.method(parameter=None)
            """
        )
        assert my_plugin.check_call_arguments(
            function_call=call,
        )

    def test_no_argument(self):
        call = astroid.extract_node(
            """
            def function(parameter): ...

            function(None)
            """
        )
        assert my_plugin.check_call_arguments(
            function_call=call,
        ) == False

    """
    def function(default_parameter=None): ...
    
    function()
    """

    """
    def function(default_parameter=None): ...

    argument = None
    function(argument)
    """

    """
    def function(default_parameter=None): ...

    argument = None
    function(default_parameter=argument)
    """

    """
    def function(*arbitrary_parameters): ...

    function()
    """

    """
    def function(*arbitrary_parameters): ...

    function(None)
    """

    """
    def function(*arbitrary_parameters): ...

    function(None, None)
    """

    """
    def function(**keyword_parameters): ... 
    
    function()
    """

    """
    def function(**keyword_parameters): ... 
    
    function(argument=None)
    """

    """
    def function(*arbitrary_parameters, **keyword_parameters): ...

    function(None, argument=None)
    """

    """
    def function(position_only_parameter, /): ...

    argument = None
    function(argument)
    """

    """
    def function(position_only_parameter, /): ...

    function(None)
    """

    """
    def function(position_only_parameter, /): ...

    function(position_only_parameter=None)
    """

    """
    def function(*, keyword_only_parameter): ...

    argument = None
    function(argument)
    """

    """
    def function(*, keyword_only_parameter): ...

    function(None)
    """

    """
    def function(*, keyword_only_parameter): ...

    function(keyword_only_parameter=None)
    """

    """
    Tests
    - combinations
    - lambdas
    - calls with *args
    - calls with **kwargs
    """

    def test_finds_non_unique_ints(self):
        func_node, return_node_a, return_node_b = astroid.extract_node("""
        def test(): #@
            if True:
                return 5 #@
            return 5 #@
        """)

        self.checker.visit_functiondef(node=func_node)
        self.checker.visit_return(return_node_a)
        with self.assertAddsMessages(
            pylint.testutils.MessageTest(
                msg_id="non-unique-returns",
                node=return_node_b,
                line=5,
                col_offset=4,
                end_line=5,
                end_col_offset=12,
            ),
        ):
            self.checker.visit_return(return_node_b)

    def test_ignores_unique_ints(self):
        func_node, return_node_a, return_node_b = astroid.extract_node("""
        def test(): #@
            if True:
                return 1 #@
            return 5 #@
        """)

        with self.assertNoMessages():
            self.checker.visit_functiondef(func_node)
            self.checker.visit_return(return_node_a)
            self.checker.visit_return(return_node_b)