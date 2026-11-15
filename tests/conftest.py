import pytest
from app import app, inventory


@pytest.fixture
def client():
    app.config["TESTING"] = True

    inventory.clear()
    inventory.append({
        "id": 1,
        "barcode": "1111111111111",
        "product_name": "Brown Bread",
        "brands": "Festive",
        "ingredients_text": "Wheat flour, water, yeast, salt",
        "price": 1.50,
        "stock": 30
    })
    inventory.append({
        "id": 2,
        "barcode": "2222222222222",
        "product_name": "Orange Juice",
        "brands": "Del Monte",
        "ingredients_text": "Orange juice, water",
        "price": 2.75,
        "stock": 10
    })

    return app.test_client()
