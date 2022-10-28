import json
import re
import requests
from typing import Union
from .index import runtime_index


def gtm_compare_get_version(gtm_id) -> int:

    container_exp = r'var data = ({[\u0000-\uffff]*?});\n[\t-\r \xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]'
    req = requests.get('https://www.googletagmanager.com/gtm.js?id=' + gtm_id)
    raw_data = req.content.decode('utf-8')

    container_data = re.search(container_exp, raw_data, re.IGNORECASE).group(1)

    container_json = json.loads(container_data)

    return container_json['resource']['version']


# better-me add fallback situations when there are no arguments given.
def find_in_index(value: str, index: dict) -> dict:
    """
    Attempts to find 'value' in 'index'.
    Considering that a container hold a lot of information, it is best to index items in dictionaries that
    hold other dictionaries as values, even in the case of single key-value pairs.
    Keeping this consistency avoids having to write exception cases.

    :param value: Dictionary key to look for
    :type value: string
    :param index: Dictionary to search into
    :type index: dictionary
    :return: Dictionary containing value data
    :rtype: dictionary
    """
    try:
        index[value]
    except KeyError:
        return {'title': ''}

    return index[value]


def get_runtime_index(index_value: Union[int, str], dict_key: str, full_index: bool = False):
    if full_index:
        return runtime_index[index_value]

    requested_value = runtime_index[index_value][dict_key]

    return requested_value


def flatten_container(container):
    """
    Flattens a nested list or tuple creating a generator object
    :param container: nested list
    :type container: list
    :return: flattened list generator
    :rtype: generator
    """
    for i in container:
        if isinstance(i, (list, tuple)):
            for j in flatten_container(i):
                yield j
        else:
            yield i
