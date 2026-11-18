# Inventory Management System

A simple inventory system built with Flask. It allows users to add, view, update, search, and delete shop products.

It also uses OpenFoodFacts to find product information using a barcode or product name.


## Setup

1. Create a virtual environment:

```bash
python -m venv venv
```

2. Activate it:

```bash
source venv/bin/activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Project

Open two terminals.

**Terminal 1 – Start the API:**

```bash
python app.py
```

**Terminal 2 – Start the CLI:**

```bash
python cli.py
```

## API Endpoints

- `GET /inventory` – View products
- `GET /inventory/<id>` – View one product
- `POST /inventory` – Add a product
- `PATCH /inventory/<id>` – Update a product
- `DELETE /inventory/<id>` – Delete a product
- `GET /search/barcode/<barcode>` – Search by barcode
- `GET /search/name` – Search by name
- `POST /inventory/import/<barcode>` – Import a product
## CLI Menu

The command line menu allows you to:

1. View all products
2. View one product
3. Add a product
4. Update price or stock
5. Delete a product
6. Search for a product
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

## Tests

```bash
python -m pytest
```