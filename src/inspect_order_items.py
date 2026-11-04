import pandas as pd

pd.set_option("display.max_columns", None)

order_items = pd.read_csv("data/raw/olist_order_items_dataset.csv")

order_items["shipping_limit_date"] = pd.to_datetime(
    order_items["shipping_limit_date"]
)

print(order_items.head())
order_items.info()

print("\n")

print("Cantidad de filas duplicadas:")
print(order_items.duplicated().sum())

print("\n")

print("Cantidad de combinaciones order_id + order_item_id duplicadas:")

print(
    order_items.duplicated(
        subset=["order_id", "order_item_id"]
    ).sum()
)

print("\n")

print("Registros con precio igual o inferior a cero:")
print(order_items[order_items["price"] <= 0])

print("Registros con flete igual o inferior a cero:")
print(order_items[order_items["freight_value"] <= 0])

print("\n")

print("Cantidad de registros con flete igual a cero:")
print((order_items["freight_value"] == 0).sum())

print("Porcentaje sobre el total:")
print(
    (order_items["freight_value"] == 0).mean() * 100
)

print("\n")

print("Estadísticas descriptivas de precio y flete:")
print(order_items[["price", "freight_value"]].describe())

print("\n")

print("10 registros con mayor precio:")
print(
    order_items.sort_values(
        by="price",
        ascending=False
    ).head(10)
)

print("10 registros con mayor costo de envío:")
print(
    order_items.sort_values(
        by="freight_value",
        ascending=False
    ).head(10)
)