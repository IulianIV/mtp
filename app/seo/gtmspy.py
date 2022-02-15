import json
from typing import Union, Generator

from app.manager.helpers import GTM_ROOT, get_existing_gtm_script


class GTMSpy:

    def __init__(self, container_id: str):

        self.gtm_container_id = container_id
        self.gtm_container_url = GTM_ROOT + container_id
        self.container_json: dict = self.container_to_json(pretty_print=False)
        self.version = self.container_version()

    def container_to_json(self, pretty_print: bool = True) -> Union[dict, str]:

        with open(get_existing_gtm_script(self.gtm_container_id)) as container_script:

            data = container_script.read()

            container_data = data[data.find('var data = {'):data.find('/*')]
            container_data = container_data[container_data.find('{'):container_data.rfind('}')+1]

            container_json = json.loads(container_data)

            if not pretty_print:
                return container_json
            else:
                pretty_printed = json.dumps(container_json, indent=4, sort_keys=True)

                return pretty_printed

    def container_version(self) -> str:

        version = self.container_json['resource']['version']

        return version

    # generates a list of dictionaries that contain GTM functions
    def macros(self) -> Generator:

        macro_list = self.container_json['resource']['macros']

        yield macro_list

    def tags(self) -> Generator:

        tag_list = self.container_json['resource']['tags']

        yield tag_list

    def predicates(self) -> Generator:

        predicates_list = self.container_json['resource']['predicates']

        yield predicates_list

    def rules(self) -> Generator:

        rules_list = self.container_json['resource']['rules']

        yield rules_list

    def __repr__(self):
        return f'====== GTM SPY OBJECT ======\n' \
               f'Container ID: {self.gtm_container_id}\n' \
               f'Container URL: {self.gtm_container_url}\n\n' \
               f'====== CONTAINER DATA ======\n' \
               f'Container has too much data to display correctly.\n' \
               f'Container version: {self.version}\n'
