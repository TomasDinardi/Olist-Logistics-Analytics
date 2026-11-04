import pandas as pd

pd.set_option("display.max_columns", None)

orders = pd.read_csv("data/raw/olist_orders_dataset.csv")

date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date"
]

for column in date_columns:
    orders[column] = pd.to_datetime(orders[column])

print(orders.head())
orders.info()
print(orders["order_status"].value_counts())

print(
    orders.groupby("order_status")[
        [
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ].count()
)

print("\n")
print("Ordenes con estatus de entregadas sin fecha  de entrega")

print(    
    orders[
        (orders["order_status"] == "delivered") &
        (orders["order_delivered_customer_date"].isna())
    ]
)

print("\n")
print("Ordenes sin estatus de entregadas con fecha de entrega")

print(
    orders[
        (orders["order_status"] != "delivered") &
        (orders["order_delivered_customer_date"].notna())
    ]
)

print("\n")
print("Fechas fuera de orden cronológico:")

print(
    "Aprobación anterior a compra:",
    (orders["order_approved_at"] < orders["order_purchase_timestamp"]).sum()
)

print(
    "Entrega al transportista anterior a compra:",
    (orders["order_delivered_carrier_date"] < orders["order_purchase_timestamp"]).sum()
)

print(
    "Entrega al cliente anterior a entrega al transportista:",
    (orders["order_delivered_customer_date"] < orders["order_delivered_carrier_date"]).sum()
)

print("\n")
print("Órdenes con entrega al transportista anterior a la compra:")

print(
    orders[
        orders["order_delivered_carrier_date"] <
        orders["order_purchase_timestamp"]
    ][
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ].head(10)
)

print("\n")
print("Órdenes con entrega al cliente anterior a la entrega al transportista:")

print(
    orders[
        orders["order_delivered_customer_date"] <
        orders["order_delivered_carrier_date"]
    ][
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ]
)

print("\n")

# Diferencia entre compra y entrega al transportista
carrier_before_purchase = (
    orders.loc[
        orders["order_delivered_carrier_date"] <
        orders["order_purchase_timestamp"],
        "order_purchase_timestamp"
    ]
    -
    orders.loc[
        orders["order_delivered_carrier_date"] <
        orders["order_purchase_timestamp"],
        "order_delivered_carrier_date"
    ]
)

print("Diferencia entre compra y entrega al transportista (horas):")
print((carrier_before_purchase.dt.total_seconds() / 3600).describe())

print("\n")

# Diferencia entre entrega al transportista y entrega al cliente
customer_before_carrier = (
    orders.loc[
        orders["order_delivered_customer_date"] <
        orders["order_delivered_carrier_date"],
        "order_delivered_carrier_date"
    ]
    -
    orders.loc[
        orders["order_delivered_customer_date"] <
        orders["order_delivered_carrier_date"],
        "order_delivered_customer_date"
    ]
)

print("Diferencia entre entrega al cliente y al transportista (horas):")
print((customer_before_carrier.dt.total_seconds() / 3600).describe())

print("\n")

# Diferencia entre compra y entrega al transportista
carrier_anomalies = orders.loc[
    orders["order_delivered_carrier_date"] <
    orders["order_purchase_timestamp"]
].copy()

carrier_anomalies["difference_hours"] = (
    carrier_anomalies["order_purchase_timestamp"] -
    carrier_anomalies["order_delivered_carrier_date"]
).dt.total_seconds() / 3600

print("10 mayores anomalías de entrega al transportista:")

print(
    carrier_anomalies[
        [
            "order_id",
            "order_status",
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
            "difference_hours"
        ]
    ].sort_values(
        by="difference_hours",
        ascending=False
    ).head(10)
)

print("\n")

extreme_orders = orders.loc[
    orders["order_id"].isin([
        "7c48bb55e8e4f7e56d412e9653db37bc",
        "4021cd7611d6d9ce5ffcd24817fc374f"
    ])
]

print(extreme_orders.T)

print("\n")

print(
    carrier_anomalies[
        carrier_anomalies["difference_hours"] > 24
    ][
        [
            "order_id",
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
            "difference_hours"
        ]
    ].sort_values(
        by="difference_hours",
        ascending=False
    )
)

print("\n")

print(
    orders.groupby("order_status")[
        date_columns
    ].apply(lambda x: x.isna().sum())
)

print("\n")

delivered_missing_dates = orders.loc[
    (orders["order_status"] == "delivered") &
    (
        orders[
            [
                "order_approved_at",
                "order_delivered_carrier_date",
                "order_delivered_customer_date"
            ]
        ].isna().any(axis=1)
    ),
    [
        "order_id",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date"
    ]
]

print(delivered_missing_dates.to_string(index=False))

print("\n")

delivered_missing_approval = orders.loc[
    (orders["order_status"] == "delivered") &
    (orders["order_approved_at"].isna())
]

print(
    delivered_missing_approval[
        [
            "order_id",
            "order_purchase_timestamp",
            "order_delivered_carrier_date",
            "order_delivered_customer_date"
        ]
    ].sort_values(
        by="order_purchase_timestamp"
    ).to_string(index=False)
)

print("\n")

print("Cantidad de order_id duplicados:")
print(orders["order_id"].duplicated().sum())

print("¿Todos los order_id son únicos?")
print(orders["order_id"].is_unique)
