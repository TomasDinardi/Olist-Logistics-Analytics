import pandas as pd

pd.set_option("display.max_columns", None)

customers = pd.read_csv("data/raw/olist_customers_dataset.csv")

print(customers.head())
customers.info()

print("\nCantidad de customer_id duplicados:")
print(customers["customer_id"].duplicated().sum())

print("\n¿Todos los customer_id son únicos?")
print(customers["customer_id"].is_unique)

print("\nCantidad de customer_unique_id distintos:")
print(customers["customer_unique_id"].nunique())

print("\nCantidad de customer_unique_id duplicados:")
print(customers["customer_unique_id"].duplicated().sum())


customer_frequency = customers["customer_unique_id"].value_counts()

print("\nCantidad de clientes con más de un registro:")
print((customer_frequency > 1).sum())

print("\nCantidad máxima de registros asociados a un cliente:")
print(customer_frequency.max())

print("\nDistribución de clientes según cantidad de registros:")
print(customer_frequency.value_counts().sort_index())


print("\nCantidad de códigos postales distintos:")
print(customers["customer_zip_code_prefix"].nunique())

print("\nCantidad de códigos postales iguales a cero:")
print((customers["customer_zip_code_prefix"] == 0).sum())

print("\nCantidad de códigos postales negativos:")
print((customers["customer_zip_code_prefix"] < 0).sum())

print("\nCódigos postales más frecuentes:")
print(customers["customer_zip_code_prefix"].value_counts().head(10))


print("\nCantidad de ciudades distintas:")
print(customers["customer_city"].nunique())

print("\nCantidad de estados distintos:")
print(customers["customer_state"].nunique())

print("\nCantidad de registros por estado:")
print(customers["customer_state"].value_counts())

print("\nLas 15 ciudades con más registros:")
print(customers["customer_city"].value_counts().head(15))


print("\nCantidad de combinaciones geográficas distintas:")
print(
    customers[
        ["customer_zip_code_prefix", "customer_city", "customer_state"]
    ].drop_duplicates().shape[0]
)

zip_locations = customers.groupby("customer_zip_code_prefix")[
    ["customer_city", "customer_state"]
].nunique()

print("\nCódigos postales asociados a más de una ciudad:")
print((zip_locations["customer_city"] > 1).sum())

print("\nCódigos postales asociados a más de un estado:")
print((zip_locations["customer_state"] > 1).sum())


orders = pd.read_csv("data/raw/olist_orders_dataset.csv")

print("\nCantidad de customer_id de orders que no existen en customers:")
print((~orders["customer_id"].isin(customers["customer_id"])).sum())

print("\nCantidad de customer_id de customers que no existen en orders:")#
print((~customers["customer_id"].isin(orders["customer_id"])).sum())