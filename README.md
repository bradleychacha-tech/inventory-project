# Inventory Management System

A Flask REST API and a command line menu for managing a shop's inventory. Product details can be looked up from [OpenFoodFacts](https://world.openfoodfacts.org/). The data is kept in a Python list, so it resets when the server restarts.

## Setup

Create and activate a virtual environment (`venv\Scripts\activate` on Windows, `source venv/bin/activate` on Mac or Linux), then install the packages:

```bash
pip install -r requirements.txt
```

## Run

Start the API in one terminal:

```bash
python app.py
```

Start the CLI in a second terminal:

```bash
python cli.py
```

## API endpoints

| Method | Route | What it does |
|--------|-------|--------------|
| GET | `/inventory` | Get all items |
| GET | `/inventory/<id>` | Get one item |
| POST | `/inventory` | Add an item (`product_name` required, plus `brands`, `barcode`, `ingredients_text`, `price`, `stock`) |
| PATCH | `/inventory/<id>` | Update an item (for example `price` or `stock`) |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/search/barcode/<barcode>` | Find a product on OpenFoodFacts by barcode |
| GET | `/search/name?name=...` | Find a product on OpenFoodFacts by name |
| POST | `/inventory/import/<barcode>` | Add an OpenFoodFacts product to the inventory (JSON: `price`, `stock`) |

Errors are returned as JSON, for example `{"error": "Item not found"}`.

## CLI usage

```
1. View all items
2. View one item
3. Add a new item
4. Update price or stock
5. Delete an item
6. Find a product on OpenFoodFacts
0. Exit
```

Example of updating an item (option 4):

```
Choose an option: 4
Enter the item ID: 1
New price (press Enter to skip): 7.00
New stock (press Enter to skip):
Item updated:
ID: 1 | Name: Nutella Hazelnut Spread | Brand: Ferrero | Price: 7.0 | Stock: 25
```