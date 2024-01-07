#!/usr/bin/env python3

import json
from urllib.request import urlopen

PRODUCT_CONSTANT_FIELDS = ["name", "managementType", "riskLevel"]
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
    return total ** (12 / len(returns))


def main():
    products = json.load(urlopen("https://www.vanguardinvestor.co.uk/api/productList"))
    products_by_name = {}
    for product in products:
        name = product["name"]
        products = products_by_name.get(name, [])
        products.append(product)
        products_by_name[name] = products
    for name, products in products_by_name.items():
        for i in range(1, len(products)):
            for field in PRODUCT_CONSTANT_FIELDS:
                if products[0][field] != products[i][field]:
                    print(f"{name}'s {field} is not consistent: {products}")
                    exit(1)
        assets = 0.0
        ret = 0.0
        ret_len = 0
        for product in products:
            try:
                fund = json.load(urlopen("https://www.vanguardinvestor.co.uk/api/funds/" + product["id"]))
                total_net_assets = fund["totalNetAssets"]
                assets += pounds([total_net_assets["value"], fund.get("totalAssets", "")], total_net_assets["currency"])
                returns = fund["fundData"]["annualNAVReturns"]["returns"]
                if len(returns) > ret_len:
                    ret = average_return(returns)
            except Exception as e:
                print(product["id"])
                raise e
        for field in PRODUCT_CONSTANT_FIELDS:
            print(products[0][field], end="\t")
        print(f"{assets}\t{ret}")


if __name__ == "__main__":
    main()
