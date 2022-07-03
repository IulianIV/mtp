import copy
import json
import os
import re
from os import PathLike
from typing import Generator, Callable, Union, List, Set

import requests

from app.manager.errors import SectionIndexError
from app.manager.helpers import Config
from .index import evaluations_index, dlvBuiltins_index
from .types import (SECTIONS, CONTAINER_ID, CONTAINER, CONTAINER_VERSION, CONTAINER_SECTION_CONTENTS,
                    GTM_CONTAINER_URL, ROOT, ITEM_PROPERTY, SECTION_ITEM)

CONTAINER_SAVE_PATH: PathLike = Config.GTM_SPY_DOWNLOAD_PATH

GTM_URL_ROOT: str = 'https://www.googletagmanager.com/gtm.js?id='


# TODO All typing has to be refactored. Pay attention to typing hints on function arguments - they must hint
#   towards what type of data to give not what type is expected to find in the GTM Container. At function return
#   seems to be fine.
# fixme These need to be re-documented and re-defined or refactored to hint towards the correct functionality
#   At the moment it is not clear what each function does
#         get_section_properties_values()
#         available_item_properties()
#         get_section_properties()

def check_for_container(method: Callable) -> Union[Callable, TypeError]:
    def wrapper(self, section: SECTIONS):
        if section in SECTIONS:
            return method(self, section)
        else:
            raise SectionIndexError(f'Not in sections list. Accepted sections are: {SECTIONS}')

    return wrapper


class Container(object):
    _root_path = CONTAINER_SAVE_PATH

    def __init__(self, container_id: str, website: str = None):
        if website is None:
            self._id: CONTAINER_ID = container_id
            # _full_container also hold 'resource' and 'runtime' data
            self._full_container: CONTAINER = self.container_to_json()
            # _usable_container only hold 'version' and literal container data ('macros', 'tags', 'predicates', 'rules')
            self._usable_container: CONTAINER = self._full_container[self.container_root]
            self._version: CONTAINER_VERSION = self.version
        else:
            pass

    @staticmethod
    def check_for_script(container_id: CONTAINER_ID) -> Union[bool, str]:
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
            return Container.download_gtm_container_from_url(CONTAINER_SAVE_PATH, container_id)

    @staticmethod
    def download_gtm_container_from_url(file_path: os.PathLike, container_id: CONTAINER_ID) -> str:
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
    def get_existing_gtm_script(container_id: CONTAINER_ID) -> Union[PathLike, str]:
        """
        Finds the local file path from a given Container ID, if it exists.

        :param container_id: CONTAINER_ID string object
        :return: Pathlike container file location
        """
        if Container.check_for_script(container_id):
            return os.path.join(CONTAINER_SAVE_PATH, container_id + '.js')
        else:
            return 'This container script was not found. Maybe download it?..'


    # fixme Fix situations when an item does not contain given property.
    #   Basically fix "KeyError" errors. What to do when a section doesn't have that property at all?
    #   analyze this functionality
    @staticmethod
    def get_section_properties_values(container_section: CONTAINER_SECTION_CONTENTS,
                                      section_item_property: ITEM_PROPERTY) -> List:
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
    def available_item_properties(section_item: SECTION_ITEM) -> List[str]:
        """
        Creates a list of the available properties from a given section

        :param section_item: Literal item found within any given container section
        :return: List of available properties
        """

        properties = [key for key in section_item.keys()]

        return properties

    # fixme What happens when a List or empty section is passed?
    @staticmethod
    def get_section_properties(container_section: CONTAINER_SECTION_CONTENTS) -> Set:
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

    def find(self, container_section: CONTAINER_SECTION_CONTENTS):
        """
        Empty because it awaits development

        :param container_section:
        :return:
        """
        pass

    @check_for_container
    def section_contents(self, section: CONTAINER_SECTION_CONTENTS) -> Union[str, Generator]:
        """
        Get the content of the given section

        :param section: 'predicates' or 'tags'
        :return: Section contents
        """

        container_section = self._usable_container[section]

        return container_section

    def container_to_json(self) -> CONTAINER_SECTION_CONTENTS:
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
    def id(self) -> CONTAINER_ID:
        return self._id

    @property
    def url(self) -> GTM_CONTAINER_URL:
        url = GTM_URL_ROOT + self._id
        return url

    @property
    def full_container(self) -> CONTAINER:
        return self._full_container

    @property
    def container_root(self):
        """
        References the 'resource' part of the container

        :return: 'resource' contents
        """

        root: str = list(self._full_container.keys())[0]

        return root

    @property
    def container(self):
        return self._usable_container

    @property
    def version(self) -> CONTAINER_VERSION:

        self._version = self.section_contents(ROOT['VERSION'])

        return self._version

    @property
    def macros(self) -> CONTAINER_SECTION_CONTENTS:

        macros = self.section_contents('macros')

        return macros

    @property
    def predicates(self) -> CONTAINER_SECTION_CONTENTS:

        predicates = self.section_contents('predicates')

        return predicates

    @property
    def rules(self) -> CONTAINER_SECTION_CONTENTS:

        rules = self.section_contents('rules')

        return rules

    @property
    def tags(self) -> CONTAINER_SECTION_CONTENTS:
        tags = self.section_contents('tags')

        return tags

    @property
    def runtime(self) -> CONTAINER_SECTION_CONTENTS:
        runtime = self.section_contents('runtime')

        return runtime

    @property
    def permissions(self) -> CONTAINER_SECTION_CONTENTS:
        permissions = self.section_contents('permissions')

        return permissions

    def process_macro(self, macro):
        """
        Processes the given "macro" list and displays its contents.

        :param macro: ["macro", 5]
        :return: Container like object. Any given "macros" section value at the given macro index.
        """
        if self._is_macro(macro):
            try:
                macro_literal = self.macros[macro[1]]
                return macro_literal
            except IndexError:
                return 'Provide a macro index that exists'

    def _is_macro(self, macro):
        """
        Deprecation warning: This will be removed as soon as "process_type" is developed

        Determines whether a given property value is indeed a macro

        :param macro: ["macro", 5]
        :return: True or False if given data is a valid macro or not
        """
        if type(macro) is not list:
            return False
        if len(macro) < 2 or len(macro) > 2:
            return False
        elif macro[0] == 'macro' or macro[1] is int:
            return True
        else:
            try:
                _ = self.macros[macro[1]]
                return True
            except IndexError:
                return False

    # better-me To have this properly implemented several custom types would have to be created
    """
    This function would analyze and determine the type of such possbile parameters. This is a 
        non-exhaustive list:
            Type 1 :["list",
                       ["map", "keyz", "lookup_input", "value", "lookup_output"],
                       ["map", "keyd", "lookup_input", "value", ["macro", 5]],
                       ["map", "keyr", ["macro", 9], "value", "lookup_output"]
                       ]
            Type 2: ["list", "31742945_23_21", "31742945_23_22"]
            Type 3: ["list", ["tag", 0, 0]]
            Type 4: ["map"]
            Type 5: "\u003Cscript type="text/gtmscript"\u003Ewindow.$zopim|"
            Type 6: ["macro", 8]
            Type 7: bool, int, regular string
            Type 8: string with macros included
    """
    # fixme Not done. Has to be finished
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
            if property_value[0] == 'macro' and property_value[1] is int:
                return 'macro'

            # determines if type is template
            if property_value[0] == 'template':
                return 'template'

            # determines if type is mapping
            if property_value[0] == 'list' and property_value[1] is list and property_value[1][0] == 'map':
                return 'mapping'

            # determines if type is escape
            if property_value[0] == 'escape' and self.process_type(property_value[1]) == 'macro':
                return 'escape'

        # determines if type is map
        if real_type is list and len(property_value) == 1 and property_value[0] == 'map':
            return 'map'

        # determines if type is trigger_group
        if real_type is list and property_value[0] == 'list':
            if len(property_value) == 1:
                return 'empty trigger group'
            elif len(property_value) >= 2 and property_value[1] is str and '_' in property_value[1]:
                return 'trigger group'

        # determines multiple string types
        if real_type is str and re.match(r'^\(\^\$\|\(\(\^\|,\)[0-9_]+\(\$\|,\)\)\)$', property_value):
            return 'RegEx'

    def process_trigger_group(self, tag):
        """
        To be detailed. A rough detail on how it works can be found in UpNote and app.diagrams.net

        :return:
        """

        if 'vtp_triggerIds' in tag:
            if type(tag['vtp_triggerIds']) is list and len(tag['vtp_triggerIds']) > 1:
                print(tag)
            elif type(tag['vtp_triggerIds']) is list and len(tag['vtp_triggerIds']) == 1:
                return 'empty trigger group'

        return tag

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

                if self._is_macro(predicate_evaluated):
                    predicate_evaluated = self.process_macro(predicate_evaluated)

                try:
                    predicate_against = dlv_indexes[predicate_against]['title']
                except KeyError:
                    predicate_against = predicates[predicate_index]['arg1']

                return f'Predicate index {predicate_index} states that \n{predicate_evaluated}\nshould evaluate as' \
                       f' {predicate_evaluator[0]} ({predicate_evaluator[1]}) against "{predicate_against}"'

        except IndexError:
            return 'Provide a predicate index that exists'

    def process_rules(self):
        """
        Handles the assignment of the 'if', 'unless' and 'blocking' clauses
        to the tags referenced in the 'add' section of the 'rules' item.
        Creates a new 'tags' section that contains a '_conditions' item for every eligible tag.
        _conditions contains the literal rule found in 'rules' i.e. {['if', 2, 3], ['unless', 4, 5]}

        :return: A new tag section updated with triggering rules
        """
        process_container = copy.deepcopy(self._usable_container)

        popper = ['version', 'macros', 'predicates']

        for pop in popper:
            process_container.pop(pop)

        tags = process_container['tags']
        rules = process_container['rules']

        conditions = []
        condition = []
        targets = []

        for rl_set, index in zip(rules, range(0, len(rules))):
            for rls in rl_set:
                if re.search('if|unless', rls[0]):
                    condition.append(rls)
                else:
                    targets.append(rls)
            conditions.insert(index, list(condition))
            condition.clear()

        for x in range(0, len(targets)):
            for tag_index in targets[x][1:]:
                tags[tag_index]['_conditions'] = conditions[x]

        return process_container

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

            if process_macro and self._is_macro(item[map_key]):
                proc_macro = self.process_macro(item[map_key])
                map_dict[f'{key}_{index}'] = proc_macro
            else:
                map_dict[f'{key}_{index}'] = item[map_key]

            if process_macro and self._is_macro(item[map_value]):
                proc_macro = self.process_macro(item[map_value])
                map_dict[f'{value}_{index}'] = proc_macro
            else:
                map_dict[f'{value}_{index}'] = item[map_value]

        return map_dict

    def __str__(self):
        return \
            f'''
                ====== GTM CONTAINER ======
                Container ID: {self._id}
                Container version: {self._version}
                Container URL: {self.url}
                
                ==========================
                
                
            '''
