from __future__ import annotations
from typing import Any
from copy import deepcopy
from abc import ABC, abstractmethod
from .index import macros_index, tags_index, dlvBuiltins_index, evaluations_index, macro_data_keys

# TODO debate if it is necessary to create other classes for individual resource members (i.e. GTMResourceMacro)


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

    def get_by_index(self, index: int, original: bool = False):
        container = self.parsed

        if original:
            container = self.original

        return container[index]

    def get_by_key_value(self, value: Any, key: Any = None, original: bool = False):
        """
        Searches the given container for items that contain the given key, value pair.
        If only either of arguments is given, it will try to find the first value that contains the given arguments

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
                for (k, v) in item.items():
                    if item[k] == value:
                        return item
            else:
                if key in item and item[key] == value:
                    return item

    @abstractmethod
    def add_index_data(self):
        pass


class GTMResourceMacros(GTMResourceTemplate):

    def __init__(self, macro_container: list):
        super().__init__(macro_container)

    # better-me Find a way to parse the given macro if not already parsed. Parsing it should also modify in self.parsed
    #   if the macro is referenced in the original container DO NOT parse.
    def get_by_reference(self, macro_reference: list, original: bool = False) -> dict:
        """
        Find a macro value by reference `["macro", 6]`. If the referenced macro is not parsed, parse it and directly
        modify self.parsed.
        Ff the macro is referenced in the original container DO NOT parse.
        :param macro_reference: ["macro" 6]
        :type macro_reference: list
        :param original: If the original container should be read
        :type original: bool
        :return:
        :rtype:
        """
        container = self.parsed

        if original:
            container = self.original

        try:
            macro_literal = container[macro_reference[1]]
            return macro_literal
        except IndexError:
            return 'Given macro index parameter does not exist.'

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

        for macro in self.parsed:
            for key, value in macro.items():
                if isinstance(value, list):
                    value_type = self.determine_type(value)

                    if value_type == 'macro':
                        macro[key] = self.get_data_key(macro)
        return self

    @staticmethod
    def determine_type(resource_value: list):
        # determines if type is macro
        if resource_value[0] == 'macro' and isinstance(resource_value[1], int):
            return 'macro'

    # macros contain certain keys that are used as data referential (i.e. `vtp_name`)
    @staticmethod
    def get_data_key(macro: dict):

        for data in macro_data_keys:
            if data in macro:
                return macro[data]


class GTMResourceTags(GTMResourceTemplate):

    def __init__(self, tag_container: list):
        super().__init__(tag_container)

    def add_index_data(self):

        for tag in self.parsed:
            tag_name = tag['function']
            if tag_name in tags_index:
                index_details = tags_index[tag_name]
            # This makes sure that if the tag is a Custom Template Tag, the contents are still visible
            elif tag_name not in tags_index and 'cvt' in tag_name:
                index_details = tags_index['_custom_tag_template']

            tag.update(**index_details)

        return self


class GTMResourcePredicates(GTMResourceTemplate):

    def __init__(self, predicate_container: list):
        super().__init__(predicate_container)

    def add_index_data(self):

        for predicate in self.parsed:
            eval_name = predicate['function']
            index_details = evaluations_index[eval_name]
            predicate.update(**index_details)

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

