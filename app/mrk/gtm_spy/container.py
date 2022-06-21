import json
import os
from os import PathLike
from typing import Generator, Callable, Union, List, Set

import requests

from app.manager.errors import SectionIndexError
from app.manager.helpers import Config
from .types import (SECTIONS, CONTAINER_ID, CONTAINER, CONTAINER_VERSION, CONTAINER_SECTION_CONTENTS,
                    GTM_CONTAINER_URL, ROOT, ITEM_PROPERTY, SECTION_ITEM)

CONTAINER_SAVE_PATH: PathLike = Config.GTM_SPY_DOWNLOAD_PATH

GTM_URL_ROOT: str = 'https://www.googletagmanager.com/gtm.js?id='

# TODO All typing has to be refactored. Pay attention to typing hints on function arguments - they must hint
#   towards what type of data to give not what type is expected to find in the GTM Container. At function return
#   seems to be fine.


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
            self._full_container: CONTAINER = self.container_to_json()
            self._usable_container: CONTAINER = self._full_container[self.container_root]
            self._version: CONTAINER_VERSION = self.version
        else:
            pass

    # checks for the existence of a GTM Script
    @staticmethod
    def check_for_script(container_id: str) -> Union[bool, str]:
        local_script_filename = os.path.join(CONTAINER_SAVE_PATH, container_id + '.js')

        if os.path.exists(local_script_filename):
            print('GTM Script for given ID already exists.')
            return True
        else:
            print('Given script ID is not present in root folder. Attempting download...')
            return Container.download_gtm_container_from_url(CONTAINER_SAVE_PATH, container_id)

    # downloads a gtm script by giving a GTM Container ID
    @staticmethod
    def download_gtm_container_from_url(file_path: os.PathLike, container_id: CONTAINER_ID) -> str:
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

    # returns a path for an existing GTM script
    @staticmethod
    def get_existing_gtm_script(container_id: CONTAINER_ID) -> Union[PathLike, str]:
        if Container.check_for_script(container_id):
            return os.path.join(CONTAINER_SAVE_PATH, container_id + '.js')
        else:
            return 'This container script was not found. Maybe download it?..'

    # Creates a list from the given section of all the values found for key 'function'
    # fixme Fix situations when an item does not contain given property.
    #   Basically fix "KeyError" errors. What to do when a section doesn't have that property at all?
    #   analyze this functionality
    @staticmethod
    def get_section_properties_values(container_section: CONTAINER_SECTION_CONTENTS, section_item_property: ITEM_PROPERTY) -> List:
        properties = list()
        iter_arg = iter(container_section)

        while True:
            try:
                item_property = next(iter_arg)
                properties.append(item_property[section_item_property])
            except StopIteration:
                break
        return properties

    # Creates a list of the dictionary keys found within the given argument
    # fixme What happens when a List or empty section is passed?
    @staticmethod
    def available_item_properties(section_item: SECTION_ITEM) -> List[str]:

        properties = [key for key in section_item.keys()]

        return properties

    # fixme What happens when a List or empty section is passed?
    @staticmethod
    def get_section_properties(container_section: CONTAINER_SECTION_CONTENTS) -> Set:
        overall_properties = list()

        for item in container_section:
            for key in item.keys():
                overall_properties.append(key)

        final_properties = set(overall_properties)

        return final_properties

    def find(self, container_section: CONTAINER_SECTION_CONTENTS):
        pass

    @check_for_container
    def section_contents(self, section: CONTAINER_SECTION_CONTENTS) -> Union[str, Generator]:

        container_section = self._usable_container[section]

        return container_section

    def container_to_json(self) -> CONTAINER_SECTION_CONTENTS:

        with open(self.get_existing_gtm_script(self._id)) as container_script:
            data = container_script.read()

            container_data = data[data.find('var data = {'):data.find('/*')]
            container_data = container_data[container_data.find('{'):container_data.rfind('}') + 1]

            container_json = json.loads(container_data)

            return container_json

    def find_container(self, website_url: str):
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

    def __repr__(self):
        return \
            f'''
                ====== GTM CONTAINER ======
                Container ID: {self._id}
                Container version: {self._version}
                Container URL: {self.url}
                
                ==========================
                
                
            '''
