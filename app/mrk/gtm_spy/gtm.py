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
from .index import evaluations_index, dlvBuiltins_index, macros_index, tags_index, triggers_not_tags, \
    triggers_index, runtime_index, UnaryOperator, BinaryOperator, TernaryOperator, Statement,\
    ValueStatement, PropertySetter, PropertyAccessor, Array
from .utils import find_in_index, get_runtime_index, flatten_container

# FIXME MAJOR! All create_container_name() functions need to be evaluated and commented. The goal, eventually,
#   is to have their complexity reduced. Especially in the case of trigger and trigger_group_processing..
#   It is OK to have it complex if the JSON parsing itself is complex but a better, faster way to deal
#   with those has to be developed.

# TODO Use generators wherever possible to make code more readable, fast and easier to manage
#   change the codebase for this. This might also save memory.
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

        :param section: 'predicates' or 'tags' etc.
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
        Returns the macros secton of the container
        :return: macros section
        :rtype: dict
        """

        macros = self.resource_section_contents('macros')

        return macros

    @property
    def predicates(self) -> list:
        """
        Returns the predicates secton of the container
        :return:
        :rtype:
        """
        predicates = self.resource_section_contents('predicates')

        return predicates

    @property
    def rules(self) -> list:
        """
        Returns the rules secton of the container
        :return:
        :rtype:
        """

        rules = self.resource_section_contents('rules')

        return rules

    @property
    def tags(self) -> list:
        """
        Returns the tags secton of the container
        :return:
        :rtype:
        """
        tags = self.resource_section_contents('tags')

        return tags

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

            trigg_cond = re.compile('if|unless')

            # allows for easy determining the type of the rule
            rule_types = [x[0] for x in rl_set]

            # All the checks below are necessary.
            # Upon analysis, it was concluded that there are certain "types" of rules, defined by their members
            # the "members" are described by the conditionals below

            # Member 1 - if no "block" rule is found, it is automatically a "firing" tag
            if 'block' not in rule_types:
                for rls in rl_set:
                    if re.search(trigg_cond, rls[0]):
                        condition.append(rls)
                    elif re.search('add', rls[0]):
                        targets.append(rls)

                conditions.insert(index, list(condition))
                condition.clear()

            # Member 2 - if there is no "add" but there is "block" it means it is a "blocking" tag
            if 'block' in rule_types and 'add' not in rule_types:
                for rls in rl_set:
                    if re.search(trigg_cond, rls[0]):
                        block.append(rls)
                    elif re.search('block', rls[0]):
                        block_targets.append(rls)

                blocks.insert(index, list(block))
                block.clear()

            # Member 3 - If there is "add" and "block" it means the same rules are used as "firing" and "blocking"
            #   conditions
            if 'add' in rule_types and 'block' in rule_types:
                for rls in rl_set:
                    if re.search(trigg_cond, rls[0]):
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

        It behaves as follows: if "include tag name" is checked it prints both last 2 values fot he list,
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

                        # Handles triggers that are not in tags, but in predicates, which are valid triggers
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
    def runtime_parser(self) -> GTMRuntime:
        runtime_template = GTMRuntime(self.id, True)

        return runtime_template


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
        stripped_template = self.contents[4:]

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

        for item in stripped_template:
            if isinstance(item, list) and item[0] == 50:
                cache[f'declared_function_{stripped_template.index(item) - 2}:'] = item[1]
                function_names.append(item[1])

        for item in self._find_nested_index_and_name(51, False):
            cache[f'assigned_function_{count}:'] = item
            count += 1
            function_names.append(item)

        if not member_list:
            return ((k, v) for (k, v) in cache.items())

        return (x for x in function_names)

    # better-me Here temporarily for test reasons
    # in production mode there should be no checking if the index is "3" or other values
    # it is like this to create index methods one by one
    def parse_line(self, test_line):

        def indexer(container):
            for idx, item in enumerate(container):
                if isinstance(item, int):
                    try:
                        index_method = get_runtime_index(item, 'method')
                        method_call = getattr(self, index_method)(container)
                        return method_call
                    except KeyError:
                        continue
                if isinstance(item, str) and container[0] == 'require':
                    index_method = get_runtime_index(container[0], 'method')
                    method_call = getattr(self, index_method)(container)
                    return method_call
                if isinstance(item, str) and item in self.functions:
                    return self.parse_function_call(item)
                elif isinstance(item, list):
                    try:
                        index_method = get_runtime_index(item[0], 'method')
                        method_call = getattr(self, index_method)(item)
                        return method_call
                    except KeyError:
                        continue

        return indexer(test_line)

    def parse(self):

        contents = self.contents

        self.parse_line(contents)

    # Treat property accessors differently if necessary, even though they are binary operators
    # Special treatments needs to be made if arg1 is evaluated as string but represents a function reference
    def parse_binary_operator(self, container) -> str:
        """
        Handles parsing of binary operators that take two operands as arguments (i.e. "+", "||", "==" etc.)
        :return: string representation of parsed operator
        :rtype: str
        """
        arg1 = container[1]
        arg2 = container[2]
        operator_symbol = get_runtime_index(container[0], 'symbol')
        container_string = ''

        # fix-me There is no semicolon here
        # if this check does not pass start evaluating what the next arguments are and their respective methods
        if isinstance(arg1, list) and isinstance(arg2, list):
            container_string = f'{self.parse_line(arg1)} {operator_symbol} {self.parse_line(arg2)}'
        # if arg1[0] == 15 and arg2[0] == 15:
        #     container_string = f'{arg1[1]} {operator_symbol} {arg2[1]}'
        elif isinstance(arg1, str):
            if isinstance(arg2, list):
                arg2 = self.parse_line(arg2)
                container_string = f'{arg1} {operator_symbol} {arg2}'
            elif isinstance(arg2, str):
                container_string = f'{arg1} {operator_symbol} "{arg2}"'
            elif isinstance(arg2, int):
                container_string = f'{arg1} {operator_symbol} {arg2}'


        return container_string

    @staticmethod
    def parse_unary_operator(container) -> str:
        """
        Handles parsing of unary operators "!", "~", "-" etc.
        :return: string representation of parsed operator
        :rtype: str
        """
        arguments = container[1]
        operator_symbol = get_runtime_index(container[0], 'symbol')

        if operator_symbol == 'typeof':
            container_string = f'{operator_symbol} {arguments}'
        else:
            container_string = f'{operator_symbol}{arguments}'

        return container_string

    def parse_method_accessor(self, container) -> str:

        raw_object = container[1]
        _object = ''

        if isinstance(raw_object, list):
            _object = self.parse_line(raw_object)

        _property = container[2]
        _method_arguments = container[3]
        arguments = []
        argument_string = ''

        if isinstance(_method_arguments, list):
            arguments = self.parse_line(_method_arguments)

        base_string = f'{_object}.{_property}('

        if len(arguments) == 1:
            argument_string += f'"{arguments[0]}"'
        else:
            for arg in arguments:
                argument_string += f'"{arg}",'

        if argument_string.endswith(','):
            argument_string = argument_string[:-1]

        container_string = base_string + argument_string + ');'

        return container_string

    def parse_array_literal(self, container) -> list:
        if len(container) == 1:
            return list()

        argument_list = []

        for argument in container[1:]:
            if isinstance(argument, list):
                raw_argument = self.parse_line(argument)
                argument_list.append(raw_argument)
            elif isinstance(argument, str):
                argument_list.append(argument)

        return argument_list

    def parse_key_value_object(self, container) -> dict:

        if len(container) == 1:
            return dict()

        argument_dict = {}

        for idx, argument in enumerate(container[1:]):
            if isinstance(argument, list):
                container[idx + 1] = self.parse_line(argument)

        dict_keys = container[1:][::2]
        dict_values = container[1:][1::2]

        for (k, v) in itertools.zip_longest(dict_keys, dict_values):
            argument_dict[k] = v

        return argument_dict

    @staticmethod
    def parse_value_reference(container) -> str:
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

        if container[0] == 52:
            value_type = 'const'

        if container[0] == 41:
            value_type = 'let'

        value_name = container[1]
        assignment = container[2]
        container_string = ''

        if isinstance(assignment, list):
            assignment_value = self.parse_line(assignment)
            container_string = f'{value_type} {value_name} = {assignment_value}'
        elif isinstance(assignment, str):
            container_string = f'{value_type} {value_name} = {assignment}'

        return container_string

    def parse_switch_statement(self, container):

        switch_identifier = ''

        # Parse the identifier - argument 1
        if isinstance(container[1], list):
            switch_identifier = self.parse_line(container[1])

        switch_head = f'switch ({switch_identifier}) {{\n'

        # parse through the argument declaration list - argument 2

        raw_switch_cases = self.get_arguments(container[2])
        parsed_cases = []

        for idx, argument in enumerate(raw_switch_cases):
            if isinstance(argument, list):
                parsed_cases.append(self.parse_line(argument))
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
                expression_string.append(self.parse_line(item))

        switch_statement_string = switch_head + ''.join(expression_string)

        for idx, arg in enumerate(parsed_cases):
            switch_statement_string = switch_statement_string.replace(f'%%%%{idx}', str(parsed_cases[idx]))

        # temporary replacement for the "default"
        switch_statement_string = re.sub(r" %%%%\d", "", switch_statement_string)
        switch_statement_string += '};'

        return switch_statement_string

    # parse the switch body arguments such as "case" or "default"
    def parse_switch_expressions(self, container):

        case_string = f'\t{get_runtime_index(container[0], "symbol")} %%%%{self.counter}:\n\t\t'
        self.counter += 1

        case_body = []

        for idx, item in enumerate(container[1:]):
            if isinstance(item, list):
                arguments = self.get_arguments(item)

                for arg in arguments:
                    case_body.append(self.parse_line(arg) + ';')

        case_body = '\n\t\t'.join(case_body) + '\n'

        switch_expression_body = case_string + case_body

        return switch_expression_body

    @staticmethod
    def get_arguments(container):
        return container[1:]

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
            return_string += self.parse_line(return_arguments)

        if isinstance(return_arguments, int):
            return_string += str(return_arguments)

        return_statement_literal = f'{return_statement_literal} {return_string};'

        return return_statement_literal

    @staticmethod
    def parse_function_call(function_name):
        return f'{function_name}()'

    def parse_defined_functions(self, container):
        function_name = container[1]
        function_arguments = self.get_arguments(container[2])
        function_body = container[3:]

        function_start_string = f'function {function_name}('
        function_body_string = ''

        for argument in function_arguments:
            if argument == function_arguments[-1]:
                function_start_string += f'{argument}'
            else:
                function_start_string += f'{argument}, '

        function_start_string += ') {\n\n'

        for part in function_body:
            if isinstance(part, list):
                function_body_string += '\t' + self.parse_line(part) + '\n'

        function_string = function_start_string + function_body_string + '\n}'

        return function_string

    def parse_return_multiple(self, container):
        multiple_returns = container[1:]
        return_literals = ''

        for idx, item in enumerate(multiple_returns):
            if idx == len(multiple_returns) - 1:
                if isinstance(item, list):
                    return_literals += f'{str(self.parse_line(item))}'
                else:
                    return_literals += f'{str(item)}'
            elif isinstance(item, list):
                return_literals += f'{str(self.parse_line(item))}, '

        return return_literals



