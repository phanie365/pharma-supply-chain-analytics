from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

np.random.seed(None)  # Seed aléatoire pour avoir des données différentes chaque jour

RAW_PATH = Path("data/raw")
TODAY = pd.Timestamp(datetime.now().date())


def load_existing(filename):
    path = RAW_PATH / filename
    return pd.read_csv(path)


def generate_daily_sales(products, warehouses, n=50):
    sales = pd.DataFrame({
        "sales_order_id": [f"SO-{TODAY.strftime('%Y%m%d')}-{i:04d}" for i in range(1, n + 1)],
        "order_date": [TODAY] * n,
        "product_id": np.random.choice(products["product_id"], n),
        "warehouse_id": np.random.choice(warehouses["warehouse_id"], n),
        "customer_type": np.random.choice(
            ["Pharmacy", "Hospital", "Clinic", "Distributor"],
            n, p=[0.45, 0.30, 0.15, 0.10]
        ),
        "quantity_ordered": np.random.randint(10, 600, n)
    })

    delivery_rate = np.random.choice([1.0, 0.95, 0.8, 0.5], n, p=[0.72, 0.15, 0.09, 0.04])
    sales["quantity_delivered"] = (sales["quantity_ordered"] * delivery_rate).astype(int)

    sales = sales.merge(products[["product_id", "unit_price"]], on="product_id", how="left")
    sales["sales_amount"] = np.round(sales["quantity_delivered"] * sales["unit_price"], 2)
    sales = sales.drop(columns=["unit_price"])

    return sales


def generate_daily_supplier_orders(products, warehouses, suppliers, n=10):
    supplier_orders = pd.DataFrame({
        "supplier_order_id": [f"PO-{TODAY.strftime('%Y%m%d')}-{i:04d}" for i in range(1, n + 1)],
        "supplier_id": np.random.choice(suppliers["supplier_id"], n),
        "product_id": np.random.choice(products["product_id"], n),
        "warehouse_id": np.random.choice(warehouses["warehouse_id"], n),
        "order_date": [TODAY] * n,
        "quantity_ordered": np.random.randint(100, 5000, n)
    })

    supplier_orders = supplier_orders.merge(
        suppliers[["supplier_id", "supplier_name"]], on="supplier_id", how="left"
    )

    supplier_orders["expected_delivery_date"] = supplier_orders["order_date"] + pd.to_timedelta(
        np.random.randint(3, 21, n), unit="D"
    )

    supplier_orders["actual_delivery_date"] = None
    supplier_orders["quantity_received"] = 0
    supplier_orders["order_status"] = "Open"

    return supplier_orders[[
        "supplier_order_id", "supplier_id", "supplier_name",
        "product_id", "warehouse_id", "order_date",
        "expected_delivery_date", "actual_delivery_date",
        "quantity_ordered", "quantity_received", "order_status"
    ]]


def update_inventory(inventory, products):
    """Met à jour les quantités de stock aléatoirement"""
    inventory = inventory.copy()

    # Simule des mouvements de stock sur 5% des lignes
    n_updates = max(1, int(len(inventory) * 0.05))
    indices = np.random.choice(len(inventory), n_updates, replace=False)

    for idx in indices:
        change = np.random.randint(-50, 100)
        new_qty = max(0, inventory.loc[idx, "quantity_on_hand"] + change)
        inventory.loc[idx, "quantity_on_hand"] = new_qty
        inventory.loc[idx, "last_inventory_update"] = TODAY.strftime("%Y-%m-%d")

    return inventory


def append_to_csv(filename, new_data):
    path = RAW_PATH / filename
    existing = pd.read_csv(path)
    updated = pd.concat([existing, new_data], ignore_index=True)
    updated.to_csv(path, index=False)
    print(f"✅ {filename} : +{len(new_data)} lignes ajoutées (total: {len(updated)})")


def save_csv(filename, data):
    path = RAW_PATH / filename
    data.to_csv(path, index=False)
    print(f"✅ {filename} : {len(data)} lignes sauvegardées")


def main():
    print(f"📅 Génération des données du {TODAY.date()}\n")

    # Charge les données existantes
    products = load_existing("products.csv")
    warehouses = load_existing("warehouses.csv")
    suppliers = load_existing("suppliers.csv")
    inventory = load_existing("inventory.csv")

    # Génère les nouvelles données du jour
    new_sales = generate_daily_sales(products, warehouses, n=50)
    new_supplier_orders = generate_daily_supplier_orders(products, warehouses, suppliers, n=10)
    updated_inventory = update_inventory(inventory, products)

    # Ajoute aux CSV existants
    append_to_csv("sales_orders.csv", new_sales)
    append_to_csv("supplier_orders.csv", new_supplier_orders)
    save_csv("inventory.csv", updated_inventory)

    print(f"\n✅ Données du {TODAY.date()} générées avec succès !")


if __name__ == "__main__":
    main()