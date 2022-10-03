import json
import os
import re
from copy import deepcopy
from typing import Generator, Callable, Union, Any

import requests

from app.manager.helpers import Config, extract_trigger_id
from .index import evaluations_index, dlvBuiltins_index, macros_index, tags_index, triggers_not_tags, triggers_index
from .utils import find_in_index

# FIXME MAJOR! All create_container_name() functions need to be evaluated and commented. The goal, eventually,
#   is to have their complexity reduced. Especially in the case of trigger and trigger_group_processing..
#   It is OK to have it complex if the JSON parsing itself is complex but a better, faster way to deal
#   with those has to be developed.

CONTAINER_SAVE_PATH: os.PathLike = Config.GTM_SPY_DOWNLOAD_PATH

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


# decorator to validate if a given section is indeed a valid section
def check_for_container(method: Callable) -> Union[Callable, TypeError]:
    def wrapper(self, section: SECTIONS):
        if section in SECTIONS:
            return method(self, section)
        else:
            raise IndexError(f'Not in sections list. Accepted sections are: {SECTIONS}')

    return wrapper


class GTMIntel(object):
    _root_path = CONTAINER_SAVE_PATH

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
        self._resource_container = self._working_container[self.container_root]

    @check_for_container
    def section_contents(self, section: list) -> Union[str, Generator]:
        """
        Get the content of the given section

        :param section: 'predicates' or 'tags' etc.
        :return: Section contents
        """

        container_section = self._resource_container[section]

        return container_section

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
        print(container)
        for item in container:
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
    def container_root(self):
        """
        References the 'resource' part of the container

        :return: 'resource' contents
        """

        root: str = list(self._working_container.keys())[0]

        return root

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

        version = self.section_contents(ROOT['VERSION'])

        return version

    @property
    def macros(self) -> list:
        """
        Returns the macros secton of the container
        :return: macros section
        :rtype: dict
        """

        macros = self.section_contents('macros')

        return macros

    @property
    def predicates(self) -> list:
        """
        Returns the predicates secton of the container
        :return:
        :rtype:
        """
        predicates = self.section_contents('predicates')

        return predicates

    @property
    def rules(self) -> list:
        """
        Returns the rules secton of the container
        :return:
        :rtype:
        """

        rules = self.section_contents('rules')

        return rules

    @property
    def tags(self) -> list:
        """
        Returns the tags secton of the container
        :return:
        :rtype:
        """
        tags = self.section_contents('tags')

        return tags

    @property
    def runtime(self) -> list:
        runtime = self.section_contents('runtime')

        return runtime

    @property
    def permissions(self) -> list:
        permissions = self.section_contents('permissions')

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
                            group_conditions['_group_trigger'].append(re.search(r'^\(\^\$\|\(\(\^\|,\)([0-9_]+)\(\$\|,\)\)\)$', predicates[predicate_index]['arg1']).group(1))
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
