from __future__ import annotations

from typing import Generator, Union
from itertools import islice
from collections import OrderedDict
import json
import itertools
import re

from .index import Template, Statement, BinaryOperator, runtime_function_regex, runtime_index
from .utils import get_runtime_index, flatten_container


class GTMRuntime:

    def __init__(self, runtime_container: list):
        self.runtime_container = runtime_container

    @property
    def templates(self) -> Generator:
        """
        :return: Creates a generator containing all found templates within the runtime section
        :rtype: Generator
        """
        templates_to_gen = (GTMRuntimeTemplate(template) for template in self.runtime_container)

        return templates_to_gen

    @property
    def template_names(self) -> Generator:
        return (template.name for template in self.templates)

    @property
    def length(self):
        template_length = len(list(self.templates))

        return template_length

    def fetch_template(self, template_index: int) -> GTMRuntimeTemplate:
        """
        Fetches a template from the available templates by their index
        :param template_index: index of template to return
        :type template_index: int
        :return: Returns a RuntimeTemplate object
        :rtype: GTMRuntimeTemplate
        """
        template = next(islice(self.templates, template_index, None))

        return template


class GTMRuntimeTemplate:
    def __init__(self, template: Template):
        # TODO maybe implement this as a generator too, to save memory and adapt other methods?
        self.contents = template
        self.cache = []
        self.counter = 0

    @property
    def length(self):
        length = len(self.contents)

        return length

    @property
    def name(self):
        name = self.contents[1]

        return name

    # TODO Improve this once the role of index 46 has been established.
    #   Grabbing the field_data variable this is is kind of crude
    # fix-me naming of this function is highly inefficient
    @property
    def field_data_variable(self):
        variable = self.contents[2][1]

        return variable

    @property
    def template_main_function(self):
        """
        Generate the main function that hold the whole template data
        :return: String representation of the main template function
        :rtype: str
        """
        symbol = get_runtime_index(self.contents[0], 'symbol')
        name = self.name
        body = f'{symbol} {name}() {{}};'

        return body

    @property
    def lets(self) -> Generator:
        """
        Create a generator of "let" variable declarations
        :return: let variables generator
        :rtype: Generator
        """
        return self._find_nested_index_and_name(41)

    @property
    def consts(self) -> Generator:
        """
        Create a generator of "const" variable declarations
        :return: const variables generator
        :rtype: Generator
        """
        return self._find_nested_index_and_name(52)

    @property
    def vars(self):
        """
        Grab the first occurrence of the 41 index in the template, which defines the list of "var" declared variables
        :return: var variables generator
        :rtype: Generator
        """
        stripped_template = self.contents[3:4]

        for item in stripped_template:
            if isinstance(item, list) and item[0] == 41:
                for var in item[1:]:
                    yield var

    @property
    def functions(self, member_list: bool = True):
        """
        Create a generator of "function" declarations and assignments
        :param member_list: If True return a list of function names. Else prints a detailed dict.
        :type member_list: bool
        :return: function declaration/assignment generator
        :rtype: Generator
        """

        cache = {}
        count = 1
        function_names = []

        # needed to bypass the first 50 "function" declaration
        stripped_template = self.contents[1:]

        # Adds function declaration to list if function is directly declared or declared through variable assignment
        for item in stripped_template:
            if (isinstance(item, list) and item[0] == 50) or \
                    (isinstance(item, list) and (item[0] == 52 or item[0] == 41)
                     and (len(item) == 3 and item[2][0] == 51)):
                cache[f'declared_function_{stripped_template.index(item) - 2}:'] = item[1]
                function_names.append(item[1])

        for item in self._find_nested_index_and_name(51, False):
            cache[f'assigned_function_{count}:'] = item
            count += 1
            function_names.append(item)

        if not member_list:
            return ((k, v) for (k, v) in cache.items())

        return (x for x in function_names)

    # TODO get index counter by the index symbol/sign (i.e. "<<")
    def count_occurrences(self, index: int, count_all: bool = False, print_to_console: bool = True) -> Union[int, dict]:
        """
        Count occurrences of a runtime index values within the current template.
        :param index: runtime index value found within the template
        :type index: int
        :param count_all: if TRUE count all indexes regardless of given index
        :type count_all: bool
        :param print_to_console: if FALSE does not print results to console
        :type print_to_console: bool
        :return: Returns a simple integer if count_all is set to False. Returns a dictionary of index: index_count if count_all is set to True
        :rtype: Union[int, dict]
        """
        template = list(flatten_container(self.contents))

        response_dict = dict()

        if not count_all:
            if index not in runtime_index.keys():
                raise KeyError(f'Please choose a value between 1 and 66')
            else:
                count = template.count(index)

            response = count
            if print_to_console:
                print(f'Found {count} instances of {runtime_index[index]}')

            return response
        else:
            for item in template:
                if item in runtime_index.keys():
                    count = list(template).count(item)
                    response_dict[f'{item}'] = count

            if print_to_console:
                print(response_dict)

    """
    The properties below only provide the names of the items.
    For example: self.lets would be a list of all "let" declared variables.
        Try to create with an argument or another function altogether that "pretty" prints
        the data. Example: lets_literal() (a method not a property!) print "let a;"
            Although, this might be tricky. Doing this, what happens to variables that have assignment? 
                The assignment should be included in the print.
    """

    def _find_nested_index_and_name(self, var_type: int, unique: bool = True) -> Generator:
        """
        Create a generator of given index and their names
        :return: let/cont variables generator
        :rtype: Generator
        """

        # TODO try to redo the lower inner function with generators. What you have tried is right here, below.
        #   This does not seems to work. If a copy of container is yielded it just simply shows nothing
        #   and only parses the first occurrence of 41 index
        #   Also check the implementation of "consts"
        # def count_lets(container):
        #
        #     for idx, item in enumerate(container):
        #         if item == 41:
        #             yield item
        #         elif isinstance(item, list):
        #             for j in count_lets(item):
        #                 if j == 41:
        #                     yield item

        cache = []
        var = var_type

        # needed to bypass the first 41 "var" declaration in case of "let"
        if self.contents[3][0] == 41:
            stripped_template = self.contents[4:]
        else:
            stripped_template = self.contents[3:]

        def indexer(container):
            nonlocal cache
            container_copy = container.copy()

            for idx, item in enumerate(container):
                if item == var:
                    cache.append(container_copy[1])
                elif isinstance(item, list):
                    for j in indexer(item):
                        if j == var:
                            cache.append(container[1])

            # using OrderedDict to make the list unique
            if not unique:
                return (let for let in cache)
            else:
                cache = list(OrderedDict.fromkeys(cache))
                return (let for let in cache)

        return indexer(stripped_template)

    def _parse_container(self, container_line):

        def parser(line):
            for idx, item in enumerate(line):
                if isinstance(item, int):
                    try:
                        index_method = get_runtime_index(item, 'method')
                        method_call = getattr(self, index_method)(line)
                        return method_call
                    except KeyError:
                        continue
                if isinstance(item, str) and line[0] == 'require':
                    index_method = get_runtime_index(line[0], 'method')
                    method_call = getattr(self, index_method)(line)
                    return method_call
                if isinstance(item, str) and (item in self.functions or item in self.consts or item in self.vars or
                                              item in self.lets):
                    return self.parse_function_call(line)
                elif isinstance(item, list):
                    try:
                        index_method = get_runtime_index(item[0], 'method')
                        method_call = getattr(self, index_method)(item)
                        return method_call
                    except KeyError:
                        continue

        container_string = self._sanitize_container_string(parser(container_line))

        return container_string

    def parse_template(self) -> str:

        template = [self.contents]
        template_string = ""

        for line in template:
            template_string += self._parse_container(line)

        return template_string

    # fixme this section has some duplicated code. Keep yourself DRY an improve the code.
    def parse_binary_operator(self, container) -> str:
        """
        Handles parsing of binary operators that take two operands as arguments (i.e. "+", "||", "==" etc.)
        :return: string representation of parsed operator
        :rtype: str
        """
        arg1 = container[1]
        arg2 = container[2]
        operator_symbol = get_runtime_index(container[0], 'symbol')

        try:
            exception_string = container[3]
        except IndexError:
            exception_string = ''

        # fixme has dependency with parse_ternary_operator
        if container[0] == 17:
            if isinstance(arg2, list):
                container_string = f'{self._parse_container(arg1)}{operator_symbol}{self._parse_container(arg2)}'
                return container_string

            if isinstance(arg2, str):
                container_string = f'{self._parse_container(arg1)}{operator_symbol}{arg2}'
                return container_string

        if isinstance(arg1, list):
            if isinstance(arg2, list):
                container_string = f'{self._parse_container(arg1)} {operator_symbol} {self._parse_container(arg2)}'
                return container_string

            if isinstance(arg2, int):
                container_string = f'{self._parse_container(arg1)} {operator_symbol} {arg2}'
                return container_string

            if isinstance(arg2, str):
                if arg2 not in self.vars and arg2 not in self.lets and arg2 not in self.consts:
                    container_string = f'{self._parse_container(arg1)} {operator_symbol} \'{arg2}\''
                else:
                    container_string = f'{self._parse_container(arg1)} {operator_symbol} {arg2}'
                return container_string

        elif isinstance(arg1, str) or isinstance(arg1, int):
            if isinstance(arg2, list):
                arg2 = self._parse_container(arg2)

                if exception_string == 'property_setter':
                    container_string = f'{arg1} {operator_symbol} {arg2};'
                    return container_string

                # this checks if the binary argument is eligible for quoting
                if arg1 not in self.vars and arg1 not in self.lets and arg1 not in self.consts:
                    container_string = f'{arg1} {operator_symbol} {arg2}'
                elif arg1 in self.vars:
                    container_string = f'var {arg1} {operator_symbol} {arg2}'
                else:
                    container_string = f'{arg1} {operator_symbol} {arg2}'
                return container_string
            elif isinstance(arg2, str):
                if isinstance(arg1, int):
                    if arg1 in self.vars:
                        container_string = f'var {arg1} {operator_symbol} \'{arg2}\''
                    else:
                        container_string = f'{arg1} {operator_symbol} \'{arg2}\''
                elif arg1 in self.vars:
                    container_string = f'var {arg1} {operator_symbol} \'{arg2}\''
                else:
                    container_string = f'{arg1} {operator_symbol} \'{arg2}\''

                return container_string
            elif isinstance(arg2, int):
                if arg1 in self.vars:
                    container_string = f'var {arg1} {operator_symbol} {arg2}'
                else:
                    container_string = f'{arg1} {operator_symbol} {arg2}'
                return container_string

    def parse_unary_operator(self, container) -> str:
        """
        Handles parsing of unary operators "!", "~", "-" etc.
        :return: string representation of parsed operator
        :rtype: str
        """
        arguments = container[1]
        operator_symbol = get_runtime_index(container[0], 'symbol')

        try:
            operator_variation = get_runtime_index(container[0], 'variation')
        except KeyError:
            operator_variation = ''

        # the postfix and prefix sections do not actually parse the whole container.
        #   since we do not really care about the functionality of the operator
        #   we can only parse it to show it accordingly.

        if operator_variation == 'prefix':
            temp_arg = arguments[1]
            container_string = f'{operator_symbol}{temp_arg}'
            return container_string

        if isinstance(arguments, list):
            arguments = self._parse_container(arguments)

        if operator_variation == 'postfix':
            container_string = f'{arguments}{operator_symbol}'
            return container_string

        if operator_symbol == 'typeof':
            container_string = f'{operator_symbol} {arguments}'
        else:
            container_string = f'{operator_symbol}{arguments}'

        return container_string

    def parse_method_accessor(self, container) -> str:

        raw_object = container[1]
        _object = ''
        _is_pattern = False

        if isinstance(raw_object, list):
            _object = self._parse_container(raw_object)

        _property = container[2]
        _method_arguments = container[3]
        arguments = []
        argument_string = ''

        if isinstance(_method_arguments, list):
            arguments = self._parse_container(_method_arguments)

        base_string = f'{_object}.{_property}('

        # better-me the regex matching is done to find instances of situations similar to "s.length -1" which
        #   should be literal but are otherwise quoted.
        if len(arguments) == 1:
            if any(re.search(re.escape(f'.*{operator.value}.*'), arguments[0]) for operator in BinaryOperator):
                argument_string += f'{arguments[0]}'
            elif any(re.search(f'.*{operator.value}.*', arguments[0]) for operator in Statement):
                argument_string += f'{arguments[0]}'
            elif arguments[0] in (self.lets or self.vars or self.consts or self.functions):
                argument_string += f'{arguments[0]}'
            else:
                argument_string += f'\'{arguments[0]}\''
        else:
            for arg in arguments:
                argument_string += f'{arg},'

        if argument_string.endswith(','):
            argument_string = argument_string[:-1]

        container_string = base_string + argument_string + ')'

        return container_string

    def parse_array_literal(self, container) -> list:
        if len(container) == 1:
            return list()

        argument_list = []

        for argument in container[1:]:
            if isinstance(argument, list):
                raw_argument = self._parse_container(argument)
                argument_list.append(raw_argument)
            elif isinstance(argument, str):
                argument_list.append(argument)

        return argument_list

    def parse_key_value_object(self, container) -> str:

        if len(container) == 1:
            return '{}'

        argument_dict = {}

        for idx, argument in enumerate(container[1:]):
            if isinstance(argument, list):
                if container[0] == 15:
                    container[idx + 1] = self._parse_container(argument)
                else:
                    container[idx + 1] = f'{{{{{self._parse_container(argument)}}}}}'

        dict_keys = container[1:][::2]
        dict_values = container[1:][1::2]

        for (k, v) in itertools.zip_longest(dict_keys, dict_values):
            argument_dict[k] = v

        # to be able to correctly print javascript code unquoted, dictionaries are not a good strategy.
        #   they are natively converted to string. Converting the dict to JSON (a string) and then removing
        #   quotes works.

        argument_dict = re.sub(r'("{{)|(}}")', '', json.dumps(argument_dict))

        # attempt to remove character escapes
        # better-me address this possible issues. What if in the array body you want the given string to be shown as
        #   escaped? i.e literal '\"USD\"'. Meanwhile, his replaces escapes

        argument_dict = re.sub(r'\\\s*([nt])', '', argument_dict)

        return argument_dict

    def parse_let_const(self, container):
        value_type = ''
        container_string = ''

        if len(container) > 3 and container[0] == 41:
            return container_string

        if container[0] == 52:
            value_type = 'const'

        if container[0] == 41:
            value_type = 'let'

        value_name = container[1]
        try:
            assignment = container[2]
        except IndexError:
            container_string = f'{value_type} {value_name};'
            return container_string

        if isinstance(assignment, list):
            assignment_value = self._parse_container(assignment)
            container_string = f'{value_type} {value_name} = {assignment_value}\n'
        elif isinstance(assignment, str):
            container_string = f'{value_type} {value_name} = {assignment}\n'

        return container_string

    def parse_switch_statement(self, container):

        switch_identifier = ''

        # Parse the identifier - argument 1
        if isinstance(container[1], list):
            switch_identifier = self._parse_container(container[1])

        switch_head = f'switch ({switch_identifier}) {{'

        # parse through the argument declaration list - argument 2

        raw_switch_cases = self.get_arguments(container[2])
        parsed_cases = []

        for idx, argument in enumerate(raw_switch_cases):
            if isinstance(argument, list):
                parsed_cases.append(self._parse_container(argument))
                continue

            parsed_cases.append(argument)

        # parse through the body arguments - argument 3

        switch_body = self.get_arguments(container[3])

        if raw_switch_cases == [] and switch_body == []:
            switch_head += '}'
            return switch_head

        expression_string = []

        for idx, item in enumerate(switch_body):
            if isinstance(item, list):
                expression_string.append(self._parse_container(item))

        switch_statement_string = switch_head + ''.join(expression_string)

        for idx, arg in enumerate(parsed_cases):
            switch_statement_string = switch_statement_string.replace(f'%%%%{idx}', str(parsed_cases[idx]))

        # temporary replacement for the "default"
        switch_statement_string = re.sub(r" %%%%\d", "", switch_statement_string)
        switch_statement_string += '};'

        return switch_statement_string

    # parse the switch body arguments such as "case" or "default"
    def parse_switch_expressions(self, container):

        case_string = f'{get_runtime_index(container[0], "symbol")} %%%%{self.counter}:'
        self.counter += 1

        case_body = []

        for idx, item in enumerate(container[1:]):
            if isinstance(item, list):
                arguments = self.get_arguments(item)

                for arg in arguments:
                    case_body.append(self._parse_container(arg) + ';')

        case_body = '\n'.join(case_body)

        switch_expression_body = case_string + case_body

        return switch_expression_body

    def parse_return_statement(self, container):
        return_statement_literal = get_runtime_index(container[0], 'symbol')

        if len(container) == 1:
            return 'return;'

        return_arguments = container[1]

        return_string = ''

        if isinstance(return_arguments, list):
            return_str = self._parse_container(return_arguments)

            if isinstance(return_str, list) and not return_str:
                return_str = '[]'

            if isinstance(return_str, dict):
                return_string += str(return_str)
            else:
                return_string += return_str

        if isinstance(return_arguments, int):
            return_string += str(return_arguments)

        return_statement_literal = f'{return_statement_literal} {return_string};'

        return return_statement_literal

    def parse_defined_function(self, container):
        function_name = container[1]
        function_arguments = self.get_arguments(container[2])

        # template wise modification of the 'a' variable into the 'data' variable for easier user interpretation
        if any(re.match(regex, function_name) for regex in runtime_function_regex):
            function_arguments = ['data']

        function_body = container[3:]

        function_start_string = f'function {function_name}('
        function_body_string = ''

        for argument in function_arguments:
            if argument == function_arguments[-1]:
                function_start_string += f'{argument}'
            else:
                function_start_string += f'{argument}, '

        function_start_string += ') {'

        for part in function_body:
            if isinstance(part, list):
                function_body_string += self._parse_container(part)

        function_string = function_start_string + function_body_string + '}'

        return function_string

    def parse_return_multiple(self, container):
        multiple_returns = container[1:]
        return_literals = ''

        for idx, item in enumerate(multiple_returns):
            if idx == len(multiple_returns) - 1:
                if isinstance(item, list):
                    return_literals += f'{str(self._parse_container(item))}'
                else:
                    return_literals += f'{str(item)}'
            elif isinstance(item, list):
                return_literals += f'{str(self._parse_container(item))}, '

        return return_literals

    def parse_property_accessor(self, container):
        accessed_object = container[1]
        object_property = container[2]

        if isinstance(object_property, str):
            object_property = f'\'{object_property}\''

        if isinstance(object_property, list):
            object_property = self._parse_container(object_property)

        if isinstance(accessed_object, list):
            accessed_object = self._parse_container(accessed_object)

        property_access_string = f'{accessed_object}[{object_property}]'

        return property_access_string

    def parse_ternary_operator(self, container):
        condition = container[1]
        if_true = container[2]
        if_false = container[3]

        if isinstance(condition, list):
            condition = self._parse_container(condition)

        if isinstance(if_true, list):
            if_true = self._parse_container(if_true)

        if isinstance(if_false, list):
            if_false = self._parse_container(if_false)

        ternary_operator_string = f'{condition} ? {if_true} : {if_false}'

        return ternary_operator_string

    def parse_property_setter(self, container):
        set_to_object = container[1]
        property_to_set = container[2]
        property_value = container[3]
        left_operand_string = ''

        if isinstance(set_to_object, list):
            set_to_object = self._parse_container(set_to_object)

        if isinstance(property_to_set, str):
            try:
                property_to_set = int(property_to_set)
                left_operand_string = f'{set_to_object}["{property_to_set}"]'
            except ValueError:
                left_operand_string = f'{set_to_object}.{property_to_set}'

        if isinstance(property_to_set, list):
            left_operand_string = f'{set_to_object}[{self._parse_container(property_to_set)}]'

        property_setter_string = self.parse_binary_operator([3, left_operand_string, property_value, 'property_setter'])

        return property_setter_string

    def parse_function_call(self, container):
        function_name = container[0]
        function_call_arguments = container[1:]
        function_call_string = f'{function_name}('

        for arg in function_call_arguments:
            if isinstance(arg, list):
                function_call_string += f'{self._parse_container(arg)}'

            if isinstance(arg, int):
                function_call_string += f'{arg}'

            if isinstance(arg, str):
                function_call_string += f'\'{arg}\''

            if arg != function_call_arguments[-1]:
                function_call_string += ', '

        function_call_string += ")"

        return function_call_string

    def parse_assigned_function(self, container):
        function_name = container[1]
        function_arguments = container[2][1:]
        function_head_string = f'function {function_name}('
        function_body_string = ''
        local_scope = []

        try:
            function_body = container[3:]
        except IndexError:
            function_body = []

        if function_arguments == [] and function_body == []:
            return f'function {function_name}(){{}};'

        for arg in function_arguments:
            function_head_string += f'{arg}'

            if arg != function_arguments[-1]:
                function_head_string += ', '

        function_head_string += ') {'

        for part in function_body:
            if isinstance(part, list):
                if part[0] == 41:
                    local_scope.append(part[1])
                elif part[0] == 52:
                    function_body_string += f'const {self.parse_binary_operator([3, part[1], part[2]])};'
                elif part[0] == 3 and part[1] in local_scope:
                    function_body_string += f'let {self._parse_container(part)};'
                else:
                    function_body_string += f'{self._parse_container(part)}'

        function_body_string = function_head_string + function_body_string + '}'

        return function_body_string

    def parse_if_statement(self, container):
        if_condition = container[1]
        if_body = self.get_arguments(container[2])

        # better-me Although it does not break functionality, it should be clearly stated in method names, along indexes
        #   that the 53 index actually refers to scoping and not strictly for loops.
        # upon analysis, it was found that index 53 actually refers to the scope of the expressions being a
        #   representative of 'let'. This explains why ``for`` statements with 'let' declarations have the for
        #   statement body inside the '63' index, because index 63 is the actual for.
        # This behaviour was observed when index 53 was encountered inside an if statement which was not behaving
        #   as a for loop statement.
        # Test with if statements with variable declarations with let, along let declared for loops
        #   confirmed the theory above.
        # This conditional here check if the conditional body is a let declaration and interprets accordingly.
        if if_body[0][0] == 53:
            if_body = self.get_arguments(if_body[0])

        else_header_string = ''

        if_body_string = ''
        else_body_string = ''

        if isinstance(if_condition, list):
            if_condition = self._parse_container(if_condition)

        if_header_string = f'if ({if_condition}) {{'

        try:
            else_body = self.get_arguments(container[3])
        except IndexError:
            else_body = ''

        if else_body:
            else_header_string = f'else {{'

        if isinstance(else_body, list) and else_body[0][0] == 22:
            else_header_string = f'else'

        if not if_body:
            if_body_string = ''
        else:
            for part in if_body:
                if isinstance(part, list):
                    if_body_string += f'{self._parse_container(part)}'

        if not else_body:
            else_body_string = ''
        else:
            for idx, part in enumerate(else_body):
                if isinstance(part, list):
                    else_body_string += f'{self._parse_container(part)}'

        # if else
        if else_body:
            if_statement_string = f'{if_header_string} {if_body_string}}} {else_header_string} {else_body_string}'
            return if_statement_string

        # if
        if not else_body:
            if_statement_string = f'{if_header_string} {if_body_string}}}'
            return if_statement_string

    def parse_for_a_of_in_b(self, container):

        for_body_string = ''
        var_type = ''
        for_type = ''
        for_body = []

        if container[0] == 64:
            var_type = 'var'
            for_type = 'of'
        elif container[0] == 47:
            var_type = 'var'
            for_type = 'in'

        if container[0] == 66:
            var_type = 'let'
            for_type = 'of'
        elif container[0] == 55:
            var_type = 'let'
            for_type = 'in'

        if container[0] == 64 or container[0] == 66:
            if len(container[3]) == 1:
                for_body = ''
            else:
                for_body = container[3][1][1:]
        elif container[0] == 47 or container[0] == 55:
            for_body = self.get_arguments(container[3])

        for_index = container[1]
        for_iterable = container[2]

        if isinstance(for_index, list):
            for_index = self._parse_container(for_index)

        if isinstance(for_iterable, list):
            for_iterable = self._parse_container(for_iterable)

        for_header_string = f'for ({var_type} {for_index} {for_type} {for_iterable}) {{'

        for part in for_body:
            if isinstance(part, list):
                for_body_string += f'{self._parse_container(part)}'

        for_body_string += '}'

        for_statement_string = f'{for_header_string}{for_body_string}'

        return for_statement_string

    def parse_while_var_for_statement(self, container):
        while_statement_string = ''
        while_conditional_string = ''
        while_body_string = ''

        while_conditional = container[1]
        is_for_conditional = container[2]
        is_do_while = container[3]

        # while and for statements share the same index with differences in the container body.
        #   this checks' if the current 42 index container is a while or loop statement container.
        if is_for_conditional[0] != 46:
            return self.parse_standard_var_for_loop(container)
        if is_do_while == 'false':
            is_do_while = False
        elif is_do_while == 'true':
            is_do_while = True

        while_body = self.get_arguments(container[4])

        if isinstance(while_conditional, list):
            while_conditional_string = self._parse_container(while_conditional)

        for part in while_body:
            if isinstance(while_body, list):
                while_body_string += f'{self._parse_container(part)}'

        if not is_do_while:
            while_statement_string = f'while ({while_conditional_string}) {{{while_body_string}}}'
        elif is_do_while:
            while_statement_string = f'do {{{while_body_string}}} while ({while_conditional_string});'

        return while_statement_string

    def parse_standard_var_for_loop(self, container):
        for_conditional_string = ''
        for_afterthought_string = ''
        for_body_string = ''

        for_conditional = container[1]

        if isinstance(for_conditional, list):
            for_conditional_string = self._parse_container(for_conditional)

        for_afterthought = container[2]

        if isinstance(for_afterthought, list):
            for_afterthought_string = self._parse_container(for_afterthought)

        for_body = container[4]

        # Another confirmation for the situation of the 53 index in the case of the "if_statement"
        #   Confirmed in the so-called "standard_var_for_loop" parser - index 53 arguments of a certain statement
        #   that are scoped to permit "let" variable declarations.
        if for_body[1][0] == 53:
            for_body = self.get_arguments(for_body[1])

        for part in for_body:
            if isinstance(part, list):
                for_body_string += f'{self._parse_container(part)}'

        for_statement_string = f'for (; {for_conditional_string}; {for_afterthought_string}) {{{for_body_string}}}'

        return for_statement_string

    def parse_standard_let_for_loop(self, container):
        for_initializer_string = ''
        for_conditional = ''
        for_afterthought = ''
        for_body = ''

        for_let_declaration_list = self.get_arguments(container[1])
        for_assigned_initializer_list = container[2:-1]

        for_arguments = self._parse_container(container[-1])

        if isinstance(for_arguments, dict):
            for_conditional = for_arguments['for_conditional']
            for_afterthought = for_arguments['for_afterthought']
            for_body = for_arguments['for_body']

        if for_assigned_initializer_list and for_assigned_initializer_list[0][0] == 3:
            for assignment in for_assigned_initializer_list:
                if assignment[0] == 3:
                    try:
                        for_let_declaration_list.remove(assignment[1])
                    except ValueError:
                        continue

                if isinstance(assignment, list):
                    for_initializer_string += f'{self._parse_container(assignment)}, '

        for idx, declaration in enumerate(for_let_declaration_list):
            if idx == len(for_let_declaration_list) - 1:
                for_initializer_string += f'{declaration}'
            else:
                for_initializer_string += f'{declaration}, '

        for_statement_string = f'for (let {for_initializer_string}; {for_conditional}; ' \
                               f'{for_afterthought}) {{{for_body}}}'

        return for_statement_string

    def parse_for_loop_body(self, container) -> dict:
        for_body_conditional_string = ''
        for_body_afterthought_string = ''
        for_body_string = ''
        for_body_variable_list = container[1]
        for_body_conditional = container[2]

        if isinstance(for_body_conditional, list):
            for_body_conditional_string = self._parse_container(for_body_conditional)

        for_body_afterthought = container[3]

        if isinstance(for_body_afterthought, list):
            for_body_afterthought_string = self._parse_container(for_body_afterthought)

        for_body = self.get_arguments(container[4])

        for part in for_body:
            if isinstance(part, list):
                for_body_string += f'{self._parse_container(part)}'

        for_body_string_dict = {
            'for_conditional': for_body_conditional_string,
            'for_afterthought': for_body_afterthought_string,
            'for_body': for_body_string,
            'for_body_variable_list': for_body_variable_list
        }

        return for_body_string_dict

    @staticmethod
    def parse_value_reference(container) -> str:
        if container[0] == 15 and container[1] == 'a':
            return 'data'
        if container[0] == 15:
            return container[1]

    @staticmethod
    def parse_require_exception(container) -> str:
        container_string = ''

        if container[0] == 'require':
            container_string = f'require("{container[1]}");'

        return container_string

    @staticmethod
    def parse_simple_statement(container):
        statement_string = get_runtime_index(container[0], 'symbol')

        return statement_string

    @staticmethod
    def _sanitize_container_string(container_string: str) -> str:

        if isinstance(container_string, str):
            sanitized_string = re.sub(r';{2,}$', ';', container_string)
        else:
            return container_string

        return sanitized_string

    @staticmethod
    def get_arguments(container):
        return container[1:]
