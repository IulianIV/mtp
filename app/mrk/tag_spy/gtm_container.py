from __future__ import annotations
import itertools
from typing import Union, Generator
from copy import deepcopy
from .index import GTMRootKeys, GTMResourceKeys
from .connectors import GTMConnector
from .gtm_resources import GTMResourcePredicates, GTMResourceRules, GTMResourceTags, GTMResourceMacros
from .gtm_template import GTMRuntimeTemplate


class GTMContainer:

    def __init__(self, container_id: str, first_load: bool = False, container_data=None):
        connector = GTMConnector(container_id, first_load, container_data)

        self._id = connector.id
        self._url = connector.url

        self._original_container = connector.original_container

        self._working_container = deepcopy(self._original_container)

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
    def working_container(self) -> dict:
        """
        The whole container
        :return: The whole container
        :rtype: dict
        """
        return self._working_container

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
        return self._url

    @property
    def version(self) -> str:
        """
        Returns the version of the container
        :return: container version
        :rtype: str
        """
        return self._working_container[GTMRootKeys.RESOURCE.value][GTMResourceKeys.VERSION.value]

    @property
    def resource_section(self) -> GTMResource:
        """
        Returns the contents of the 'resources' section
        :return: 'resources' container section
        :rtype: dict
        """
        return GTMResource(self._working_container[GTMRootKeys.RESOURCE.value])

    @property
    def runtime(self) -> GTMRuntime:

        if GTMRootKeys.RUNTIME.value in self._working_container.keys():
            runtime = GTMRuntime(self._working_container[GTMRootKeys.RUNTIME.value])
        else:
            runtime = list()

        return runtime


class GTMResource(GTMContainer):

    def __init__(self, container_id: str, first_load: bool = False, container_data=None):
        super().__init__(container_id, first_load, container_data)
        self.resource_container = self.working_container[GTMRootKeys.RESOURCE.value]

    def _resource_section_contents(self, section: GTMResourceKeys) -> Union[str, list]:
        """
        Get the content of the given section

        :param section: 'predicates' or 'tags' etc. # noinspection SpellCheckingInspection
        :return: Section contents
        """
        resource_section = self.resource_container[section]

        return resource_section

    @property
    def _macro_list(self) -> list:
        macro_list = self._resource_section_contents(GTMResourceKeys.MACROS.value)

        return macro_list

    @property
    def _tag_list(self) -> list:
        tag_list = self._resource_section_contents(GTMResourceKeys.TAGS.value)

        return tag_list

    @property
    def _predicate_list(self) -> list:
        predicate_list = self._resource_section_contents(GTMResourceKeys.PREDICATES.value)

        return predicate_list

    @property
    def _rule_list(self) -> list:
        rule_list = self._resource_section_contents(GTMResourceKeys.RULES.value)

        return rule_list

    @property
    def macros(self) -> GTMResourceMacros:

        macro_generator = GTMResourceMacros(self._macro_list)

        return macro_generator

    @property
    def predicates(self) -> GTMResourcePredicates:

        predicates_gen = GTMResourcePredicates(self._predicate_list, self.macros)

        return predicates_gen

    @property
    def tags(self) -> GTMResourceTags:

        tags_gen = GTMResourceTags(self._tag_list, self.macros, self.rules, self.predicates)

        return tags_gen

    @property
    def rules(self) -> GTMResourceRules:

        rules_gen = GTMResourceRules(self._rule_list)

        return rules_gen


class GTMRuntime(GTMContainer):

    def __init__(self, container_id: str, first_load: bool = False, container_data=None):
        super().__init__(container_id, first_load, container_data)

        if GTMRootKeys.RUNTIME.value in self._working_container.keys():
            self.runtime_container = self._working_container[GTMRootKeys.RUNTIME.value]
        else:
            self.runtime_container = list()

    @property
    def templates(self) -> Generator:
        """
        :return: Creates a generator containing all found templates within the runtime section
        :rtype: Generator
        """
        templates_to_gen = (GTMRuntimeTemplate(template) for template in self.runtime_container)

        return templates_to_gen

    @property
    def template_names(self) -> Generator:
        return (template.name for template in self.templates)

    @property
    def length(self):
        template_length = len(list(self.templates))

        return template_length

    def fetch_template(self, template_index: int) -> GTMRuntimeTemplate:
        """
        Fetches a template from the available templates by their index
        :param template_index: index of template to return
        :type template_index: int
        :return: Returns a RuntimeTemplate object
        :rtype: GTMRuntimeTemplate
        """
        template = next(itertools.islice(self.templates, template_index, None))

        return template



