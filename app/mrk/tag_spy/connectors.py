from __future__ import annotations

import json
import re

import requests

from .index import GTMRootKeys


class GTMConnector(object):

    def __init__(self, container_id: str, first_load: bool = False, container_data=None):

        self._id = container_id
        self._container_data = container_data

        if first_load:
            # _full_container also hold 'resource' and 'runtime' data
            self._original_container = self.container_to_json()
        else:
            self._original_container = self.saved_container_to_json(self._container_data)

    def container_to_json(self) -> dict:
        """
        Fetches the contents of a given GTM ID by building its URL.

        :return: Container Data in JSON format
        """
        container_exp = r'var data = ({[\u0000-\uffff]*?});\n[\t-\r ' \
                        r'\xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]'
        req = requests.get(self.url)
        raw_data = req.content.decode('utf-8')

        container_data = re.search(container_exp, raw_data, re.IGNORECASE).group(1)

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
    def saved_container_to_json(container) -> dict:
        """
        Function that is used to convert container data into JSON format. Primarily used in reading the data
        from the database

        :param container: literal container data
        :type container: dict
        :return: container JSON
        :rtype: JSON
        """

        container_data = container.decode('utf-8')

        container_json = json.loads(container_data)

        return container_json

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
        url = GTMRootKeys.URL.value + self._id
        return url

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
