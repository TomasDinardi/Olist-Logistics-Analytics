import pandas as pd

pd.set_option("display.max_columns", None)

products = pd.read_csv("data/raw/olist_products_dataset.csv")

print(products.head())
products.info()

print("\n")

print("Cantidad de valores faltantes por columna:")
print(products.isna().sum())

print("\nPorcentaje de valores faltantes por columna:")
print((products.isna().mean() * 100).round(2))

print("\n")

descriptive_columns = [
    "product_category_name",
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty"
]

physical_columns = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("Productos con información descriptiva incompleta:")
print(
    products[
        products[descriptive_columns].isna().any(axis=1)
    ]
)

print("Productos con información física incompleta:")
print(
    products[
        products[physical_columns].isna().any(axis=1)
    ]
)

print("\n")

print("Cantidad de product_id duplicados:")
print(products["product_id"].duplicated().sum())

print("¿Todos los product_id son únicos?")
print(products["product_id"].is_unique)

print("\n")

numeric_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("Valores iguales a cero:")
print((products[numeric_columns] == 0).sum())

print("\nValores negativos:")
print((products[numeric_columns] < 0).sum())

print("\n")

print("Productos con peso igual a cero:")
print(
    products.loc[
        products["product_weight_g"] == 0,
        [
            "product_id",
            "product_category_name",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm"
        ]
    ]
)

print("\n")

print("Estadísticas descriptivas de productos:")
print(products[numeric_columns].describe())

print("\n")

print("\nCantidad de productos por categoría:")
print(products["product_category_name"].value_counts(dropna=False).head(15))

print("\n")

physical_columns = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm"
]

print("10 productos con mayor peso:")
print(
    products.nlargest(10, "product_weight_g")[
        ["product_id", "product_category_name"] + physical_columns
    ]
)

print("\n10 productos con mayor volumen geométrico:")
products["volume_cm3"] = (
    products["product_length_cm"]
    * products["product_height_cm"]
    * products["product_width_cm"]
)

print(
    products.nlargest(10, "volume_cm3")[
        ["product_id", "product_category_name"] + physical_columns + ["volume_cm3"]
    ]
)

