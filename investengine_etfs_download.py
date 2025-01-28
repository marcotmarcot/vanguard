#!/usr/bin/env python3

import json
import os
import re
from urllib.request import urlretrieve
from bs4 import BeautifulSoup

ALL = 'investengine_all.html'
ETFS = 'investengine_etfs'


def main():
    with open(ALL, 'r', encoding='utf-8') as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
    json_string = script_tag.string
    json_data = json.loads(json_string)
    default_securities = json_data['props']['pageProps']['defaultSecurities']
    os.makedirs(ETFS)
    for security in default_securities:
        provider_filter_name = re.sub(r'\s+', '-',
            security
            .get('provider_filter_name')
            .lower()
            .replace('(', '')
            .replace(')', '')
            .replace('&', '')
            .replace('dws', '')
            .strip())
        ticker = security.get('ticker').lower()
        file = f'{ETFS}/{provider_filter_name}_{ticker}.html'
        print(file)
        urlretrieve(f'http://investengine.com/etfs/{provider_filter_name}/{ticker}', file)


if __name__ == "__main__":
    main()
