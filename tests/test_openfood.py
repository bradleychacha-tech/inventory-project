# test_openfood.py
# Tests for openfood.py. We never call the real website,
# we use Mock to pretend the API answered.

from unittest.mock import Mock, patch

import pytest
import requests

from openfood import get_product_by_barcode, get_product_by_name


def fake_response(data):
    response = Mock()
    response.json.return_value = data
    return response


@patch("openfood.requests.get")
def test_barcode_found(mock_get):
    mock_get.return_value = fake_response({
        "status": 1,
        "product": {
            "product_name": "Organic Almond Milk",
            "brands": "Silk",
            "ingredients_text": "Filtered water, almonds, cane sugar"
        }
    })

    product = get_product_by_barcode("1234567890123")

    assert product["product_name"] == "Organic Almond Milk"
    assert product["brands"] == "Silk"
    assert product["barcode"] == "1234567890123"
    # check that the barcode was used in the url
    url = mock_get.call_args[0][0]
    assert "1234567890123" in url


@patch("openfood.requests.get")
def test_barcode_not_found(mock_get):
    mock_get.return_value = fake_response({"status": 0})

    assert get_product_by_barcode("0000") is None


@patch("openfood.requests.get")
def test_barcode_missing_fields_are_empty(mock_get):
    mock_get.return_value = fake_response({
        "status": 1,
        "product": {"product_name": "Plain Rice"}
    })

    product = get_product_by_barcode("5555")

    assert product["product_name"] == "Plain Rice"
    assert product["brands"] == ""
    assert product["ingredients_text"] == ""


@patch("openfood.requests.get")
def test_barcode_api_down(mock_get):
    mock_get.side_effect = requests.exceptions.ConnectionError()

    with pytest.raises(requests.exceptions.RequestException):
        get_product_by_barcode("1234567890123")


@patch("openfood.requests.get")
def test_name_found(mock_get):
    mock_get.return_value = fake_response({
        "products": [
            {
                "code": "3017620422003",
                "product_name": "Nutella",
                "brands": "Ferrero",
                "ingredients_text": "Sugar, palm oil, hazelnuts"
            }
        ]
    })

    product = get_product_by_name("nutella")

    assert product["barcode"] == "3017620422003"
    assert product["product_name"] == "Nutella"
    # check that the search word was sent
    params = mock_get.call_args[1]["params"]
    assert params["search_terms"] == "nutella"


@patch("openfood.requests.get")
def test_name_not_found(mock_get):
    mock_get.return_value = fake_response({"products": []})

    assert get_product_by_name("zzzzzz") is None


@patch("openfood.requests.get")
def test_name_api_down(mock_get):
    mock_get.side_effect = requests.exceptions.Timeout()

    with pytest.raises(requests.exceptions.RequestException):
        get_product_by_name("nutella")
