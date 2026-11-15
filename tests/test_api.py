from app import inventory


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Inventory API is running"


def test_get_all_items(client):
    response = client.get("/inventory")
    assert response.status_code == 200
    assert len(response.get_json()) == 2


def test_get_one_item(client):
    response = client.get("/inventory/1")
    assert response.status_code == 200
    assert response.get_json()["product_name"] == "Brown Bread"


def test_get_item_not_found(client):
    response = client.get("/inventory/99")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_create_item(client):
    new_item = {
        "product_name": "Peanut Butter",
        "brands": "Pearl",
        "price": 4.25,
        "stock": 15
    }
    response = client.post("/inventory", json=new_item)
    assert response.status_code == 201

    data = response.get_json()
    assert data["id"] == 3
    assert data["product_name"] == "Peanut Butter"
    assert len(inventory) == 3


def test_create_item_without_name(client):
    response = client.post("/inventory", json={"price": 5})
    assert response.status_code == 400
    assert len(inventory) == 2


def test_create_item_without_json(client):
    response = client.post("/inventory")
    assert response.status_code == 400


def test_create_item_bad_price(client):
    response = client.post("/inventory", json={"product_name": "Tea", "price": "cheap"})
    assert response.status_code == 400


def test_create_item_negative_stock(client):
    response = client.post("/inventory", json={"product_name": "Tea", "stock": -5})
    assert response.status_code == 400


def test_update_price_and_stock(client):
    response = client.patch("/inventory/1", json={"price": 1.80, "stock": 50})
    assert response.status_code == 200

    data = response.get_json()
    assert data["price"] == 1.80
    assert data["stock"] == 50
    assert data["product_name"] == "Brown Bread"


def test_update_item_not_found(client):
    response = client.patch("/inventory/99", json={"price": 2})
    assert response.status_code == 404


def test_update_bad_price(client):
    response = client.patch("/inventory/1", json={"price": -3})
    assert response.status_code == 400
    assert inventory[0]["price"] == 1.50


def test_update_bad_stock_does_not_change_price(client):
    response = client.patch("/inventory/1", json={"price": 9, "stock": "lots"})
    assert response.status_code == 400
    assert inventory[0]["price"] == 1.50


def test_update_without_json(client):
    response = client.patch("/inventory/1")
    assert response.status_code == 400


def test_delete_item(client):
    response = client.delete("/inventory/2")
    assert response.status_code == 200
    assert len(inventory) == 1

    response = client.get("/inventory/2")
    assert response.status_code == 404


def test_delete_item_not_found(client):
    response = client.delete("/inventory/99")
    assert response.status_code == 404
    assert len(inventory) == 2
