import json
import os
import re
from copy import deepcopy
from typing import Generator, Callable, Union, List, Set, Any

import requests

from app.manager.errors import SectionIndexError
from app.manager.helpers import Config, extract_trigger_id
from .index import evaluations_index, dlvBuiltins_index, macros_index, tags_index, triggers_not_tags, triggers_index
from .lurker import find_in_index

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


# fixme These need to be re-documented and re-defined or refactored to hint towards the correct functionality
#   At the moment it is not clear what each function does
#         get_section_properties_values()
#         available_item_properties()
#         get_section_properties()

# TODO This class only parses and returns raw GTM data, creates a final, structured and readable GTM container
#   which can be represented in the front-end
#   Another separate functionality has to be created that parses the final container against the index
#   to pretty print all data.

def check_for_container(method: Callable) -> Union[Callable, TypeError]:
    def wrapper(self, section: SECTIONS):
        if section in SECTIONS:
            return method(self, section)
        else:
            raise SectionIndexError(f'Not in sections list. Accepted sections are: {SECTIONS}')

    return wrapper


class GTMIntel(object):
    _root_path = CONTAINER_SAVE_PATH

    def __init__(self, container_id: str, website: str = None):
        if website is None:
            self._id = container_id
            # _full_container also hold 'resource' and 'runtime' data
            self._full_container = self.container_to_json()
            # the preserve the integrity of the original container, we will be working on a copy.
            self._working_container = deepcopy(self._full_container)
            # _usable_container only hold 'version' and literal container data ('macros', 'tags', 'predicates', 'rules')
            self._usable_container = self._working_container[self.container_root]
            self._version = self.version
        else:
            pass

    @staticmethod
    def check_for_script(container_id: str) -> Union[bool, str]:
        """
        Checks whether the given GTM Script ID is saved as a file in the root system path

        :param container_id: CONTAINER_ID like string: 'GTM-XXXXX'
        :return: True if exists or downloads the container if not found
        """
        local_script_filename = os.path.join(CONTAINER_SAVE_PATH, container_id + '.js')

        if os.path.exists(local_script_filename):
            print('GTM Script for given ID already exists.')
            return True
        else:
            print('Given script ID is not present in root folder. Attempting download...')
            return GTMIntel.download_gtm_container_from_url(CONTAINER_SAVE_PATH, container_id)

    @staticmethod
    def download_gtm_container_from_url(file_path: os.PathLike, container_id: str) -> str:
        """
        Downloads and saves a GTM Container in the given path.

        :param file_path: Pathlike object
        :param container_id: CONTAINER_ID string object
        :return: File name of the saved GTM Container
        """
        local_filename = os.path.join(file_path, container_id + ".js")

        script_url = GTM_URL_ROOT + container_id
        # NOTE the stream=True parameter below
        with requests.get(script_url, stream=True) as r:
            r.raise_for_status()
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)

        return local_filename

    @staticmethod
    def get_existing_gtm_script(container_id: str) -> Union[os.PathLike, str]:
        """
        Finds the local file path from a given Container ID, if it exists.

        :param container_id: CONTAINER_ID string object
        :return: Pathlike container file location
        """
        if GTMIntel.check_for_script(container_id):
            return os.path.join(CONTAINER_SAVE_PATH, container_id + '.js')
        else:
            return 'This container script was not found. Maybe download it?..'

    # fixme Fix situations when an item does not contain given property.
    #   Basically fix "KeyError" errors. What to do when a section doesn't have that property at all?
    #   analyze this functionality
    @staticmethod
    def get_section_properties_values(container_section: str,
                                      section_item_property: str) -> List:
        """
        From the given section name, creates a list of all the values of the given property name

        :param container_section: 'tags' or 'predicates'
        :param section_item_property: 'function' or 'arg0'
        :return: List of property values
        """
        properties = list()
        iter_arg = iter(container_section)

        while True:
            try:
                item_property = next(iter_arg)
                properties.append(item_property[section_item_property])
            except StopIteration:
                break
        return properties

    # fixme What happens when a List or empty section is passed?
    @staticmethod
    def available_item_properties(section_item: str) -> List[str]:
        """
        Creates a list of the available properties from a given section

        :param section_item: Literal item found within any given container section
        :return: List of available properties
        """

        properties = [key for key in section_item.keys()]

        return properties

    # fixme What happens when a List or empty section is passed?
    @staticmethod
    def get_section_properties(container_section: str) -> Set:
        """
        When a certain code smell will be fixed this will be detailed

        :param container_section:
        :return:
        """
        overall_properties = list()

        for item in container_section:
            for key in item.keys():
                overall_properties.append(key)

        final_properties = set(overall_properties)

        return final_properties

    def find(self, container_section: list):
        """
        Empty because it awaits development

        :param container_section:
        :return:
        """
        pass

    @check_for_container
    def section_contents(self, section: list) -> Union[str, Generator]:
        """
        Get the content of the given section

        :param section: 'predicates' or 'tags'
        :return: Section contents
        """

        container_section = self._usable_container[section]

        return container_section

    def container_to_json(self) -> dict:
        """
        Converts a given container to JSON

        :return: Computer friendly container data
        """

        with open(self.get_existing_gtm_script(self._id)) as container_script:
            data = container_script.read()

            container_data = data[data.find('var data = {'):data.find('/*')]
            container_data = container_data[container_data.find('{'):container_data.rfind('}') + 1]

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

    @property
    def id(self) -> str:
        return self._id

    @property
    def url(self) -> str:
        url = GTM_URL_ROOT + self._id
        return url

    @property
    def full_container(self) -> dict:
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
    def container(self):
        return self._usable_container

    @property
    def version(self) -> str:

        self._version = self.section_contents(ROOT['VERSION'])

        return self._version

    @property
    def macros(self) -> list:

        macros = self.section_contents('macros')

        return macros

    @property
    def predicates(self) -> list:

        predicates = self.section_contents('predicates')

        return predicates

    @property
    def rules(self) -> list:

        rules = self.section_contents('rules')

        return rules

    @property
    def tags(self) -> list:
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
        process_container = self._usable_container

        tags = process_container['tags']
        rules = process_container['rules']

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

            rule_types = [x[0] for x in rl_set]

            if 'block' not in rule_types:
                for rls in rl_set:
                    if re.search(trigg_cond, rls[0]):
                        condition.append(rls)
                    elif re.search('add', rls[0]):
                        targets.append(rls)

                conditions.insert(index, list(condition))
                condition.clear()

            if 'block' in rule_types and 'add' not in rule_types:
                for rls in rl_set:
                    if re.search(trigg_cond, rls[0]):
                        block.append(rls)
                    elif re.search('block', rls[0]):
                        block_targets.append(rls)

                blocks.insert(index, list(block))
                block.clear()

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

    def process_trigger_groups(self) -> Union[dict, str]:

        tags = self._usable_container['tags']

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

    # TODO add an exception for non-dict container.
    # TODO have the possibility to only pass either key or value
    def search_in_container(self, container: str, key: Union[str, int], value: Any) -> list:
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

        container = self._usable_container[container]

        found_item = []

        for item in container:
            if key in item and item[key] == value:
                found_item.append(item)

        return found_item

    def create_macro_container(self):

        macros = []

        original_macros = self.macros

        for macro in original_macros:
            temp_dict = {}
            macro_name = macro['function']
            index_details = find_in_index(macro_name, macros_index)
            for key, value in macro.items():
                temp_dict[key] = value
                temp_dict = {**temp_dict, **index_details}

            macros.append(temp_dict)

        return macros

    def create_tag_container(self):

        tags = []

        rules_tagged = self.process_rules()

        for tag in rules_tagged:
            temp_dict = {}
            tag_name = tag['function']
            temp_dict['_sequence'] = self.process_teardown_setup(tag)
            if tag_name not in triggers_not_tags:
                index_details = find_in_index(tag_name, tags_index)

                for key, value in tag.items():
                    temp_dict[key] = value
                    temp_dict = {**temp_dict, **index_details}

                tags.append(temp_dict)

        return tags

    def create_predicates_container(self):
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

        rule_tagged = self.process_rules()
        predicates = self.create_predicates_container()
        triggers = []

        for tag in rule_tagged:
            temp_dict = {}
            if tag['function'] in triggers_index:
                trigger_index = find_in_index(tag['function'], triggers_index)

                for key, value in tag.items():
                    temp_dict[key] = value
                    temp_dict = {**temp_dict, **trigger_index}

                triggers.append(temp_dict)

        for predicate in predicates:
            temp_dict = {}

            if predicate['arg1'] in triggers_index:
                temp_dict['function'] = predicate['arg1']
                trigger_index = find_in_index(predicate['arg1'], triggers_index)

                triggers.append({**temp_dict, **trigger_index})

        return triggers

    def __str__(self):
        return \
            f'''
                ====== GTM CONTAINER ======
                Container ID: {self._id}
                Container version: {self._version}
                Container URL: {self.url}
                
                ==========================
                
                
            '''
