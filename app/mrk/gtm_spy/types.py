from typing import Union, List, Sequence, Generator


CONTAINER = dict
CONTAINER_SECTIONS = List[str]
CONTAINER_SECTION_CONTENTS = Union[Generator, Sequence[List], List[Sequence[dict]], str]
NAME_INDEX = Union[dict, str]
CONTAINER_ID = str
CONTAINER_VERSION = str
GTM_CONTAINER_URL = str

ROOT: dict = {
    'VERSION': 'version',
    'MACROS': 'macros',
    'TAGS': 'tags',
    'PREDICATES': 'predicates',
    'RULES': 'rules',
    'RUNTIME': 'runtime',
    'PERMISSIONS': 'permissions'
}


SECTIONS: CONTAINER_SECTIONS = [ROOT['VERSION'], ROOT['MACROS'],
                                ROOT['TAGS'], ROOT['PREDICATES'], ROOT['RULES'],
                                ROOT['RUNTIME'], ROOT['PERMISSIONS']]

SECTION_ITEM = Union[dict, List]
ITEM_PROPERTY = Union[int, str, bool, List]
