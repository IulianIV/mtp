from __future__ import annotations

import itertools
from collections import OrderedDict
import json
import re
from copy import deepcopy
from typing import Generator, Callable, Union, Any, NewType, List
from itertools import islice

import requests

from app.manager.helpers import extract_trigger_id
from .index import evaluations_index, dlvBuiltins_index, macros_index, tags_index, \
    triggers_index, runtime_index, BinaryOperator, runtime_function_regex, Statement
from .utils import find_in_index, get_runtime_index, flatten_container

# FIXME MAJOR! All create_container_name() functions need to be evaluated and commented. The goal, eventually,
#   is to have their complexity reduced. Especially in the case of trigger and trigger_group_processing..
#   It is OK to have it complex if the JSON parsing itself is complex but a better, faster way to deal
#   with those has to be developed.


# TODO research ways or libraries for faster JSON parsing.
# TODO List storage in memory can be replaced with generators (?)

# TODO refactor the code by using ABC or Protocol and Dataclasses.
#   There should be a class GTM that holds the whole container, handles connection and other non-data related methods.
#   All other container sections should inherit from the GTM class
#       GTMMacros, GTMPredicates, GTMTags, GTMRules and so on, which themselves being so similar could inherit
#       from another class. This way the main class is not so cluttered.

# TODO Create a find_type(Union[section, container]) -> Union[builtin type, custom type]:
#  function that handles type definitions across all containers and sections.

GTM_URL_ROOT: str = 'https://www.googletagmanager.com/gtm.js?id='

ROOT = {
    'VERSION': 'version',
    'MACROS': 'macros',
    'TAGS': 'tags',
    'PREDICATES': 'predicates',
    'RULES': 'rules',
    'RUNTIME': 'runtime',
    'PERMISSIONS': 'permissions'
}

SECTIONS = [ROOT['VERSION'], ROOT['MACROS'],
            ROOT['TAGS'], ROOT['PREDICATES'], ROOT['RULES'],
            ROOT['RUNTIME'], ROOT['PERMISSIONS']]

Template = NewType('RuntimeTemplate', List[Union[int, str, List]])


# decorator to validate if a given section is indeed a valid section
def check_for_container(method: Callable) -> Union[Callable, TypeError]:
    def wrapper(self, section: SECTIONS):
        if section in SECTIONS:
            return method(self, section)
        else:
            raise IndexError(f'Not in sections list. Accepted sections are: {SECTIONS}')

    return wrapper


class GTMIntel(object):

    def __init__(self, container_id: str, first_load: bool = False, container_data=None):

        self._id = container_id

        if first_load:
            # _full_container also hold 'resource' and 'runtime' data
            self._original_container = self.container_to_json()
        elif not first_load:
            self._original_container = self.saved_container_to_json(container_data)

        # the preserve the integrity of the original container, we will be working on a copy.
        self._working_container = deepcopy(self._original_container)
        # _usable_container only hold 'version' and literal container data ('macros', 'tags', 'predicates', 'rules')
        self._resource_container = self._working_container[self.container_resource_section]
        self.runtime_container = self._working_container[self.container_runtime_section]

    @check_for_container
    def resource_section_contents(self, section: list) -> Union[str, Generator]:
        """
        Get the content of the given section

        :param section: 'predicates' or 'tags' etc. # noinspection SpellCheckingInspection
        :return: Section contents
        """

        resource_section = self._resource_container[section]

        return resource_section

    def container_to_json(self) -> dict:
        """
        Fetches the contents of a given GTM ID by building its URL.

        :return: Container Data in JSON format
        """
        container_exp = r'var data = ({[\u0000-\uffff]*?});\n[\t-\r \xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]'
        req = requests.get(self.url)
        raw_data = req.content.decode('utf-8')

        container_data = re.search(container_exp, raw_data, re.IGNORECASE).group(1)

        container_json = json.loads(container_data)

        return container_json

    @staticmethod
    def saved_container_to_json(container_data) -> dict:
        """
        Function that is used to convert container data into JSON format. Primarily used in reading the data
        from the database
        
        :param container_data: literal container data
        :type container_data: dict
        :return: container JSON
        :rtype: JSON
        """

        container_data = container_data.decode('utf-8')

        container_json = json.loads(container_data)

        return container_json

    def find_container(self, website_url: str):
        """
        Function which will be using the 'seeker' module to attempt to automatically find
        a given websites GTM Container ID for analysis

        :param website_url:
        :return: Container ID
        """
        pass

    @staticmethod
    def count_items(container):
        function_list = []
        for item in container:
            if 'function' in item:
                function_list.append(item['function'])

        count = len(function_list)

        return count

    @property
    def id(self) -> str:
        """
        Returns the ID of the container.
        :return: Container ID
        :rtype: str
        """
        return self._id

    @property
    def url(self) -> str:
        """
        Return the URL of the container
        :return: Container URL
        :rtype: str
        """
        url = GTM_URL_ROOT + self._id
        return url

    @property
    def working_container(self) -> dict:
        """
        The whole container
        :return: The whole container
        :rtype: dict
        """
        return self._working_container

    @property
    def container_resource_section(self):
        """
        References the 'resource' part of the container

        :return: 'resource' contents
        """

        resource: list = list(self._working_container.keys())[0]

        return resource

    @property
    def container_runtime_section(self):
        """
        References the 'runtime' part of the container

        :return: 'runtime' section
        """

        if 'runtime' in list(self._working_container.keys()):
            return list(self._working_container.keys())[1]
        else:
            return 'runtime section missing from selected container'

    @property
    def original_container(self) -> dict:
        """
        All modifications are done on a deepcopy() of the original to avoid data corruption.
        Also, to be able, in the future, to process different types of data.
        This returns the original, non-modified container.
        :return: Original container
        :rtype: dict 
        """
        return self._original_container

    @property
    def resource_container(self):
        """
        Returns the contents of the 'resources' section
        :return: 'resources' container section
        :rtype: dict
        """
        return self._resource_container

    @property
    def version(self) -> str:
        """
        Returns the version of the container
        :return: container version
        :rtype: str
        """

        version = self.resource_section_contents(ROOT['VERSION'])

        return version

    @property
    def macros(self) -> list:
        """
        Returns the macros' section of the container
        :return: macros section
        :rtype: dict
        """

        macros = self.resource_section_contents('macros')

        return macros

    @property
    def macro_names(self) -> Generator:
        return (macro['function'] for macro in self.macros)

    @property
    def predicates(self) -> list:
        """
        Returns the predicates' section of the container
        :return:
        :rtype:
        """
        predicates = self.resource_section_contents('predicates')

        return predicates

    @property
    def rules(self) -> list:
        """
        Returns the rules' section of the container
        :return:
        :rtype:
        """

        rules = self.resource_section_contents('rules')

        return rules

    @property
    def tags(self) -> list:
        """
        Returns the tags' section of the container
        :return:
        :rtype:
        """
        tags = self.resource_section_contents('tags')

        return tags

    @property
    def tag_names(self) -> Generator:
        return (tag['function'] for tag in self.tags)

    @property
    def runtime(self) -> list:
        runtime = self.runtime_container

        return runtime

    @property
    def permissions(self) -> list:
        permissions = self.resource_section_contents('permissions')

        return permissions

    def process_type(self, property_value):

        """
        Tries to determine the type of value a property has.
        This deprecates the need of functions such as "_is_macro"
        This done will remove the need for "type" checking at process function level.

        :param property_value: Any value of a property belonging to any section from the container
        :return: Parameter value GTMSpy type
        """

        real_type = type(property_value)

        # determines if type is bool
        if real_type is bool:
            return bool

        # determines if type is int
        if real_type is int:
            return int

        # determines multiple sequence types
        if real_type is list and len(property_value) >= 2:

            # determines if type is macro
            if property_value[0] == 'macro' and type(property_value[1]) is int:
                return 'macro'

            # determines if type is template
            if property_value[0] == 'template':
                return 'template'

            # determines if type is mapping
            if property_value[0] == 'list' and type(property_value[1]) is list and property_value[1][0] == 'map':
                return 'mapping'

            # determines if type is escape
            if property_value[0] == 'escape' and self.process_type(property_value[1]) == 'macro':
                return 'escape'

            # determines if type is gtm_firing_sequence
            if property_value[0] == 'list' and type(property_value[1]) is list and property_value[1][0] == 'tag':
                return 'sequence'

        # determines if type is map
        if real_type is list and len(property_value) == 1 and property_value[0] == 'map':
            return 'map'

        # determines if type is trigger_group
        if real_type is list and len(property_value) != 0 and property_value[0] == 'list':
            if len(property_value) == 1:
                return 'empty trigger group'
            elif len(property_value) >= 2 and type(property_value[1]) is str and '_' in property_value[1]:
                return 'trigger group'

        # determines multiple string types
        if real_type is str and re.match(r'^\(\^\$\|\(\(\^\|,\)[0-9_]+\(\$\|,\)\)\)$', property_value):
            return 'RegEx'

    def process_macro(self, macro):
        """
        Processes the given "macro" list and displays its contents.

        :param macro: ["macro", 5]
        :return: Container like object. Any given "macros" section value at the given macro index.
        """
        if self.process_type(macro) == 'macro':
            try:
                macro_literal = self.macros[macro[1]]
                return macro_literal
            except IndexError:
                return 'Provide a macro index that exists'

    def process_escape(self, escape):
        """
        Processes a list type and pretty prints it.
        Example: ["escape", ["macro", 24], 8, 16]

        :return:
        :rtype:
        """
        macro_index = escape[1][1]

        macros = self.macros
        macro = macros[macro_index]

        return macro

    def process_template(self, template):
        valid_type = self.process_type(template)
        new_string = ''

        if valid_type != 'template':
            return None

        if len(template) == 2:
            return template
        else:
            for x in range(1, len(template)):
                if self.process_type(template[x]) == 'escape':
                    escaped = self.process_escape(template[x])
                    new_string += str(escaped)

                new_string += template[x]
            return new_string

    def process_predicate(self, predicate_index, detailed=False):
        """
        Processes a predicate and displays it in a more user-friendly way.
        Still in development to also print the values in a computer friendly way.

        :param predicate_index: The index of a predicate from the "predicates" section
        :param detailed: Prints a detailed definition of the predicate
        :return: Predicate definition
        """
        eval_indexes = evaluations_index
        dlv_indexes = dlvBuiltins_index
        predicates = self.predicates

        try:
            predicate_evaluator = predicates[predicate_index]['function']
            predicate_evaluated = predicates[predicate_index]['arg0']
            predicate_against = predicates[predicate_index]['arg1']

            if not detailed:
                return f'Predicate index {predicate_index} states that {predicate_evaluated} should evaluate as ' \
                       f'"{predicate_evaluator}" against "{predicate_against}"'
            else:
                predicate_evaluator = [eval_indexes[predicate_evaluator]['title'],
                                       eval_indexes[predicate_evaluator]['exportTitle']]

                if self.process_type(predicate_evaluated) == 'macro':
                    predicate_evaluated = self.process_macro(predicate_evaluated)

                try:
                    predicate_against = dlv_indexes[predicate_against]['title']
                except KeyError:
                    predicate_against = predicates[predicate_index]['arg1']

                return f'Predicate index {predicate_index} states that \n{predicate_evaluated}\nshould evaluate as' \
                       f' {predicate_evaluator[0]} ({predicate_evaluator[1]}) against "{predicate_against}"'

        except IndexError:
            return 'Provide a predicate index that exists'

    # better-me For the sake of running functionality, this parses the tag container more or less than 3 times.
    #   its time complexity is a bitch. Try to refine the process and make it better/faster.
    def process_rules(self):
        """
        Processes the rules container and associates found rules to their respective tags.

        :return:
        :rtype:
        """
        process_container = self._resource_container

        tags = process_container['tags']
        rules = process_container['rules']

        # Needed for front-end processing.
        # In this case, eventually, the processing of the rules is better in a nested fashion
        # Nesting allows for rule "grouping"
        for tag in tags:
            tag['_conditions'] = list()
            tag['_blocking'] = list()

        conditions = []
        condition = []
        targets = []

        blocks = []
        block = []
        block_targets = []

        for rl_set, index in zip(rules, range(0, len(rules))):

            trigger_cond = re.compile('if|unless')

            # allows for easy determining the type of the rule
            rule_types = [x[0] for x in rl_set]

            # All the checks below are necessary.
            # Upon analysis, it was concluded that there are certain "types" of rules, defined by their members
            # the "members" are described by the conditionals below

            # Member 1 - if no "block" rule is found, it is automatically a "firing" tag
            if 'block' not in rule_types:
                for rls in rl_set:
                    if re.search(trigger_cond, rls[0]):
                        condition.append(rls)
                    elif re.search('add', rls[0]):
                        targets.append(rls)

                conditions.insert(index, list(condition))
                condition.clear()

            # Member 2 - if there is no "add" but there is "block" it means it is a "blocking" tag
            if 'block' in rule_types and 'add' not in rule_types:
                for rls in rl_set:
                    if re.search(trigger_cond, rls[0]):
                        block.append(rls)
                    elif re.search('block', rls[0]):
                        block_targets.append(rls)

                blocks.insert(index, list(block))
                block.clear()

            # Member 3 - If there is "add" and "block" it means the same rules are used as "firing" and "blocking"
            #   conditions
            if 'add' in rule_types and 'block' in rule_types:
                for rls in rl_set:
                    if re.search(trigger_cond, rls[0]):
                        block.append(rls)
                        condition.append(rls)
                    elif re.search('block', rls[0]):
                        block_targets.append(rls)
                    elif re.search('add', rls[0]):
                        targets.append(rls)

                blocks.insert(index, list(block))
                conditions.insert(index, list(condition))
                block.clear()
                condition.clear()

        # While the above conditionals map the firing, blocking and target conditionals
        #   The loops from below map the indexes to the right tags.
        for x in range(0, len(targets)):
            for tag_index in targets[x][1:]:
                tags[tag_index]['_conditions'].append(conditions[x])

        for _x in range(0, len(block_targets)):
            for _tag_index in block_targets[_x][1:]:
                tags[_tag_index]['_blocking'].append(blocks[_x])

        return process_container['tags']

    def process_mapping(self, container_mapping, process_macro=False, key_name=None, value_name=None):
        """
        Attempts to create a dictionary of "map" values of some properties
        It tries to automatically assign dict keys and values according to the container mapping
        If dict key and value are given it will attempt to find those keys in the mapping.

        :param container_mapping: The property value which needs to be processed
        :param process_macro: Whether to process macros
        :param key_name: Optional dict key
        :param value_name: Optional dict value
        :return: Dictionary containing a computer-friendly value mapping
        """

        useful_map = container_mapping[1:]
        map_dict = {}

        if key_name is None and value_name is None:
            key = 'key'
            value = 'value'
        else:
            key = key_name
            value = value_name

        for item in useful_map:
            index = useful_map.index(item)
            try:
                map_key = item.index(key) + 1
                map_value = item.index(value) + 1
            except ValueError:
                print('Seems like the list contains non-standard key-value naming.\n'
                      'Attempting to find naming...')
                if container_mapping[0] == 'list':
                    print('Seems to be a valid map. Continuing...')
                    key = container_mapping[index + 1][1]
                    value = container_mapping[index + 1][3]
                map_key = item.index(key) + 1
                map_value = item.index(value) + 1

            if process_macro and self.process_type(item[map_key]) == 'macro':
                proc_macro = self.process_macro(item[map_key])
                map_dict[f'{key}_{index}'] = proc_macro
            else:
                map_dict[f'{key}_{index}'] = item[map_key]

            if process_macro and self.process_type(item[map_value]) == 'macro':
                proc_macro = self.process_macro(item[map_value])
                map_dict[f'{value}_{index}'] = proc_macro
            else:
                map_dict[f'{value}_{index}'] = item[map_value]

        return map_dict

    def process_teardown_setup(self, tag):
        """
        Processes tag properties defined as: 'teardown_tags', 'setup_tags'. The structure is the same for both.
        setup_tags: ["list", ["tag", 7, 0]] or ["list", ["tag", 7, 1]]
        teardown_tags: ["list", ["tag", 8, 0]] or  ["list", ["tag", 8, 2]]

        setup_tags: basically says to fire a tag (tag index 7) BEFORE the current tag fires (at trigger time first
            trigger the mentioned tag, not the current one). If the second value is '1' it states that the current tag
            should not be fired if tag index 7 fails or is paused.
            If second value is '0' basically states to fire it regardless.
        teardown_tags: basically says to fire a tag (tag index 8) AFTER the current tag fires (right after triggering
            and firing the current trigger, fire the referenced tag). If the second value is '2' it states that the
            referenced tag should not be fired if the current tag fails or is paused.
            If second value is '0' basically states to fire it regardless

        :return:
        :rtype:
        """
        _sequence = {}
        tags = self.tags

        for key in tag:
            if self.process_type(tag[key]) == 'sequence':
                sequence_literal = tag[key][1]
                if key == 'setup_tags':
                    _sequence['before'] = tags[sequence_literal[1]]['function']
                    _sequence['before_index'] = sequence_literal[1]
                    if sequence_literal[2] == 0:
                        _sequence['before_conditional'] = False

                    if sequence_literal[2] == 1:
                        _sequence['before_conditional'] = True

                if key == 'teardown_tags':
                    _sequence['after'] = tags[sequence_literal[1]]['function']
                    _sequence['after_index'] = sequence_literal[1]
                    if sequence_literal[2] == 0:
                        _sequence['after_conditional'] = False

                    if sequence_literal[2] == 2:
                        _sequence['after_conditional'] = True

        return _sequence

    # TODO Finish this processing functionality
    def process_metadata(self):
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

    def process_predicate_trigger(self, trigger_arg1: str) -> dict:
        """
        Find a trigger in the tags` section by its 'vtp_uniqueTriggerId` given in a predicates 'arg1' key.

        :param trigger_arg1: the ID of the trigger as defined in GTM (e.g. "(^$|((^|,)31742945_37($|,)))")
        :type trigger_arg1: string
        :return: matching tag dict
        :rtype: dict
        """

        tag_list = self.tags
        found_tag = []

        trigger_id = re.search(r'\(\^\$\|\(\(\^\|,\)([0-9_]+)\(\$\|,\)\)\)$', trigger_arg1).group(1)

        for tag in tag_list:
            for key in tag.keys():
                if tag[key] == trigger_id:
                    found_tag.append(tag)

        return found_tag[0]

    # TODO have the possibility to only pass either key or value
    # better-me convert to generator
    def search_in_container(self, container: Union[str, dict], key: Union[str, int], value: Any) -> list:
        """
        Searches the given container for items that contain the given key, value pair

        :param container: GTM valid container e.g. 'predicates'
        :type container: str
        :param key: Key that might be found within the containers items
        :type key: str, int
        :param value: Value that is associated with key
        :type value: Any
        :return: The container item where the pair was found
        :rtype: dict
        """
        if type(container) is str:
            container = self._resource_container[container]

        found_item = []

        for item in container:
            if key in item and item[key] == value:
                found_item.append(item)

        return found_item

    def create_macro_container(self):
        """
        Processes and creates the variables container

        :return: Dictionary with variable values
        :rtype: dict
        """

        macros = []

        original_macros = self.macros

        for macro in original_macros:
            temp_dict = {}
            macro_name = macro['function']

            # Custom Variable Templates have custom naming, this makes it possible to see the custom variable contents
            if macro_name not in macros_index and 'cvt' in macro_name:
                index_details = macros_index['_custom_variable_template']
            elif 'vtp_name' in macro and macro['vtp_name'] in dlvBuiltins_index:
                index_details = dlvBuiltins_index[macro['vtp_name']]
            else:
                index_details = find_in_index(macro_name, macros_index)

            for key, value in macro.items():
                temp_dict[key] = value
                temp_dict = {**temp_dict, **index_details}

            macros.append(temp_dict)

        return macros

    def create_tag_container(self):
        """
        Creates the tag container for usage in front-end. Works directly onto the rule-tagged container

        :return: Tag processed container
        :rtype: dict
        """

        tags = []

        rules_tagged = self.process_rules()

        for tag in rules_tagged:
            temp_dict = {}
            tag_name = tag['function']
            temp_dict['_sequence'] = self.process_teardown_setup(tag)
            if tag_name in tags_index:
                index_details = find_in_index(tag_name, tags_index)
            # This makes sure that if the tag is a Custom Template Tag, the contents are still visible
            elif tag_name not in tags_index and 'cvt' in tag_name:
                index_details = tags_index['_custom_tag_template']
            else:
                index_details = {**tag}

            for key, value in tag.items():
                temp_dict[key] = value
                temp_dict = {**temp_dict, **index_details}

            tags.append(temp_dict)

        return tags

    def create_predicates_container(self):
        """
        Creates the predicate container

        :return: Predicate container and index details
        :rtype: dict
        """
        new_predicates = []

        predicates = self.predicates

        for pred in predicates:
            temp_dict = {}
            pred_index = find_in_index(pred['function'], evaluations_index)

            for key, value in pred.items():
                temp_dict[key] = value
                temp_dict = {**temp_dict, **pred_index}

            new_predicates.append(temp_dict)

        return new_predicates

    def create_trigger_container(self):
        """
        Processes the rules' container while passing predicate data to relevant tags then creates new tags from certain
            other predicates and allocates to the newly create tags already existing rules.

        :return: trigger container
        :rtype: dict
        """

        # This has to be done on a rule tagged container as well on a complete predicates container
        rule_tagged = self.process_rules()
        predicates = self.create_predicates_container()
        rules = self._resource_container['rules']
        triggers = []

        # First processes the standard tags and ads trigger index information
        for tag in rule_tagged:
            temp_dict = {}

            if tag['function'] in triggers_index:
                trigger_index = find_in_index(tag['function'], triggers_index)

                for key, value in tag.items():
                    temp_dict[key] = value
                    temp_dict = {**temp_dict, **trigger_index}

                triggers.append(temp_dict)

        # Variables needed when processing predicates containing trigger names but the firing conditions point to other
        #   predicates that eventually point to the right trigger.
        group_conditions = {'_group_trigger': list(), '_trigger': list()}
        is_group_predicate = False

        for rl_set, index in zip(rules, range(0, len(rules))):
            _temp_dict = {'_conditions': list()}
            _trigger_index = {}
            # fixme the way it is set right now leads to duplication of rules and "container summary" errors.
            new_trigger = {'_conditions': list()}

            # In this case the firing or blocking condition of the rule is irrelevant. It can only help at counting
            #   how many tags is the trigger assigned to
            for rls in rl_set:
                condition = []
                if 'if' in rls:
                    for predicate_index in rls[1:]:
                        # Handles the assignment of the rule to the proper trigger that is referenced by its firing_id
                        #   in a regex variable
                        if self.process_type(predicates[predicate_index]['arg1']) == 'RegEx':
                            is_group_predicate = True
                            group_conditions['_group_trigger'].append(
                                re.search(r'^\(\^\$\|\(\(\^\|,\)([0-9_]+)\(\$\|,\)\)\)$',
                                          predicates[predicate_index]['arg1']).group(1))
                            nested_rls = [rls]
                            group_conditions['_trigger'].append(nested_rls)

                        # Handle triggers that are not in tags, but in predicates, which are valid triggers
                        if predicates[predicate_index]['arg1'] in triggers_index:
                            _trigger_index = find_in_index(predicates[predicate_index]['arg1'], triggers_index)
                            condition.append(rls)

                            _temp_dict['_conditions'].append(condition)
                            _temp_dict['function'] = predicates[predicate_index]['arg1']
                            new_trigger = {**_temp_dict, **_trigger_index}

                            triggers.append(new_trigger)

                # basically handles if the conditional is "unless" in the rule
                elif 'block' not in rls and 'add' not in rls:
                    if is_group_predicate:
                        group_conditions['_trigger'][-1].append(rls)
                        is_group_predicate = False
                    nested = [rls]
                    new_trigger['_conditions'].append(nested)
                    triggers.append(new_trigger)

        # because the above algorith duplicates tags and associates rules only to '__tg'
        # tags this si needed to overwrite the conditions
        for trigger in triggers:
            if 'vtp_triggerIds' in trigger and trigger['vtp_uniqueTriggerId'] in group_conditions['_group_trigger']:
                index = group_conditions['_group_trigger'].index(trigger['vtp_uniqueTriggerId'])
                trigger['_conditions'].append(group_conditions['_trigger'][index])

            if 'vtp_firingId' in trigger:
                unique_firing_id = re.sub(r'([0-9]+)_[0-9]+_([0-9]+)', r'\1_\2', trigger['vtp_firingId'])

                for trig in triggers:
                    if 'vtp_uniqueTriggerId' in trig and trig['vtp_uniqueTriggerId'] == unique_firing_id:
                        trig['_conditions'] = trigger['_conditions']

                triggers.pop(triggers.index(trigger))

        return triggers

    def process_trigger_groups(self) -> Union[dict, str]:
        """
        Creates a dictionary with data regarding the existing trigger group triggers.
        It maps the triggers in a dictionary which is ordered and can be easily accessed

        :return: Trigger Group Container
        :rtype: dict
        """

        tags = self._resource_container['tags']

        # all trigger groups are "__tg" but only one has a  unique firing ID
        # all child tag have triggers themselves which conditions actually further along point to another existing
        # trigger
        trigger_group = {'_group': [], '_group_members': [], '_triggers': []}

        for tag in tags:

            if tag['function'] == '__tg' and 'vtp_triggerIds' in tag:

                if len(tag['vtp_triggerIds']) < 2:
                    return 'Empty trigger group'

                trigger_group['_group'].append(tag)
                tag_members = tag['vtp_triggerIds'][1:]

                for member in tag_members:
                    trigger_group['_group_members'].append(self.search_in_container('tags', 'vtp_firingId', member))
                    trigger_group['_triggers'].append(self.search_in_container('tags', 'vtp_uniqueTriggerId',
                                                                               extract_trigger_id(member)))

        return trigger_group

    @property
    def runtime_section(self) -> GTMRuntime:
        runtime = GTMRuntime(self.id, True)

        return runtime


class GTMRuntime(GTMIntel):

    def __init__(self, container_id: str, first_load: bool = False, container_data: Any = None):
        super().__init__(container_id=container_id, first_load=first_load, container_data=container_data)

    @property
    def templates(self) -> Generator:
        """
        :return: Creates a generator containing all found templates within the runtime section
        :rtype: Generator
        """
        templates_to_gen = (RuntimeTemplate(template) for template in self.runtime)

        return templates_to_gen

    @property
    def template_names(self) -> Generator:
        return (template.name for template in self.templates)



    @property
    def length(self):
        template_length = len(list(self.templates))

        return template_length

    def fetch_template(self, template_index: int) -> RuntimeTemplate:
        """
        Fetches a template from the available templates by their index
        :param template_index: index of template to return
        :type template_index: int
        :return: Returns a RuntimeTemplate object
        :rtype: RuntimeTemplate
        """
        template = next(islice(self.templates, template_index, None))

        return template


class RuntimeTemplate:
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
    def count_occurrences(self, index: int, count_all: bool = False, print_to_console: bool = True) -> Union[
        int, dict]:
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

    @staticmethod
    def get_arguments(container):
        return container[1:]

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

    @staticmethod
    def _sanitize_container_string(container_string: str) -> str:

        if isinstance(container_string, str):
            sanitized_string = re.sub(r';{2,}$', ';', container_string)
        else:
            return container_string

        return sanitized_string

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


    @staticmethod
    def parse_simple_statement(container):
        statement_string = get_runtime_index(container[0], 'symbol')

        return statement_string

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
