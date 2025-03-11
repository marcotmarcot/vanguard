#!/usr/bin/env python3

import json
import os
import re
from datetime import datetime
from urllib.request import urlretrieve
from bs4 import BeautifulSoup

ALL = 'investengine_all.html'
ETFS = 'investengine_etfs'


def date_and_price(day):
    return (datetime.strptime(day.get('date'), '%Y-%m-%d'), float(day.get('share_price')))


def return_and_duration(daily):
    first = date_and_price(daily[0])
    last = date_and_price(daily[-1])
    years = (last[0] - first[0]).days / 365.25
    return ((last[1] / first[1]) ** (1 / years) - 1, years)


def main():
    for file in os.listdir(ETFS):
        with open(os.path.join(ETFS, file), 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
        json_string = script_tag.string
        json_data = json.loads(json_string)
        security = json_data['props']['pageProps']['security']
        print(security.get('title'), end='\t')
        print(security.get('ticker'), end='\t')
        print(float(security.get('ter')) / 100, end='\t')
        properties = security['properties']
        print(properties.get('fund_size_mm'), end='\t')
        print(properties.get('share_class_size_mm'), end='\t')
        (ret, days) = return_and_duration(security['history']['daily'])
        print(ret, end='\t')
        print(days)


if __name__ == "__main__":
    main()
