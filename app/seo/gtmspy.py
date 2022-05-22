import json
import os
from os import PathLike
from typing import Union, Generator, List, Callable

import requests

from app.manager.helpers import Config

CONTAINER_ID: str = 'id'
CONTAINER_URL: str = 'url'
CONTAINER_VERSION: str = 'version'
CONTAINER_MACROS: str = 'macros'
CONTAINER_TAGS: str = 'tags'
CONTAINER_PREDICATES: str = 'predicates'
CONTAINER_RULES: str = 'rules'

CONTAINER_SECTIONS: List[str] = [CONTAINER_ID, CONTAINER_URL, CONTAINER_VERSION, CONTAINER_MACROS,
                                 CONTAINER_TAGS, CONTAINER_PREDICATES, CONTAINER_RULES]

CONTAINER_SAVE_PATH: PathLike = Config.GTM_SPY_DOWNLOAD_PATH

GTM_ROOT = 'https://www.googletagmanager.com/gtm.js?id='


def check_for_container(method: Callable):
    def wrapper(self, section):
        if section in CONTAINER_SECTIONS:
            return method(self, section)
        else:
            raise TypeError(f'Not in sections list. Accepted sections are: {CONTAINER_SECTIONS}')

    return wrapper


class GTMSpy(object):

    def __init__(self, container_id: str):
        self._root_path = CONTAINER_SAVE_PATH
        self._id = container_id
        self._url = GTM_ROOT + container_id
        self._full_container: dict = self.container_to_json()
        self._root_property: str = list(self._full_container.keys())[0]
        self._usable_container: dict = self._full_container[self._root_property]
        self._version: str = self.version
        self._macros: Union[str, Generator] = self.macros
        self._tags: Union[str, Generator] = self.tags
        self._predicates: Union[str, Generator] = self.predicates
        self._rules: Union[str, Generator] = self.rules

    # checks for the existence of a GTM Script
    @staticmethod
    def check_for_script(container_id: str) -> Union[bool, str]:
        local_script_filename = os.path.join(CONTAINER_SAVE_PATH, container_id + '.js')

        if os.path.exists(local_script_filename):
            print('GTM Script for given ID already exists.')
            return True
        else:
            print('Given script ID is not present in root folder. Attempting download...')
            return GTMSpy.download_gtm_container_from_url(CONTAINER_SAVE_PATH, container_id)

    # downloads a gtm script by giving a GTM Container ID
    @staticmethod
    def download_gtm_container_from_url(file_path: os.PathLike, container_id: str) -> str:
        local_filename = os.path.join(file_path, container_id + ".js")

        script_url = GTM_ROOT + container_id
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
    def get_existing_gtm_script(container_id) -> Union[PathLike, str]:
        if GTMSpy.check_for_script(container_id):
            return os.path.join(CONTAINER_SAVE_PATH, container_id + '.js')
        else:
            return 'This container script was not found. Maybe download it?..'

    def get_functions(self, container_section: Generator) -> List:
        functions = []
        iter_arg = iter(container_section)

        while True:
            try:
                function = next(iter_arg)
                functions.append(function['function'])
            except StopIteration:
                break
        return functions

    @check_for_container
    def container_info(self, section: CONTAINER_SECTIONS) -> Union[str, Generator]:

        container_section = self._usable_container[section]

        return container_section

    def container_to_json(self) -> Union[dict, str]:

        with open(self.get_existing_gtm_script(self._id)) as container_script:

            data = container_script.read()

            container_data = data[data.find('var data = {'):data.find('/*')]
            container_data = container_data[container_data.find('{'):container_data.rfind('}')+1]

            container_json = json.loads(container_data)

            return container_json

    @property
    def id(self):
        return self._id

    @property
    def url(self):
        return self._url

    @property
    def full_container(self):
        return self._full_container

    @property
    def root_property(self):
        return self._root_property

    @property
    def container(self):
        return self._usable_container

    @property
    def version(self):
        self._version = self.container_info('version')

        return self._version

    @property
    def macros(self):
        self._macros = self.container_info('macros')

        return self._macros

    @property
    def predicates(self):
        self._predicates = self.container_info('predicates')

        return self._predicates

    @property
    def rules(self):
        self._rules = self.container_info('rules')

        return self._rules

    @property
    def tags(self):
        self._tags = self.container_info('tags')

        return self._tags

    def __repr__(self):
        return f'====== GTM SPY OBJECT ======\n' \
               f'Container ID: {self._id}\n' \
               f'Container URL: {self._url}\n'
