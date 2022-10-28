from __future__ import annotations
from typing import Generator, Union
from .index import GTMResourceKeys


class GTMResource:

    def __init__(self, resource_container: dict):
        self.resource_container = resource_container

    def _resource_section_contents(self, section: GTMResourceKeys) -> Union[str, list]:
        """
        Get the content of the given section

        :param section: 'predicates' or 'tags' etc. # noinspection SpellCheckingInspection
        :return: Section contents
        """

        resource_section = self.resource_container[section]

        return resource_section

    @property
    def version(self) -> str:
        version = self._resource_section_contents(GTMResourceKeys.VERSION.value)
        return version

    @property
    def macros(self) -> Generator[GTMResourceMacro]:
        macros = self._resource_section_contents(GTMResourceKeys.MACROS.value)

        macro_generator = (GTMResourceMacro(macro) for macro in macros)

        return macro_generator

    @property
    def predicates(self) -> Generator[GTMResourcePredicate]:
        predicates = self._resource_section_contents(GTMResourceKeys.PREDICATES.value)

        predicates_gen = (GTMResourcePredicate(predicate) for predicate in predicates)

        return predicates_gen

    @property
    def tags(self) -> Generator[GTMResourceTag]:
        tags = self._resource_section_contents(GTMResourceKeys.TAGS.value)

        tags_gen = (GTMResourceTag(tag) for tag in tags)

        return tags_gen

    @property
    def rules(self) -> Generator[GTMResourceRule]:
        rules = self._resource_section_contents(GTMResourceKeys.RULES.value)

        rules_gen = (GTMResourceRule(rule) for rule in rules)

        return rules_gen


class GTMResourceMacro(dict):

    def __init__(self, *args, **kwargs):
        super(GTMResourceMacro, self).__init__(*args, **kwargs)
        self.__dict__ = self


class GTMResourceTag(dict):

    def __init__(self, *args, **kwargs):
        super(GTMResourceTag, self).__init__(*args, **kwargs)
        self.__dict__ = self


class GTMResourcePredicate(dict):

    def __init__(self, *args, **kwargs):
        super(GTMResourcePredicate, self).__init__(*args, **kwargs)
        self.__dict__ = self


class GTMResourceRule(list):

    def __init__(self, *args, **kwargs):
        super(GTMResourceRule, self).__init__(*args, **kwargs)