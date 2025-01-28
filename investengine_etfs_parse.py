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


def return_and_duration(max_first_date, daily):
    first = date_and_price(daily[0])
    first_for_average = None
    for day in daily:
        if day.get('date') < max_first_date:
            continue
        first_for_average = date_and_price(day)
        break
    last = date_and_price(daily[-1])
    years = (last[0] - first_for_average[0]).days / 365.25
    return ((last[1] / first_for_average[1]) ** (1 / years) - 1, (last[0] - first[0]).days)


def main():
    etfs = []
    max_first_date = '1000-01-01'
    for file in os.listdir(ETFS):
        etf = {}
        with open(os.path.join(ETFS, file), 'r', encoding='utf-8') as f:
            html = f.read()
        soup = BeautifulSoup(html, 'html.parser')
        script_tag = soup.find('script', {'id': '__NEXT_DATA__', 'type': 'application/json'})
        json_string = script_tag.string
        json_data = json.loads(json_string)
        security = json_data['props']['pageProps']['security']
        etf['title'] = security.get('title')
        etf['ticker'] = security.get('ticker')
        etf['ter'] = float(security.get('ter')) / 100
        properties = security['properties']
        etf['fund_size'] = properties.get('fund_size_mm')
        etf['share_class_size'] = properties.get('share_class_size_mm')
        etf['daily'] = security['history']['daily']
        first_date = etf['daily'][0].get('date')
        if first_date > max_first_date:
            max_first_date = first_date
        etfs.append(etf)

    for etf in etfs:
        (ret, days) = return_and_duration(max_first_date, etf['daily'])
        print(f'{etf["title"]}\t{etf["ticker"]}\t{etf["ter"]}\t{etf["fund_size"]}\t{etf["share_class_size"]}\t{ret}\t{days}')


if __name__ == "__main__":
    main()
