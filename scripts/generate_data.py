from pathlib import Path
import pandas as pd
import numpy as np

np.random.seed(42)

RAW_PATH = Path("data/raw")
RAW_PATH.mkdir(parents=True, exist_ok=True)

TODAY = pd.Timestamp("2026-06-26")
START_DATE = pd.Timestamp("2025-01-01")
DAYS_RANGE = (TODAY - START_DATE).days


def generate_suppliers():
    supplier_names = [
        "MediSupply Europe", "PharmaLogistics", "BioHealth Distribution", "EuroMeds",
        "Global Pharma Supply", "HealthChain Partners", "ColdMed Logistics", "LifeCare Suppliers"
    ]

    return pd.DataFrame({
        "supplier_id": [f"SUP{i:03d}" for i in range(1, 9)],
        "supplier_name": supplier_names,
        "country": ["France", "Germany", "Spain", "Italy", "Belgium", "Netherlands", "France", "Germany"],
        "lead_time_days": [5, 8, 12, 7, 10, 6, 4, 9],
        "contact_email": [
            "contact@medisupply.eu", "orders@pharmalogistics.eu",
            "supply@biohealth.eu", "orders@euromeds.eu",
            "contact@globalpharma.eu", "ops@healthchain.eu",
            "coldchain@coldmed.eu", "supplier@lifecare.eu"
        ],
        "status": np.random.choice(["Active", "Inactive"], 8, p=[0.9, 0.1])
    })


def generate_products(suppliers):
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

    products = pd.DataFrame({
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
        "supplier_id": np.random.choice(suppliers["supplier_id"], 50),
        "dosage": np.random.choice(["100mg", "250mg", "500mg", "1g", "5mg/ml"], 50),
        "form": np.random.choice(["Tablet", "Capsule", "Syrup", "Injection", "Cream", "Inhaler"], 50),
        "storage_temp": np.random.choice(["15-25°C", "2-8°C", "Below 30°C"], 50, p=[0.65, 0.25, 0.10]),
        "unit_price": np.round(np.random.uniform(2.5, 95.0, 50), 2),
        "reorder_threshold": np.random.randint(80, 300, 50),
        "criticality_level": np.random.choice(["Low", "Medium", "High", "Critical"], 50, p=[0.35, 0.35, 0.20, 0.10]),
        "status": np.random.choice(["Active", "Discontinued"], 50, p=[0.9, 0.1])
    })

    return products


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
        "order_date": [TODAY - pd.Timedelta(days=int(x)) for x in np.random.randint(0, DAYS_RANGE, n)],
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


def generate_supplier_orders(products, warehouses, suppliers):
    n = 3000

    supplier_orders = pd.DataFrame({
        "supplier_order_id": [f"PO{i:06d}" for i in range(1, n + 1)],
        "supplier_id": np.random.choice(suppliers["supplier_id"], n),
        "product_id": np.random.choice(products["product_id"], n),
        "warehouse_id": np.random.choice(warehouses["warehouse_id"], n),
        "order_date": [TODAY - pd.Timedelta(days=int(x)) for x in np.random.randint(0, DAYS_RANGE, n)],
        "quantity_ordered": np.random.randint(100, 5000, n)
    })

    supplier_orders = supplier_orders.merge(
        suppliers[["supplier_id", "supplier_name"]], on="supplier_id", how="left"
    )

    supplier_orders["expected_delivery_date"] = supplier_orders["order_date"] + pd.to_timedelta(
        np.random.randint(3, 21, n), unit="D"
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
        supplier_orders["actual_delivery_date"] > TODAY, "Open",
        np.where(
            supplier_orders["quantity_received"] >= supplier_orders["quantity_ordered"],
            "Delivered", "Partially Delivered"
        )
    )

    return supplier_orders[[
        "supplier_order_id", "supplier_id", "supplier_name",
        "product_id", "warehouse_id", "order_date",
        "expected_delivery_date", "actual_delivery_date",
        "quantity_ordered", "quantity_received", "order_status"
    ]]


def generate_calendar():
    dates = pd.date_range(start=START_DATE, end=TODAY, freq="D")

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


def generate_alerts(inventory, products, warehouses, suppliers):
    inventory_enriched = (
        inventory
        .merge(products[["product_id", "product_name", "supplier_id", "reorder_threshold", "criticality_level"]], on="product_id", how="left")
        .merge(warehouses[["warehouse_id", "warehouse_name"]], on="warehouse_id", how="left")
        .merge(suppliers[["supplier_id", "supplier_name"]], on="supplier_id", how="left")
    )

    inventory_enriched["days_to_expiry"] = (
        pd.to_datetime(inventory_enriched["expiry_date"]) - TODAY
    ).dt.days

    low_stock = inventory_enriched[
        inventory_enriched["quantity_on_hand"] < inventory_enriched["reorder_threshold"]
    ].copy()
    low_stock["alert_type"] = "Low Stock"

    expiry_risk = inventory_enriched[
        inventory_enriched["days_to_expiry"] <= 90
    ].copy()
    expiry_risk["alert_type"] = "Expiration Risk"

    alerts = pd.concat([low_stock, expiry_risk], ignore_index=True)

    if alerts.empty:
        return pd.DataFrame(columns=[
            "alert_id", "created_at", "product_id", "product_name",
            "warehouse_id", "warehouse_name", "supplier_id", "supplier_name",
            "alert_type", "severity", "quantity_on_hand",
            "reorder_threshold", "days_to_expiry", "status"
        ])

    def severity(row):
        if row["criticality_level"] == "Critical":
            return "Critical"
        if row["alert_type"] == "Expiration Risk" and row["days_to_expiry"] <= 30:
            return "High"
        if row["alert_type"] == "Low Stock" and row["quantity_on_hand"] < 50:
            return "High"
        return "Medium"

    alerts["severity"] = alerts.apply(severity, axis=1)
    alerts["status"] = "Open"
    alerts["created_at"] = TODAY
    alerts["alert_id"] = [f"ALT{i:06d}" for i in range(1, len(alerts) + 1)]

    return alerts[[
        "alert_id", "created_at", "product_id", "product_name",
        "warehouse_id", "warehouse_name", "supplier_id", "supplier_name",
        "alert_type", "severity", "quantity_on_hand",
        "reorder_threshold", "days_to_expiry", "status"
    ]]


def inject_quality_issues(products, warehouses, inventory, sales_orders, supplier_orders):
    products = products.copy()
    warehouses = warehouses.copy()
    inventory = inventory.copy()
    sales_orders = sales_orders.copy()
    supplier_orders = supplier_orders.copy()

    products.loc[products.sample(frac=0.04, random_state=1).index, "manufacturer"] = np.nan
    products.loc[products.sample(frac=0.04, random_state=2).index, "storage_temp"] = np.nan
    warehouses.loc[warehouses.sample(n=1, random_state=3).index, "manager_name"] = np.nan

    warehouses.loc[0, "country"] = "FRANCE"
    warehouses.loc[1, "country"] = "france"
    sales_orders.loc[sales_orders.sample(frac=0.02, random_state=4).index, "customer_type"] = "hospital"

    inventory.loc[inventory.sample(n=3, random_state=5).index, "quantity_on_hand"] = -10
    products.loc[products.sample(n=1, random_state=6).index, "unit_price"] = -5

    bad_expiry_idx = inventory.sample(n=3, random_state=7).index
    inventory.loc[bad_expiry_idx, "expiry_date"] = inventory.loc[bad_expiry_idx, "manufacturing_date"] - pd.Timedelta(days=30)

    bad_sales_idx = sales_orders.sample(n=5, random_state=8).index
    sales_orders.loc[bad_sales_idx, "quantity_delivered"] = sales_orders.loc[bad_sales_idx, "quantity_ordered"] + 50

    sales_orders.loc[sales_orders.sample(n=5, random_state=9).index, "quantity_ordered"] = 25000

    inventory = pd.concat([inventory, inventory.sample(n=10, random_state=10)], ignore_index=True)
    sales_orders = pd.concat([sales_orders, sales_orders.sample(n=20, random_state=11)], ignore_index=True)

    return products, warehouses, inventory, sales_orders, supplier_orders


def save_dataset(df, filename):
    path = RAW_PATH / filename
    df.to_csv(path, index=False)
    print(f"✅ {filename} : {len(df)} lignes")


def main():
    print(f"📅 Période : {START_DATE.date()} → {TODAY.date()} ({DAYS_RANGE} jours)\n")

    suppliers = generate_suppliers()
    products = generate_products(suppliers)
    warehouses = generate_warehouses()
    inventory = generate_inventory(products, warehouses)
    sales_orders = generate_sales_orders(products, warehouses)
    supplier_orders = generate_supplier_orders(products, warehouses, suppliers)
    calendar = generate_calendar()

    products, warehouses, inventory, sales_orders, supplier_orders = inject_quality_issues(
        products, warehouses, inventory, sales_orders, supplier_orders
    )

    alerts = generate_alerts(inventory, products, warehouses, suppliers)

    save_dataset(suppliers, "suppliers.csv")
    save_dataset(products, "products.csv")
    save_dataset(warehouses, "warehouses.csv")
    save_dataset(inventory, "inventory.csv")
    save_dataset(sales_orders, "sales_orders.csv")
    save_dataset(supplier_orders, "supplier_orders.csv")
    save_dataset(alerts, "alerts.csv")
    save_dataset(calendar, "calendar.csv")

    print("\n✅ Tous les datasets générés dans data/raw/")


if __name__ == "__main__":
    main()