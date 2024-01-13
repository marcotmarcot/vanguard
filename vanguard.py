#!/usr/bin/env python3

import json
from urllib.request import urlopen

PRODUCT_CONSTANT_FIELDS = ["name", "managementType", "riskLevel", "ocfValue"]
CURRENCIES = {
    "EUR": 0.86,
    "GBP": 1,
    "USD": 0.79,
}


def pounds(values, currency: str):
    units = {
        " Billion": 1000,
        " Million": 1,
    }
    for value in values:
        for unit, multiplier in units.items():
            if value.endswith(unit):
                return float(value[:-len(unit)]) * multiplier * CURRENCIES[currency]
    raise f"Unknown units: {values}"


def average_return(returns: list):
    total = 1.0
    for ret in reversed(returns):
        total *= 1 + ret["monthPercent"] / 100
    return total ** (12 / len(returns)) - 1


def main():
    products = json.load(urlopen("https://www.vanguardinvestor.co.uk/api/productList"))
    products_by_name = {}
    for product in products:
        if "hedged" in product["id"]:
            continue
        name = product["name"]
        products = products_by_name.get(name, [])
        products.append(product)
        products_by_name[name] = products
    for name, products in products_by_name.items():
        if len(products) > 2:
            print(f"{name} contains {len(products)} products")
            exit(1)
        for i in range(1, len(products)):
            for field in PRODUCT_CONSTANT_FIELDS:
                if products[0][field] != products[i][field]:
                    print(f"{name}'s {field} is not consistent: {products}")
                    exit(1)
        assets = 0.0
        ret = 0.0
        ret_len = 0
        ticker = ""
        for product in products:
            try:
                fund = json.load(urlopen("https://www.vanguardinvestor.co.uk/api/funds/" + product["id"]))
                total_net_assets = fund["totalNetAssets"]
                assets += pounds([total_net_assets["value"], fund.get("totalAssets", "")], total_net_assets["currency"])
                returns = fund["fundData"]["annualNAVReturns"]["returns"]
                if len(returns) > ret_len:
                    ret = average_return(returns)
                if ticker == "" or product.get("shareClassCode", "") == "ACCM":
                    ticker = fund["ticker"]
            except Exception as e:
                print(product["id"])
                raise e
        product = products[0]
        print(f"{product['name']}\t{ticker}\t{product['riskLevel']}\t{product['ocfValue']}%\t{assets}\t" +
              f"{product['managementType']}\t{ret}%")


if __name__ == "__main__":
    main()
