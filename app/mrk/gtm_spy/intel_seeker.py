import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

url = 'https://rsge.ro/'

URL = str


def tag_finder(website: URL) -> tuple:
    container_id = ''
    container_url = ''
    container_head = ''
    container_body = ''

    return container_id, container_url, container_head, container_body


def selenium_find_id(page_url):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.implicitly_wait(35)
    browser.get(page_url)
    browser.add_cookie({'name': 'cookies-accepted', 'value': '1'})
    browser.refresh()
    page = browser.page_source

    soup = BeautifulSoup(page, 'html.parser')
    script_tag_source = soup.find_all('script', {'src': re.compile(r'gtm\.js\?')})[0]['src']

    container_id = re.search(r'id=([A-Z-]+)', script_tag_source).group(1)

    return container_id


def easy_find_id(page_url: str):

    r_id = re.compile(r'GTM-[A-Z0-9]+')

    request_page = requests.get(page_url)
    page_content = request_page.content

    soup = BeautifulSoup(page_content, 'html.parser')
    find_scripts = soup.find_all('script')

    get_script = list(filter(lambda s: re.search(r_id, s.text), find_scripts))

    try:
        container_id = re.search(r_id, get_script[0].text).group()
    except IndexError:
        raise ConsentError('IndexError on script tag filtering. '
                           'Probabil Consent Blocked. Add consent cookies and try again.\n')

    return container_id


if __name__ == '__main__':
    gtm_id = selenium_find_id('https://rsge.ro/')
    print(gtm_id)
