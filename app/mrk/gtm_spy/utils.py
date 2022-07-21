import json
import re

import requests


def gtm_compare_get_version(gtm_id) -> int:

    container_exp = r'var data = ({[\u0000-\uffff]*?});[\t-\r \xA0\u1680\u2000-\u200A\u2028\u2029\u202F\u205F\u3000\uFEFF]'
    req = requests.get('https://www.googletagmanager.com/gtm.js?id=' + gtm_id)
    raw_data = req.content.decode('utf-8')

    container_data = re.search(container_exp, raw_data, re.IGNORECASE).group(1)

    container_json = json.loads(container_data)

    return container_json['resource']['version']
