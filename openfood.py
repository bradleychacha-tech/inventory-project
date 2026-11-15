# openfood.py
# Functions that get product data from the OpenFoodFacts API.

import requests

BASE_URL = "https://world.openfoodfacts.org"

# OpenFoodFacts asks apps to say who they are
HEADERS = {"User-Agent": "InventoryLab/1.0 (student project)"}


def make_product(product, barcode):
    # keep only the fields we want to store
    return {
        "barcode": barcode,
        "product_name": product.get("product_name", ""),
        "brands": product.get("brands", ""),
        "ingredients_text": product.get("ingredients_text", "")
    }


def get_product_by_barcode(barcode):
    url = f"{BASE_URL}/api/v0/product/{barcode}.json"
    response = requests.get(url, headers=HEADERS, timeout=10)
    data = response.json()

    # status 1 means the product was found, 0 means not found
    if data.get("status") != 1:
        return None

    return make_product(data["product"], barcode)


def get_product_by_name(name):
    url = f"{BASE_URL}/cgi/search.pl"
    params = {
        "search_terms": name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1
    }
    response = requests.get(url, params=params, headers=HEADERS, timeout=10)
    data = response.json()

    products = data.get("products", [])
    if len(products) == 0:
        return None

    # we only take the first match
    first = products[0]
    return make_product(first, first.get("code", ""))