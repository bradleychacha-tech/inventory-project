# test_cli.py
# Tests for the CLI. We pretend the user types answers (patch input)
# and pretend the API answers (patch requests).

from unittest.mock import Mock, patch

import requests

import cli


def fake_response(data, status=200):
    response = Mock()
    response.status_code = status
    response.json.return_value = data
    return response


bread = {
    "id": 1,
    "barcode": "1111111111111",
    "product_name": "Brown Bread",
    "brands": "Festive",
    "ingredients_text": "Wheat flour, water, yeast, salt",
    "price": 1.5,
    "stock": 30
}


# ---------- view ----------

@patch("cli.requests.get")
def test_view_all(mock_get, capsys):
    mock_get.return_value = fake_response([bread])

    cli.view_all()

    output = capsys.readouterr().out
    assert "Brown Bread" in output
    assert "30" in output


@patch("cli.requests.get")
def test_view_all_empty(mock_get, capsys):
    mock_get.return_value = fake_response([])

    cli.view_all()

    assert "empty" in capsys.readouterr().out


@patch("builtins.input", side_effect=["1"])
@patch("cli.requests.get")
def test_view_one(mock_get, mock_input, capsys):
    mock_get.return_value = fake_response(bread)

    cli.view_one()

    assert mock_get.call_args[0][0].endswith("/inventory/1")
    assert "Wheat flour" in capsys.readouterr().out


@patch("builtins.input", side_effect=["99"])
@patch("cli.requests.get")
def test_view_one_not_found(mock_get, mock_input, capsys):
    mock_get.return_value = fake_response({"error": "Item not found"}, 404)

    cli.view_one()

    assert "Item not found" in capsys.readouterr().out


@patch("builtins.input", side_effect=["abc", "1"])
@patch("cli.requests.get")
def test_view_one_bad_id_asks_again(mock_get, mock_input, capsys):
    mock_get.return_value = fake_response(bread)

    cli.view_one()

    output = capsys.readouterr().out
    assert "must be a whole number" in output
    assert "Brown Bread" in output


# ---------- add ----------

@patch("builtins.input", side_effect=["Peanut Butter", "Pearl", "999", "Peanuts, salt", "4.25", "15"])
@patch("cli.requests.post")
def test_add_item(mock_post, mock_input, capsys):
    mock_post.return_value = fake_response(
        {"id": 3, "product_name": "Peanut Butter", "brands": "Pearl", "price": 4.25, "stock": 15},
        201
    )

    cli.add_item()

    sent = mock_post.call_args[1]["json"]
    assert sent["product_name"] == "Peanut Butter"
    assert sent["price"] == 4.25
    assert sent["stock"] == 15
    assert "Item added" in capsys.readouterr().out


@patch("builtins.input", side_effect=["", "Pearl", "999", "Peanuts", "4", "5"])
@patch("cli.requests.post")
def test_add_item_api_error(mock_post, mock_input, capsys):
    mock_post.return_value = fake_response({"error": "product_name is required"}, 400)

    cli.add_item()

    assert "product_name is required" in capsys.readouterr().out


@patch("builtins.input", side_effect=["Tea", "Lipton", "1", "Tea leaves", "free", "2.5", "10"])
@patch("cli.requests.post")
def test_add_item_bad_price_asks_again(mock_post, mock_input, capsys):
    mock_post.return_value = fake_response(
        {"id": 3, "product_name": "Tea", "brands": "Lipton", "price": 2.5, "stock": 10}, 201
    )

    cli.add_item()

    assert "price must be a number" in capsys.readouterr().out
    assert mock_post.call_args[1]["json"]["price"] == 2.5


# ---------- update ----------

@patch("builtins.input", side_effect=["1", "2.00", "40"])
@patch("cli.requests.patch")
def test_update_item(mock_patch, mock_input, capsys):
    updated = dict(bread)
    updated["price"] = 2.0
    updated["stock"] = 40
    mock_patch.return_value = fake_response(updated, 200)

    cli.update_item()

    assert mock_patch.call_args[1]["json"] == {"price": 2.0, "stock": 40}
    assert "Item updated" in capsys.readouterr().out


@patch("builtins.input", side_effect=["1", "", "40"])
@patch("cli.requests.patch")
def test_update_only_stock(mock_patch, mock_input):
    mock_patch.return_value = fake_response(bread, 200)

    cli.update_item()

    assert mock_patch.call_args[1]["json"] == {"stock": 40}


@patch("builtins.input", side_effect=["1", "", ""])
@patch("cli.requests.patch")
def test_update_nothing(mock_patch, mock_input, capsys):
    cli.update_item()

    mock_patch.assert_not_called()
    assert "Nothing to update" in capsys.readouterr().out


@patch("builtins.input", side_effect=["1", "cheap"])
@patch("cli.requests.patch")
def test_update_bad_price(mock_patch, mock_input, capsys):
    cli.update_item()

    mock_patch.assert_not_called()
    assert "must be a number" in capsys.readouterr().out


@patch("builtins.input", side_effect=["99", "5", ""])
@patch("cli.requests.patch")
def test_update_item_not_found(mock_patch, mock_input, capsys):
    mock_patch.return_value = fake_response({"error": "Item not found"}, 404)

    cli.update_item()

    assert "Item not found" in capsys.readouterr().out


# ---------- delete ----------

@patch("builtins.input", side_effect=["2"])
@patch("cli.requests.delete")
def test_delete_item(mock_delete, mock_input, capsys):
    mock_delete.return_value = fake_response({"message": "Item deleted"}, 200)

    cli.delete_item()

    assert mock_delete.call_args[0][0].endswith("/inventory/2")
    assert "Item deleted" in capsys.readouterr().out


@patch("builtins.input", side_effect=["99"])
@patch("cli.requests.delete")
def test_delete_item_not_found(mock_delete, mock_input, capsys):
    mock_delete.return_value = fake_response({"error": "Item not found"}, 404)

    cli.delete_item()

    assert "Item not found" in capsys.readouterr().out


# ---------- find on OpenFoodFacts ----------

nutella = {
    "barcode": "3017620422003",
    "product_name": "Nutella",
    "brands": "Ferrero",
    "ingredients_text": "Sugar, palm oil, hazelnuts"
}


@patch("builtins.input", side_effect=["1", "3017620422003", "y", "6.5", "20"])
@patch("cli.requests.post")
@patch("cli.requests.get")
def test_find_by_barcode_and_add(mock_get, mock_post, mock_input, capsys):
    mock_get.return_value = fake_response(nutella)
    mock_post.return_value = fake_response(
        {"id": 3, "product_name": "Nutella", "brands": "Ferrero", "price": 6.5, "stock": 20}, 201
    )

    cli.find_on_api()

    assert mock_get.call_args[0][0].endswith("/search/barcode/3017620422003")
    assert mock_post.call_args[0][0].endswith("/inventory/import/3017620422003")
    assert mock_post.call_args[1]["json"] == {"price": 6.5, "stock": 20}
    assert "Item added" in capsys.readouterr().out


@patch("builtins.input", side_effect=["2", "nutella", "n"])
@patch("cli.requests.post")
@patch("cli.requests.get")
def test_find_by_name_but_do_not_add(mock_get, mock_post, mock_input, capsys):
    mock_get.return_value = fake_response(nutella)

    cli.find_on_api()

    assert mock_get.call_args[1]["params"] == {"name": "nutella"}
    mock_post.assert_not_called()
    assert "Found: Nutella" in capsys.readouterr().out


@patch("builtins.input", side_effect=["1", "0000"])
@patch("cli.requests.get")
def test_find_not_found(mock_get, mock_input, capsys):
    mock_get.return_value = fake_response({"error": "Product not found"}, 404)

    cli.find_on_api()

    assert "Product not found" in capsys.readouterr().out


@patch("builtins.input", side_effect=["1", "123"])
@patch("cli.requests.get")
def test_find_external_api_down(mock_get, mock_input, capsys):
    mock_get.return_value = fake_response({"error": "Could not reach OpenFoodFacts"}, 502)

    cli.find_on_api()

    assert "Could not reach OpenFoodFacts" in capsys.readouterr().out


@patch("builtins.input", side_effect=["7"])
def test_find_invalid_choice(mock_input, capsys):
    cli.find_on_api()

    assert "Please choose 1 or 2" in capsys.readouterr().out


# ---------- main menu ----------

@patch("builtins.input", side_effect=["1", "0"])
@patch("cli.requests.get")
def test_main_shows_items_then_exits(mock_get, mock_input, capsys):
    mock_get.return_value = fake_response([bread])

    cli.main()

    output = capsys.readouterr().out
    assert "Brown Bread" in output
    assert "Goodbye" in output


@patch("builtins.input", side_effect=["9", "0"])
def test_main_invalid_choice(mock_input, capsys):
    cli.main()

    assert "Invalid choice" in capsys.readouterr().out


@patch("builtins.input", side_effect=["1", "0"])
@patch("cli.requests.get")
def test_main_api_not_running(mock_get, mock_input, capsys):
    mock_get.side_effect = requests.exceptions.ConnectionError()

    cli.main()

    output = capsys.readouterr().out
    assert "Cannot connect to the API" in output
    # the menu keeps working after the error
    assert "Goodbye" in output
