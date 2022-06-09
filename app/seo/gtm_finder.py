import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

url = 'https://rsge.ro/'


def basic_search(page_url: str, consent: bool = True, consent_cookie: dict = None):
    container_id = ''
    container_url = ''

    if consent and consent_cookie is None:
        print('Provide consent cookie to send to browser.')
    elif not consent and consent_cookie is not None:
        print('Can`t pass cookies when consent is false.')

    if not consent:
        request_page = requests.get(page_url)

    else:
        request_page = requests.get(page_url, cookies=consent_cookie)

    page_contents = request_page.content

    soup = BeautifulSoup(page_contents, 'html.parser')

    script_tags = soup.find_all('script', {'src': re.compile(r'.*')})

    print(script_tags)

    return container_url, container_id


def selenium_try(page_url):
    browser = webdriver.Chrome(ChromeDriverManager().install())
    browser.implicitly_wait(35)
    browser.get(page_url)
    browser.add_cookie({'name': 'cookies-accepted', 'value': '1'})
    browser.refresh()
    page = browser.page_source

    soup = BeautifulSoup(page, 'html.parser')

    script_tags = soup.find_all('script', {'src': re.compile(r'gtm\.js\?')})[0]['src']

    print(script_tags)


def easy_find(page_url: str):
    container_id = ''
    container_url = ''

    regexp: list = [r'googletagmanager', r'GTM\-[A-Z]+']

    r_url = re.compile(regexp[0])
    r_id = re.compile(regexp[1])

    request_page = requests.get(page_url)
    page_content = request_page.content

    soup = BeautifulSoup(page_content, 'html.parser')
    get_scripts = soup.find_all('script')

    get_url = list(filter(lambda s: re.match(regexp[0], s), get_scripts))

    print(get_url)


if __name__ == '__main__':
    easy_find(url)
