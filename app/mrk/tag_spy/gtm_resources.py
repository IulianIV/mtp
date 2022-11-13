from __future__ import annotations

import re
from typing import Any, Union, Generator
from copy import deepcopy
from abc import ABC, abstractmethod
from .index import macros_index, tags_index, dlvBuiltins_index, evaluations_index,\
    macro_data_keys, resource_list_methods_index, triggers_index
from .utils import find_in_index


class GTMResourceTemplate(ABC):

    def __init__(self, container: list):
        self._original = container
        self._parsed = deepcopy(self._original)

    @property
    def original(self):
        return self._original

    @property
    def parsed(self):
        return self._parsed

    @parsed.setter
    def parsed(self, container: list):
        self._parsed = container

    def get_by_index(self, index: int, original: bool = False) -> Union[dict, list]:
        """
        Grabs the container section member found at the given `index`. By default, it looks into the `parsed` container.
        If `original` is True then it parses the original container.
        :param index: index value to grab
        :type index: int
        :param original: whether to parse the original container
        :type original: bool
        :return: container found at given index.
        :rtype: dict, list
        """
        container = self.parsed

        if original:
            container = self.original

        return container[index]

    def get_by_key_value(self, value: Any, key: Any = None, original: bool = False) -> dict:
        """
        Searches the given container for items that contain the given `key`, `value` pair.
        If only either of arguments is given, it will try to find the first value that contains the given arguments.
        Because of the `list` like structure of the `rules` container, it can not be used there.

        :param original: if passed acts upon the original container
        :type original: bool
        :param key: Key that might be found within the containers items
        :type key: Any
        :param value: Value that is associated with key
        :type value: Any
        :return: The container item where the pair was found
        :rtype: dict
        """
        container = self.parsed

        if original:
            container = self.original

        for item in container:
            if not key:
                if value in item.items():
                    return item
            else:
                if key in item and item[key] == value:
                    return item

    @abstractmethod
    def add_index_data(self):
        """
        Adds supplementary information to each container. The information supplemented is curated from a specific index
        :return: self
        :rtype:
        """
        pass

    @abstractmethod
    def parse(self):
        pass

    def determine_type(self, resource_value: Union[list, str]):
        # determines if type is macro
        if not resource_value:
            return None

        if isinstance(resource_value, int) or isinstance(resource_value, dict):
            return None

        # determines multiple string types
        if resource_value is str and re.match(r'^\(\^\$\|\(\(\^\|,\)[0-9_]+\(\$\|,\)\)\)$', resource_value):
            return re.Pattern

        if resource_value[0] == 'macro' and isinstance(resource_value[1], int):
            return 'macro'

        if resource_value[0] == 'map':
            return 'map'

        if resource_value[0] == 'escape':
            return 'escape'

        if resource_value[0] == 'list':
            return self._determine_list_type(resource_value)

        if resource_value[0] == 'template':
            return self._determine_template_type(resource_value)

    @staticmethod
    def _determine_list_type(resource: list):
        if len(resource) == 1:
            return 'mapping'
        if isinstance(resource[1], list) and resource[1][0] == 'map':
            return 'mapping'
        if isinstance(resource[1], list) and resource[1][0] == 'tag':
            return 'tag_que'

    def _determine_template_type(self, resource: list):
        if self.determine_type(resource[1]) == 'macro':
            return 'generic_template'
        if any(_ for _ in ['function', 'script', 'iframe'] if resource[1].find(_)):
            return 'custom_code_template'
        if not any(_ for _ in ['function', 'script', 'iframe'] if resource[1].find(_)):
            return 'generic_template'
        if re.error('regex_template', resource[1]) == 'regex_template':
            return 'regex_template'

    def get_names(self) -> Generator:
        return (item['function'] for item in self.parsed)


class GTMResourceMacros(GTMResourceTemplate):

    def __init__(self, macro_container: list):
        super().__init__(macro_container)

    def add_index_data(self):

        for macro in self.parsed:
            macro_name = macro['function']
            # Custom Variable Templates have custom naming, this makes it possible to see the custom variable contents
            if macro_name not in macros_index and 'cvt' in macro_name:
                index_details = macros_index['_custom_variable_template']
            # vtp_name can contain special built-in variables that belong to a different index.
            elif 'vtp_name' in macro and macro['vtp_name'] in dlvBuiltins_index:
                index_details = dlvBuiltins_index[macro['vtp_name']]
            else:
                index_details = macros_index[macro_name]

            macro.update(**index_details)

        return self

    def parse(self):

        self.add_index_data()

        for idx, macro in enumerate(self.parsed):
            for key, value in macro.items():
                if self.determine_type(value) == 'macro':
                    macro[key] = value
                elif value == '__remm':
                    self.parsed[idx] = self.process_general_resource(macro, '__remm')
                elif isinstance(value, list):
                    macro[key] = self.process_general_resource(value)
        return self

    def process_general_resource(self, resource_list: Union[list, dict], special_function: str = None):

        if special_function == '__remm':
            method_call = self.process_regex(resource_list)
            return method_call

        value_type = self.determine_type(resource_list)

        if value_type == 'macro':
            method_call = self.get_macro_data_key(self.parsed[resource_list[1]])
            return method_call

        resource_type_method = find_in_index(value_type, resource_list_methods_index)

        method_call = getattr(self, resource_type_method)(resource_list)

        return method_call

    def process_regex(self, macro_dict: dict):
        new_macro = {}

        for key, value in macro_dict.items():
            if isinstance(value, list):
                value_type = self.determine_type(value)

                if value_type == 'mapping':
                    value = self.process_regex_mapping(value)
                else:
                    value = self.process_general_resource(value)

            new_macro[key] = value

        return new_macro

    def process_regex_mapping(self, regex_table: list):
        useful_map = regex_table[1:]
        regex_dict = {}
        regex_list = []
        match_to_list = []
        output_list = []

        for idx, item in enumerate(useful_map):

            reg_ex = item[2][1]
            regex_match_to = item[2][2]

            if isinstance(reg_ex, list):
                reg_ex = self.process_general_resource(reg_ex)

            reg_ex_literal = reg_ex.encode('raw_unicode_escape').decode('unicode_escape')

            if isinstance(regex_match_to, list):
                regex_match_to = self.process_general_resource(regex_match_to)

            regex_output = item[-1]

            if isinstance(regex_output, list):
                regex_output = self.process_general_resource(regex_output)

            regex_list.append(reg_ex_literal)
            match_to_list.append(regex_match_to)
            output_list.append(regex_output)

            regex_dict[f'regex'] = regex_list
            regex_dict[f'match_to'] = match_to_list
            regex_dict[f'output'] = output_list

            regex_dict.update(regex_dict)

        return regex_dict

    def process_mapping(self, container_mapping: list):
        """
        Attempts to create a dictionary of "map" values of some properties
        It tries to automatically assign dict keys and values according to the container mapping
        If dict key and value are given it will attempt to find those keys in the mapping.

        :param container_mapping: The property value which needs to be processed
        :return: Dictionary containing a computer-friendly value mapping
        """
        if container_mapping[0] == 'list' and len(container_mapping) == 1:
            return f'[]'

        if container_mapping[0] == 'map':
            return f'{{}}'

        useful_map = container_mapping[1:]
        map_dict = {}

        for item in useful_map:

            map_key = item[2]
            map_value = item[-1]

            if isinstance(map_key, list):
                map_key = self.process_general_resource(map_key)

            if isinstance(map_value, list):
                map_value = self.process_general_resource(map_value)

            map_dict[map_key] = map_value

            map_dict.update(map_dict)

        return map_dict

    def process_template(self, template: list) -> str:
        template_contents = template[1:]
        template_string = ''
        template_substring = ''

        for item in template_contents:
            if isinstance(item, list):
                template_substring = self.process_general_resource(item)
            elif isinstance(item, str):
                template_substring = item
            template_string += template_substring

        return template_string

    # TODO what do the numbers in the escape mean?
    def process_escape(self, escape: list):
        escape_contents = escape[1]
        escape_string = f'{self.get_macro_data_key(self.parsed[escape_contents[1]])}'

        return escape_string

    # TODO Finish this processing functionality
    def process_metadata(self, metadata: list):
        """
        Some tags, if configured so, have a filled metadata property:
        ["map", "metadata_key", "metadata_value", "metadata_key_2", "metadata_value_2",
        "key_for_tag_name", "Custom Image"]
        If not filled it just shows as metadata: ["map"]

        It behaves as follows: if "include tag name" is checked it prints both last 2 values for the list,
            the penultimate item being mandatory if the conditions is checked. The last item is the tag name.
        Every other data inbetween that and "map" is the literal table of key-value pairs to be added as tag metadata.

        :return:
        :rtype:
        """

    # macros contain certain keys that are used as data referential (i.e. `vtp_name`)
    @staticmethod
    def get_macro_data_key(macro: dict):

        for data in macro_data_keys:
            if data in macro:
                return macro[data]

    def get_macro_by_reference(self, macro_reference: list):

        if self.determine_type(macro_reference) == 'macro':
            return self.parsed[macro_reference[1]]


class GTMResourceTags(GTMResourceTemplate):

    __trigger_conditions = re.compile('if|unless')

    def __init__(self, tag_container: list,
                 macro_container: GTMResourceMacros,
                 rules_container: GTMResourceRules,
                 predicates_container: GTMResourcePredicates):
        super().__init__(tag_container)
        self.macros = macro_container.parse()
        self.rules = rules_container
        self.predicates = predicates_container.parse()

    def add_index_data(self):

        index_details = {}

        for tag in self.parsed:
            tag_name = tag['function']
            if tag_name in tags_index:
                index_details = tags_index[tag_name]
            # This makes sure that if the tag is a Custom Template Tag, the contents are still visible
            elif tag_name not in tags_index and 'cvt' in tag_name:
                index_details = tags_index['_custom_tag_template']

            # adds empty lists that will be populated with triggering rules
            tag['_conditions'] = list()
            tag['_blocking'] = list()

            tag.update(**index_details)

        return self

    def parse(self):

        self.add_index_data()
        self.add_tag_sequencing()
        self.add_tag_rules()

        for idx, tag in enumerate(self.parsed):
            for key, value in tag.items():
                if isinstance(value, list):
                    value_type = self.determine_type(value)

                    if value_type != 'tag_que' and value_type is not None:
                        tag[key] = self.macros.process_general_resource(value)

        return self

    def add_tag_sequencing(self) -> GTMResourceTags:
        tag_que = {}

        for tag in self.parsed:

            tag['_sequence'] = {}

            if 'setup_tags' in tag:
                tag_que.clear()
                setup_literal = tag['setup_tags'][1]
                tag_que['before'] = self.get_by_index(setup_literal[1])['function']
                tag_que['before_index'] = setup_literal[1]

                if setup_literal[-1] == 0:
                    tag_que['before_conditional'] = False
                elif setup_literal[-1] == 1:
                    tag_que['before_conditional'] = True

                tag['_sequence'].update(tag_que)

            if 'teardown_tags' in tag:
                tag_que.clear()
                teardown_literal = tag['teardown_tags'][1]
                tag_que['after'] = self.get_by_index(teardown_literal[1])['function']
                tag_que['after_index'] = teardown_literal[1]

                if teardown_literal[-1] == 0:
                    tag_que['after_conditional'] = False
                elif teardown_literal[-1] == 2:
                    tag_que['after_conditional'] = True

                tag['_sequence'].update(tag_que)

            if 'setup_tags' not in tag and 'teardown_tags' not in tag:
                tag['_sequence'] = {}

        return self

    def add_tag_rules(self) -> GTMResourceTags:

        rules = self.rules.parsed

        for idx, rule_set in enumerate(rules):

            # allows for easy determining the type of the rule
            rule_types = [rule[0] for rule in rule_set]

            # All the checks below are necessary.
            # Upon analysis, it was concluded that there are certain "types" of rules, defined by their members
            # the "members" are described by the conditionals below

            # Member 1 - if no "block" rule is found, it is automatically a "firing" tag
            if 'block' not in rule_types:
                self._add_firing_rules(rule_set, 'firing')

            # Member 2 - if there is no "add" but there is "block" it means it is a "blocking" tag
            if 'block' in rule_types and 'add' not in rule_types:
                self._add_firing_rules(rule_set, 'blocking')

            # Member 3 - If there is "add" and "block" it means the same rules are used as "firing" and "blocking"
            #   conditions
            if 'add' in rule_types and 'block' in rule_types:
                self._add_firing_blocking_rules(rule_set)

        return self

    def _add_firing_rules(self, set_of_rules: list, rule_type: str):
        rule_holder = []

        if rule_type == 'firing':
            rule_condition = 'add'
            rule_condition_holder = '_conditions'
        elif rule_type == 'blocking':
            rule_condition = 'block'
            rule_condition_holder = '_blocking'
        else:
            return f'rule_type {rule_type} is invalid. Please use "firing" or "blocking"'

        for rules in set_of_rules:
            if re.search(self.__trigger_conditions, rules[0]):
                rule_holder.append(rules)
            elif re.search(rule_condition, rules[0]):
                for target in rules[1:]:
                    self.parsed[target][rule_condition_holder].append(list(rule_holder))
        rule_holder.clear()

    def _add_firing_blocking_rules(self, set_of_rules: list):
        firing_rules = []
        blocking_rules = []

        for rules in set_of_rules:
            if re.search(self.__trigger_conditions, rules[0]):
                blocking_rules.append(rules)
                firing_rules.append(rules)
            elif re.search('block', rules[0]):
                for target in rules[1:]:
                    self.parsed[target]['_blocking'].append(list(blocking_rules))
            elif re.search('add', rules[0]):

                for target in rules[1:]:
                    self.parsed[target]['_conditions'].append(list(firing_rules))
        firing_rules.clear()
        blocking_rules.clear()

    def create_triggers_index_list(self) -> list:
        triggers = []

        for tag in self.parsed:
            tag_name = tag['function']

            if tag_name in triggers_index:
                index = triggers_index[tag_name]

                tag.update(index)

                triggers.append(tag)

        return triggers

    # TODO Analyze the logic and redo
    def create_trigger_container(self) -> list:
        predicates = self.predicates.parse().parsed
        triggers = self.create_triggers_index_list()

        # Variables needed when processing predicates containing trigger names but the firing conditions point to other
        #   predicates that eventually point to the right trigger.
        group_conditions = {'_group_trigger': list(), '_trigger': list()}
        is_group_predicate = False

        for idx, rule_set in enumerate(self.rules.parsed):
            _temp_dict = {'_conditions': list()}
            new_trigger = {'_conditions': list()}
            _trigger_index = {}

            for rule_idx, rule in enumerate(rule_set):
                condition = []
                if 'if' in rule:
                    for predicate_index in rule[1:]:
                        # Handles the assignment of the rule to the proper trigger that is referenced by its firing_id
                        #   in a regex variable
                        if self.determine_type(predicates[predicate_index]['arg1']) is re.Pattern:
                            is_group_predicate = True
                            group_conditions['_group_trigger'].append(
                                re.search(r'^\(\^\$\|\(\(\^\|,\)([0-9_]+)\(\$\|,\)\)\)$',
                                          predicates[predicate_index]['arg1']).group(1))
                            nested_rls = [rule]
                            group_conditions['_trigger'].append(nested_rls)

                        # Handle triggers that are not in tags, but in predicates, which are valid triggers
                        if predicates[predicate_index]['arg1'] in triggers_index:
                            _trigger_index = find_in_index(predicates[predicate_index]['arg1'], triggers_index)
                            condition.append(rule)

                            _temp_dict['_conditions'].append(condition)
                            _temp_dict['function'] = predicates[predicate_index]['arg1']
                            new_trigger = {**_temp_dict, **_trigger_index}

                            triggers.append(new_trigger)

                # basically handles if the conditional is "unless" in the rule
                elif 'block' not in rule and 'add' not in rule:
                    if is_group_predicate:
                        group_conditions['_trigger'][-1].append(rule)
                        is_group_predicate = False
                    nested = [rule]
                    new_trigger['_conditions'].append(nested)
                    triggers.append(new_trigger)

        # because the above algorith duplicates tags and associates rules only to '__tg'
        # tags this is needed to overwrite the conditions
        for trigger in triggers:
            if 'vtp_triggerIds' in trigger and trigger['vtp_uniqueTriggerId'] in group_conditions['_group_trigger']:
                index = group_conditions['_group_trigger'].index(trigger['vtp_uniqueTriggerId'])
                trigger['_conditions'].append(group_conditions['_trigger'][index])

            if 'vtp_firingId' in trigger:
                unique_firing_id = re.sub(r'([0-9]+)_[0-9]+_([0-9]+)', r'\1_\2', trigger['vtp_firingId'])

                for trig in triggers:
                    if 'vtp_uniqueTriggerId' in trig and trig['vtp_uniqueTriggerId'] == unique_firing_id:

                        # fixme this silently ignores the case in which the trigger does not contain an '_conditions'
                        #   key.
                        if '_conditions' in trigger:
                            trig['_conditions'] = trigger['_conditions']
                        else:
                            trig['_conditions'] = ''

                triggers.pop(triggers.index(trigger))

        return triggers

    def process_predicate_trigger(self, trigger_arg1: str) -> dict:
        """
        Find a trigger in the tags` section by its 'vtp_uniqueTriggerId` given in a predicates 'arg1' key.

        :param trigger_arg1: the ID of the trigger as defined in GTM (e.g. "(^$|((^|,)31742945_37($|,)))")
        :type trigger_arg1: string
        :return: matching tag dict
        :rtype: dict
        """

        # TODO does it need to run on the processed container?
        tag_list = self.parsed
        found_tag = []

        trigger_id = re.search(r'\(\^\$\|\(\(\^\|,\)([0-9_]+)\(\$\|,\)\)\)$', trigger_arg1).group(1)

        for tag in tag_list:
            if trigger_id in tag.values():
                found_tag.append(tag)

        return found_tag[0]

    def process_trigger_groups(self) -> Union[dict, str]:
        """
        Creates a dictionary with data regarding the existing trigger group triggers.
        It maps the triggers in a dictionary which is ordered and can be easily accessed

        :return: Trigger Group Container
        :rtype: dict
        """

        # all trigger groups are "__tg" but only one has a  unique firing ID
        # all child tag have triggers themselves which conditions actually further along point to another existing
        # trigger
        trigger_group = {'_group': [], '_group_members': [], '_triggers': []}

        for tag in self.parsed:

            if tag['function'] == '__tg' and 'vtp_triggerIds' in tag:

                if len(tag['vtp_triggerIds']) < 2:
                    return 'Empty trigger group'

                trigger_group['_group'].append(tag)
                tag_members = tag['vtp_triggerIds'][1:]

                for member in tag_members:
                    trigger_group['_group_members'].append(self.get_by_key_value(member, 'vtp_firingId'))
                    trigger_group['_triggers'].append(self.get_by_key_value(self._extract_trigger_id(member), 'vtp_uniqueTriggerId'))

        return trigger_group

    @staticmethod
    def _extract_trigger_id(trigger_id: str) -> str:
        """
        Extracts the 'vtp_uniqueTriggerId' from a 'vtp_firingId' found in a trigger group list

        :param trigger_id: any string like: '31742945_23_22'
        :type trigger_id: str
        :return: A unique trigger id like '31742945_22'
        :rtype: str
        """
        vtp_firing_id = trigger_id

        trigger_id = re.sub(r'([0-9]+)_[0-9]+_([0-9]+)', r'\1_\2', vtp_firing_id)

        return trigger_id


class GTMResourcePredicates(GTMResourceTemplate):

    def __init__(self, predicate_container: list, macro_container: GTMResourceMacros):
        super().__init__(predicate_container)
        self.macros = macro_container.parse()

    def add_index_data(self):

        index_details = {}

        for predicate in self.parsed:
            predicate_name = predicate['function']
            if predicate_name in evaluations_index:
                index_details = evaluations_index[predicate_name]

            predicate.update(**index_details)

        return self

    def parse(self):

        self.add_index_data()

        for predicate in self.parsed:
            predicate_evaluator = predicate['function']
            predicate['_evaluator'] = [evaluations_index[predicate_evaluator]['title'],
                                       evaluations_index[predicate_evaluator]['exportTitle']]

            predicate_evaluated = predicate['arg0']

            if isinstance(predicate_evaluated, list) and self.determine_type(predicate_evaluated) == 'macro':
                evaluation_predicate = self.macros.process_general_resource(predicate_evaluated)

                if evaluation_predicate is None:
                    macro_function_name = self.macros.get_by_index(predicate_evaluated[1])['function']
                    if 'cvt' in macro_function_name:
                        predicate_evaluated = macros_index['_custom_variable_template']['title']
                    else:
                        predicate_evaluated = macros_index[macro_function_name]['title']
                else:
                    predicate_evaluated = self.macros.process_general_resource(predicate_evaluated)

            predicate['_evaluated'] = predicate_evaluated

            predicate_against = predicate['arg1']

            try:
                predicate_against = dlvBuiltins_index[predicate_against]['title']
            except KeyError:
                predicate_against = predicate['arg1']

            predicate['_against'] = predicate_against

        return self


class GTMResourceRules(GTMResourceTemplate):

    def __init__(self, rule_container: list):
        super().__init__(rule_container)

    def get_by_key_value(self, *args, **kwargs):
        """
        The rule section if composed of nested lists and contains no JSON. Therefore, this is useless for this section
        """
        pass

    def add_index_data(self):
        """
        Rules have no index to add. They reference predicated and tags.
        :return:
        :rtype:
        """
        pass

    def parse(self):
        """
        All rule parsing is done to determine tag information.
        This processing has to be done when tag parsing is done.
        :return:
        :rtype:
        """
        pass




