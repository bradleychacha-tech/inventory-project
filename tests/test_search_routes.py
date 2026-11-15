# test_search_routes.py
# Tests for the routes that use the external API.
# We patch the functions inside app.py so no real request is made.

from unittest.mock import patch

import requests

from app import inventory

fake_product = {
    "barcode": "3017620422003",
    "product_name": "Nutella",
    "brands": "Ferrero",
    "ingredients_text": "Sugar, palm oil, hazelnuts"
}


# ---------- search by barcode ----------

@patch("app.get_product_by_barcode")
def test_search_barcode_found(mock_find, client):
    mock_find.return_value = fake_product

    response = client.get("/search/barcode/3017620422003")

    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Nutella"
    mock_find.assert_called_once_with("3017620422003")


@patch("app.get_product_by_barcode")
def test_search_barcode_not_found(mock_find, client):
    mock_find.return_value = None

    response = client.get("/search/barcode/0000")

    assert response.status_code == 404


@patch("app.get_product_by_barcode")
def test_search_barcode_api_down(mock_find, client):
    mock_find.side_effect = requests.exceptions.ConnectionError()

    response = client.get("/search/barcode/123")

    assert response.status_code == 502
    assert "error" in response.get_json()


# ---------- search by name ----------

@patch("app.get_product_by_name")
def test_search_name_found(mock_find, client):
    mock_find.return_value = fake_product

    response = client.get("/search/name?name=nutella")

    assert response.status_code == 200
    assert response.get_json()["brands"] == "Ferrero"
    mock_find.assert_called_once_with("nutella")


def test_search_name_missing(client):
    response = client.get("/search/name")
    assert response.status_code == 400


@patch("app.get_product_by_name")
def test_search_name_not_found(mock_find, client):
    mock_find.return_value = None

    response = client.get("/search/name?name=zzzz")

    assert response.status_code == 404


@patch("app.get_product_by_name")
def test_search_name_api_down(mock_find, client):
    mock_find.side_effect = requests.exceptions.Timeout()

    response = client.get("/search/name?name=nutella")

    assert response.status_code == 502


# ---------- import into inventory ----------

@patch("app.get_product_by_barcode")
def test_import_item(mock_find, client):
    mock_find.return_value = fake_product

    response = client.post("/inventory/import/3017620422003", json={"price": 6.5, "stock": 20})

    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] == 3
    assert data["product_name"] == "Nutella"
    assert data["price"] == 6.5
    assert data["stock"] == 20
    # it should really be saved in the array
    assert len(inventory) == 3


@patch("app.get_product_by_barcode")
def test_import_item_without_price_and_stock(mock_find, client):
    mock_find.return_value = fake_product

    response = client.post("/inventory/import/3017620422003")

    assert response.status_code == 201
    assert response.get_json()["price"] == 0
    assert response.get_json()["stock"] == 0


@patch("app.get_product_by_barcode")
def test_import_item_not_found(mock_find, client):
    mock_find.return_value = None

    response = client.post("/inventory/import/0000", json={"price": 1, "stock": 1})

    assert response.status_code == 404
    assert len(inventory) == 2


@patch("app.get_product_by_barcode")
def test_import_item_api_down(mock_find, client):
    mock_find.side_effect = requests.exceptions.ConnectionError()

    response = client.post("/inventory/import/123", json={"price": 1, "stock": 1})

    assert response.status_code == 502
    assert len(inventory) == 2


@patch("app.get_product_by_barcode")
def test_import_item_bad_price(mock_find, client):
    mock_find.return_value = fake_product

    response = client.post("/inventory/import/123", json={"price": "free", "stock": 1})

    assert response.status_code == 400
    assert len(inventory) == 2
