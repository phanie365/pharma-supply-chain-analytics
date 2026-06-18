from pathlib import Path
import pandas as pd
import numpy as np

np.random.seed(42)

RAW_PATH = Path("data/raw")
RAW_PATH.mkdir(parents=True, exist_ok=True)

TODAY = pd.Timestamp("2026-06-18")


def generate_products():
    product_names = [
        "Doliprane", "Amoxicilline", "Ibuprofene", "Paracetamol", "Augmentin",
        "Ventoline", "Efferalgan", "Spasfon", "Kardegic", "Aerius",
        "Dafalgan", "Smecta", "Forlax", "Lovenox", "Plavix",
        "Toplexil", "Levothyrox", "Zyrtec", "Mopral", "Gaviscon",
        "Tramadol", "Cefixime", "Azithromycine", "Metformine", "Insuline",
        "Amlodipine", "Ramipril", "Omeprazole", "Prednisone", "Furosemide",
        "Loratadine", "Cetirizine", "Fluconazole", "Ketoprofene", "Biseptine",
        "Sertraline", "Atorvastatine", "Rivaroxaban", "Bisoprolol", "Salbutamol",
        "Clamoxyl", "Flagyl", "Cortancyl", "Eliquis", "Xarelto",
        "Humalog", "Lantus", "Inexium", "Doxycycline", "Nurofen"
    ]

    return pd.DataFrame({
        "product_id": [f"P{i:03d}" for i in range(1, 51)],
        "product_name": product_names,
        "category": np.random.choice([
            "Analgesic", "Antibiotic", "Anti-inflammatory", "Respiratory",
            "Cardiovascular", "Gastrointestinal", "Endocrinology",
            "Antiallergic", "Anticoagulant", "Dermatology"
        ], 50),
        "manufacturer": np.random.choice([
            "Sanofi", "Pfizer", "Novartis", "Roche",
            "GSK", "Bayer", "Merck", "AstraZeneca"
        ], 50),
        "dosage": np.random.choice(["100mg", "250mg", "500mg", "1g", "5mg/ml"], 50),
        "form": np.random.choice(["Tablet", "Capsule", "Syrup", "Injection", "Cream", "Inhaler"], 50),
        "storage_temp": np.random.choice(["15-25°C", "2-8°C", "Below 30°C"], 50, p=[0.65, 0.25, 0.10]),
        "unit_price": np.round(np.random.uniform(2.5, 95.0, 50), 2),
        "status": np.random.choice(["Active", "Discontinued"], 50, p=[0.9, 0.1])
    })


def generate_warehouses():
    locations = [
        ("France", "Paris"), ("France", "Lyon"),
        ("Germany", "Berlin"), ("Germany", "Munich"),
        ("Spain", "Madrid"), ("Spain", "Barcelona"),
        ("Italy", "Milan"), ("Italy", "Rome"),
        ("Belgium", "Brussels"), ("Netherlands", "Amsterdam")
    ]

    return pd.DataFrame({
        "warehouse_id": [f"WH{i:03d}" for i in range(1, 11)],
        "warehouse_name": [f"{city} Distribution Center" for _, city in locations],
        "country": [country for country, _ in locations],
        "city": [city for _, city in locations],
        "warehouse_type": np.random.choice(["Central", "Regional", "Cold Chain"], 10, p=[0.3, 0.5, 0.2]),
        "capacity_units": np.random.randint(30000, 120000, 10),
        "manager_name": [
            "Martin Dupont", "Claire Bernard", "Hans Muller", "Anna Schmidt",
            "Carlos Garcia", "Lucia Fernandez", "Marco Rossi", "Giulia Romano",
            "Sophie Peeters", "Eva De Vries"
        ]
    })


def generate_inventory(products, warehouses):
    n = 5000

    inventory = pd.DataFrame({
        "inventory_id": [f"INV{i:06d}" for i in range(1, n + 1)],
        "product_id": np.random.choice(products["product_id"], n),
        "warehouse_id": np.random.choice(warehouses["warehouse_id"], n),
        "batch_id": [f"BATCH-{np.random.randint(2024, 2027)}-{i:05d}" for i in range(1, n + 1)]
    })

    quantities = np.random.randint(120, 2500, n)

    stockout_indices = np.random.choice(n, size=int(n * 0.20), replace=False)
    quantities[stockout_indices] = np.random.randint(0, 100, len(stockout_indices))

    inventory["quantity_on_hand"] = quantities
    inventory["manufacturing_date"] = [
        TODAY - pd.Timedelta(days=int(x)) for x in np.random.randint(30, 900, n)
    ]

    expiry_risk_indices = set(np.random.choice(n, size=int(n * 0.10), replace=False))
    expiry_dates = []

    for i in range(n):
        if i in expiry_risk_indices:
            expiry_dates.append(TODAY + pd.Timedelta(days=int(np.random.randint(5, 90))))
        else:
            expiry_dates.append(TODAY + pd.Timedelta(days=int(np.random.randint(91, 900))))

    inventory["expiry_date"] = expiry_dates
    inventory["last_inventory_update"] = [
        TODAY - pd.Timedelta(days=int(x)) for x in np.random.randint(0, 30, n)
    ]

    return inventory


def generate_sales_orders(products, warehouses):
    n = 15000

    sales = pd.DataFrame({
        "sales_order_id": [f"SO{i:06d}" for i in range(1, n + 1)],
        "order_date": [TODAY - pd.Timedelta(days=int(x)) for x in np.random.randint(0, 365, n)],
        "product_id": np.random.choice(products["product_id"], n),
        "warehouse_id": np.random.choice(warehouses["warehouse_id"], n),
        "customer_type": np.random.choice(
            ["Pharmacy", "Hospital", "Clinic", "Distributor"],
            n,
            p=[0.45, 0.30, 0.15, 0.10]
        ),
        "quantity_ordered": np.random.randint(10, 600, n)
    })

    delivery_rate = np.random.choice([1.0, 0.95, 0.8, 0.5], n, p=[0.72, 0.15, 0.09, 0.04])
    sales["quantity_delivered"] = (sales["quantity_ordered"] * delivery_rate).astype(int)

    sales = sales.merge(products[["product_id", "unit_price"]], on="product_id", how="left")
    sales["sales_amount"] = np.round(sales["quantity_delivered"] * sales["unit_price"], 2)
    sales = sales.drop(columns=["unit_price"])

    return sales


def generate_supplier_orders(products, warehouses):
    n = 3000

    supplier_names = [
        "MediSupply Europe", "PharmaLogistics", "BioHealth Distribution", "EuroMeds",
        "Global Pharma Supply", "HealthChain Partners", "ColdMed Logistics", "LifeCare Suppliers"
    ]
    supplier_ids = [f"SUP{i:03d}" for i in range(1, len(supplier_names) + 1)]

    supplier_lookup = pd.DataFrame({
        "supplier_id": supplier_ids,
        "supplier_name": supplier_names
    })

    supplier_orders = pd.DataFrame({
        "supplier_order_id": [f"PO{i:06d}" for i in range(1, n + 1)],
        "supplier_id": np.random.choice(supplier_ids, n),
        "product_id": np.random.choice(products["product_id"], n),
        "warehouse_id": np.random.choice(warehouses["warehouse_id"], n),
        "order_date": [TODAY - pd.Timedelta(days=int(x)) for x in np.random.randint(0, 365, n)],
        "quantity_ordered": np.random.randint(100, 5000, n)
    })

    supplier_orders = supplier_orders.merge(supplier_lookup, on="supplier_id", how="left")

    supplier_orders["expected_delivery_date"] = supplier_orders["order_date"] + pd.to_timedelta(
        np.random.randint(3, 21, n),
        unit="D"
    )

    late_flags = np.random.choice([0, 1], n, p=[0.85, 0.15])
    actual_delivery_dates = []

    for expected_date, is_late in zip(supplier_orders["expected_delivery_date"], late_flags):
        if is_late:
            actual_delivery_dates.append(expected_date + pd.Timedelta(days=int(np.random.randint(1, 15))))
        else:
            actual_delivery_dates.append(expected_date - pd.Timedelta(days=int(np.random.randint(0, 3))))

    supplier_orders["actual_delivery_date"] = actual_delivery_dates

    received_rate = np.random.choice([1.0, 0.95, 0.90, 0.75], n, p=[0.75, 0.15, 0.07, 0.03])
    supplier_orders["quantity_received"] = (supplier_orders["quantity_ordered"] * received_rate).astype(int)

    supplier_orders["order_status"] = np.where(
        supplier_orders["actual_delivery_date"] > TODAY,
        "Open",
        np.where(
            supplier_orders["quantity_received"] >= supplier_orders["quantity_ordered"],
            "Delivered",
            "Partially Delivered"
        )
    )

    return supplier_orders[
        [
            "supplier_order_id", "supplier_id", "supplier_name",
            "product_id", "warehouse_id", "order_date",
            "expected_delivery_date", "actual_delivery_date",
            "quantity_ordered", "quantity_received", "order_status"
        ]
    ]


def generate_calendar():
    dates = pd.date_range(
        start=TODAY - pd.Timedelta(days=365),
        end=TODAY + pd.Timedelta(days=365),
        freq="D"
    )

    return pd.DataFrame({
        "date_key": dates.strftime("%Y%m%d").astype(int),
        "full_date": dates,
        "day": dates.day,
        "month": dates.month,
        "month_name": dates.strftime("%B"),
        "quarter": dates.quarter,
        "year": dates.year,
        "week_number": dates.isocalendar().week.astype(int)
    })


def save_dataset(df, filename):
    path = RAW_PATH / filename
    df.to_csv(path, index=False)
    print(f"{filename} generated: {len(df)} rows")


def main():
    products = generate_products()
    warehouses = generate_warehouses()
    inventory = generate_inventory(products, warehouses)
    sales_orders = generate_sales_orders(products, warehouses)
    supplier_orders = generate_supplier_orders(products, warehouses)
    calendar = generate_calendar()

    save_dataset(products, "products.csv")
    save_dataset(warehouses, "warehouses.csv")
    save_dataset(inventory, "inventory.csv")
    save_dataset(sales_orders, "sales_orders.csv")
    save_dataset(supplier_orders, "supplier_orders.csv")
    save_dataset(calendar, "calendar.csv")

    print("\nAll datasets generated successfully in data/raw/")


if __name__ == "__main__":
    main()