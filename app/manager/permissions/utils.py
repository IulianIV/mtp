from collections import defaultdict
from typing import Iterator
from app.manager.helpers import extract_nested_strings


# Converts a Werkzeug url_map to a user and computer friendly module mapping
def convert_url_map_to_module_map(url_map: Iterator, skip_list: list = None):

    if skip_list is None:
        skip_list = []

    rule_map = url_map

    module_map = defaultdict(list)

    for rule in rule_map:
        module = rule.endpoint
        split_module = module.split('.')

        if split_module[0] not in skip_list:
            # default dict is needed to seamlessly add multiple values to the same dictionary key
            module_map[split_module[0]].append([split_module[x] for x in range(1, len(split_module))])
        else:
            continue

    # because de defaultdict is initialized with a list, all previously appended members are nested.
    # this iteration flattens nested lists regardless of nesting depth
    for key, value in module_map.items():
        module_map[key] = extract_nested_strings(value)

    return module_map