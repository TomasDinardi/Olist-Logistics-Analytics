# Inspección y calidad de datos

## 1. Objetivo

Esta etapa tiene como objetivo realizar una inspección inicial de las tablas del dataset de Olist para comprender su estructura, identificar posibles problemas de calidad y evaluar qué validaciones serán necesarias antes de comenzar el análisis.

Se revisan principalmente:

- Cantidad de registros y columnas.
- Tipos de datos.
- Valores faltantes.
- Registros duplicados.
- Consistencia de fechas e importes.
- Distribución de las variables numéricas.

**Criterio de trabajo:** no se eliminan ni modifican registros durante esta etapa. Los valores inusuales se investigan antes de decidir si requieren algún tratamiento.

---

## 2. Tabla `orders`

**Archivo:** `olist_orders_dataset.csv`  
**Script:** `src/inspect_orders.py`

### 2.1. Estructura general

- Registros: 99.441.
- Columnas: 8.
- Valores faltantes: presentes en algunas columnas de fechas.
- Granularidad: un registro por pedido.

Las columnas identificadas son:

| Columna | Descripción |
|---|---|
| `order_id` | Identificador del pedido. |
| `customer_id` | Identificador del cliente. |
| `order_status` | Estado del pedido. |
| `order_purchase_timestamp` | Fecha y hora de compra. |
| `order_approved_at` | Fecha y hora de aprobación. |
| `order_delivered_carrier_date` | Fecha de entrega al transportista. |
| `order_delivered_customer_date` | Fecha de entrega al cliente. |
| `order_estimated_delivery_date` | Fecha estimada de entrega. |

Las cinco columnas correspondientes a fechas fueron convertidas al tipo `datetime64[us]` mediante `pd.to_datetime()` para permitir operaciones y comparaciones temporales.

### 2.2. Distribución de estados

| Estado | Cantidad |
|---|---:|
| delivered | 96.478 |
| shipped | 1.107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |
| **Total** | **99.441** |

La mayoría de los pedidos se encuentra en estado `delivered`.

### 2.3. Valores faltantes

Se identificaron los siguientes valores nulos:

| Columna | Valores faltantes |
|---|---:|
| `order_id` | 0 |
| `customer_id` | 0 |
| `order_status` | 0 |
| `order_purchase_timestamp` | 0 |
| `order_approved_at` | 160 |
| `order_delivered_carrier_date` | 1.783 |
| `order_delivered_customer_date` | 2.965 |
| `order_estimated_delivery_date` | 0 |

La presencia de fechas faltantes debe interpretarse considerando el estado de cada pedido. Por ejemplo, un pedido cancelado no necesariamente llegará a las etapas de despacho y entrega.

Sin embargo, también se encontraron pedidos en estado `delivered` con fechas faltantes, que requieren atención:

- 14 pedidos sin fecha de aprobación.
- 2 pedidos sin fecha de entrega al transportista.
- 8 pedidos sin fecha de entrega al cliente.

Al considerar los posibles solapamientos entre estas situaciones, se identificaron **23 pedidos entregados afectados**.

### 2.4. Validación de identificadores

Se verificó la existencia de identificadores duplicados en `order_id`.

**Resultado:** 0 duplicados.

La columna presenta valores únicos y puede considerarse una candidata a clave primaria de la tabla.

### 2.5. Consistencia de fechas

Se realizaron validaciones sobre el orden cronológico de las fechas del proceso logístico.

Se identificaron:

- 0 pedidos con fecha de aprobación anterior a la fecha de compra.
- 166 pedidos con fecha de entrega al transportista anterior a la fecha de compra.
- 23 pedidos con fecha de entrega al cliente anterior a la fecha de entrega al transportista.

Los 166 casos de fechas de transportista anteriores a la compra presentan diferencias de distinta magnitud. La mayoría tiene diferencias de hasta 24 horas, aunque se identificaron dos casos especialmente extremos:

- Un registro con una fecha de transportista aproximadamente 171 días anterior a la compra.
- Otro registro con una fecha de transportista aproximadamente 4 días anterior a la compra.

En los 23 casos de entrega al cliente anterior a la entrega al transportista, las diferencias también varían considerablemente.

Estas situaciones representan inconsistencias cronológicas que podrían estar relacionadas con problemas de registro o disponibilidad de información. Sin embargo, no se cuenta con evidencia suficiente para determinar su origen.

**Decisión metodológica:** conservar los registros originales y evitar utilizar intervalos temporales inválidos en los cálculos de duración correspondientes. No se modificarán fechas sin una justificación verificable.

---

## 3. Tabla `order_items`

**Archivo:** `olist_order_items_dataset.csv`  
**Script:** `src/inspect_order_items.py`

### 3.1. Estructura general

- Registros: 112.650.
- Columnas: 7.
- Valores faltantes: ninguno.
- Granularidad: un registro por artículo dentro de un pedido.

Las columnas identificadas son:

| Columna | Descripción |
|---|---|
| `order_id` | Identificador del pedido. |
| `order_item_id` | Número de posición del artículo dentro del pedido. |
| `product_id` | Identificador del producto. |
| `seller_id` | Identificador del vendedor. |
| `shipping_limit_date` | Fecha límite de envío al transportista. |
| `price` | Precio del artículo. |
| `freight_value` | Costo de envío del artículo. |

La columna `shipping_limit_date` fue convertida al tipo `datetime64[us]` para permitir operaciones temporales.

### 3.2. Validación de identificadores y relaciones

Se verificó la unicidad de la combinación `order_id` + `order_item_id`.

**Resultado:** 0 combinaciones duplicadas.

Esto permite considerar ambas columnas como candidatas a clave primaria compuesta.

La tabla `order_items` funciona como tabla de detalle y asociativa entre los pedidos (`orders`) y los productos (`products`).

Se identifican las siguientes relaciones:

- `order_items.order_id`: clave foránea candidata hacia `orders.order_id`.
- `order_items.product_id`: clave foránea candidata hacia `products.product_id`.
- `order_items.seller_id`: clave foránea candidata hacia `sellers.seller_id`.

La integridad referencial de estas relaciones queda pendiente de validación.

### 3.3. Validación de importes

Se revisaron los valores iguales o inferiores a cero en `price` y `freight_value`.

| Validación | Resultado |
|---|---:|
| Precio igual o inferior a cero | 0 |
| Flete negativo | 0 |
| Flete igual a cero | 383 |

Los 383 registros con costo de envío igual a cero representan aproximadamente el **0,34 % del total**.

Estos valores no se consideran errores automáticamente, ya que podrían corresponder a envíos gratuitos u otras condiciones comerciales.

No se identificaron precios iguales o inferiores a cero ni costos de envío negativos.

### 3.4. Estadísticas descriptivas

Se calcularon estadísticas descriptivas para las variables `price` y `freight_value`.

| Estadístico | Precio (`price`) | Flete (`freight_value`) |
|---|---:|---:|
| Cantidad | 112.650 | 112.650 |
| Promedio | 120,65 | 19,99 |
| Desviación estándar | 183,63 | 15,81 |
| Mínimo | 0,85 | 0,00 |
| 25 % | 39,90 | 13,08 |
| Mediana | 74,99 | 16,26 |
| 75 % | 134,90 | 21,15 |
| Máximo | 6.735,00 | 409,68 |

Se observa una diferencia considerable entre el promedio y la mediana en ambas variables:

- En `price`, el promedio es 120,65 y la mediana 74,99.
- En `freight_value`, el promedio es 19,99 y la mediana 16,26.

Esto sugiere una posible asimetría hacia valores elevados y una dispersión importante.

### 3.5. Investigación inicial de valores extremos

Se inspeccionaron los diez registros con mayor precio y los diez registros con mayor costo de envío.

**Precio:**

- El valor máximo observado es 6.735.
- Los diez registros analizados presentan precios entre 3.999,90 y 6.735.

**Costo de envío:**

- El valor máximo observado es 409,68.
- Los diez registros analizados presentan costos de envío entre 314,40 y 409,68.

Estos valores se consideran observaciones extremas que requieren mayor investigación. No se clasifican automáticamente como errores ni se eliminan.

Una investigación posterior podrá relacionarlos con las características de los productos, sus dimensiones, peso, vendedores y ubicaciones.

---

**## 4. Tabla `products`**

**Archivo:** `olist_products_dataset.csv`  
**Script:** `src/inspect_products.py`

**### 4.1. Estructura general**

- Registros: 32.951.
- Columnas: 9.
- Valores faltantes: presentes en columnas descriptivas y físicas.
- Granularidad: un registro por producto.

Las columnas identificadas son:

| Columna | Descripción |
|---|---|
| `product_id` | Identificador del producto. |
| `product_category_name` | Categoría del producto. |
| `product_name_lenght` | Longitud del nombre del producto. |
| `product_description_lenght` | Longitud de la descripción del producto. |
| `product_photos_qty` | Cantidad de fotografías del producto. |
| `product_weight_g` | Peso del producto en gramos. |
| `product_length_cm` | Largo del producto en centímetros. |
| `product_height_cm` | Alto del producto en centímetros. |
| `product_width_cm` | Ancho del producto en centímetros. |

Se conservaron los nombres originales de las columnas, incluyendo la escritura `lenght` presente en el dataset.

**### 4.2. Valores faltantes**

Se identificaron los siguientes valores nulos:

| Columna | Valores faltantes | Porcentaje |
|---|---:|---:|
| `product_id` | 0 | 0 % |
| `product_category_name` | 610 | 1,85 % |
| `product_name_lenght` | 610 | 1,85 % |
| `product_description_lenght` | 610 | 1,85 % |
| `product_photos_qty` | 610 | 1,85 % |
| `product_weight_g` | 2 | 0,01 % |
| `product_length_cm` | 2 | 0,01 % |
| `product_height_cm` | 2 | 0,01 % |
| `product_width_cm` | 2 | 0,01 % |

Se comprobó que los 610 productos con información descriptiva incompleta presentan valores faltantes simultáneamente en los cuatro campos correspondientes.

En cuanto a la información física, se identificaron dos productos:

- Un producto tiene información descriptiva completa, pero carece de peso y dimensiones.
- Otro producto presenta valores faltantes tanto en los campos descriptivos como en los físicos.

**### 4.3. Validación de identificadores**

Se verificó la existencia de identificadores duplicados en `product_id`.

**Resultado:** 0 duplicados.

Todos los identificadores son únicos, por lo que `product_id` puede considerarse una candidata a clave primaria de la tabla.

**### 4.4. Validación de valores numéricos**

Se revisaron los valores iguales a cero y los valores negativos en las columnas numéricas.

**Valores iguales a cero:**

| Columna | Cantidad |
|---|---:|
| `product_name_lenght` | 0 |
| `product_description_lenght` | 0 |
| `product_photos_qty` | 0 |
| `product_weight_g` | 4 |
| `product_length_cm` | 0 |
| `product_height_cm` | 0 |
| `product_width_cm` | 0 |

No se encontraron valores negativos en ninguna de las columnas analizadas.

Se identificaron cuatro productos con peso igual a cero. Los cuatro pertenecen a la categoría `cama_mesa_banho` y presentan las mismas dimensiones: 30 × 25 × 30 cm.

Este patrón podría indicar un valor predeterminado o un problema de carga de datos. Sin embargo, no existe evidencia suficiente para determinar su origen.

**### 4.5. Estadísticas descriptivas**

Se calcularon estadísticas descriptivas para las variables numéricas.

| Estadístico | Nombre | Descripción | Fotografías | Peso (g) | Largo (cm) | Alto (cm) | Ancho (cm) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Cantidad | 32.341 | 32.341 | 32.341 | 32.949 | 32.949 | 32.949 | 32.949 |
| Promedio | 48,48 | 771,50 | 2,19 | 2.276,47 | 30,82 | 16,94 | 23,20 |
| Desviación estándar | 10,25 | 635,12 | 1,74 | 4.282,04 | 16,91 | 13,64 | 12,08 |
| Mínimo | 5 | 4 | 1 | 0 | 7 | 2 | 6 |
| 25 % | 42 | 339 | 1 | 300 | 18 | 8 | 15 |
| Mediana | 51 | 595 | 1 | 700 | 25 | 13 | 20 |
| 75 % | 57 | 972 | 3 | 1.900 | 38 | 21 | 30 |
| Máximo | 76 | 3.992 | 20 | 40.425 | 105 | 105 | 118 |

Se observa una diferencia considerable entre el promedio y la mediana del peso, lo que sugiere una distribución con valores elevados que pueden influir en el promedio.

También se identifican diferencias entre ambas medidas en la longitud de las descripciones y en las dimensiones físicas.

**### 4.6. Distribución de categorías**

Las 15 categorías con mayor cantidad de productos son:

| Categoría | Cantidad |
|---|---:|
| `cama_mesa_banho` | 3.029 |
| `esporte_lazer` | 2.867 |
| `moveis_decoracao` | 2.657 |
| `beleza_saude` | 2.444 |
| `utilidades_domesticas` | 2.335 |
| `automotivo` | 1.900 |
| `informatica_acessorios` | 1.639 |
| `brinquedos` | 1.411 |
| `relogios_presentes` | 1.329 |
| `telefonia` | 1.134 |
| `bebes` | 919 |
| `perfumaria` | 868 |
| `papelaria` | 849 |
| `fashion_bolsas_e_acessorios` | 849 |
| `cool_stuff` | 789 |

La categoría con mayor cantidad de productos es `cama_mesa_banho`.

**### 4.7. Investigación inicial de valores extremos**

Se inspeccionaron los diez productos con mayor peso y los diez con mayor volumen geométrico.

**Peso:**

- El valor máximo observado es 40.425 g (40,425 kg).
- Los siguientes nueve productos presentan un peso de exactamente 30.000 g.
- Los productos pertenecen a distintas categorías.

La repetición del valor de 30 kg merece una revisión posterior, aunque no permite concluir por sí sola que exista un error.

**Volumen geométrico:**

- El volumen máximo observado es de 296.208 cm³.
- Los diez productos con mayor volumen presentan valores cercanos a los 300.000 cm³.
- La categoría `moveis_sala` aparece en ocho de esos diez productos.

El volumen se calculó multiplicando largo × alto × ancho. Se utiliza como indicador del tamaño del producto y no necesariamente representa el volumen real de su embalaje.

---

## 5. Tabla `customers`

La tabla `customers` contiene información de los clientes del marketplace, incluyendo identificadores, códigos postales, ciudades y estados de residencia.

Su análisis permitirá incorporar la dimensión geográfica a los estudios posteriores sobre el desempeño logístico.

### 5.1. Estructura y tipos de datos

La tabla contiene **99.441 registros y 5 columnas**.

| Columna | Tipo de dato | Descripción |
|---|---|---|
| `customer_id` | str | Identificador del registro de cliente asociado a una orden. |
| `customer_unique_id` | str | Identificador único que permite reconocer a un mismo cliente en distintas órdenes. |
| `customer_zip_code_prefix` | int64 | Prefijo del código postal del cliente. |
| `customer_city` | str | Ciudad del cliente. |
| `customer_state` | str | Estado brasileño del cliente. |

El consumo de memoria informado por pandas es de aproximadamente 3,8 MB.

### 5.2. Valores faltantes

Se inspeccionó la presencia de valores nulos en las columnas de la tabla.

| Columna | Valores faltantes |
|---|---:|
| `customer_id` | 0 |
| `customer_unique_id` | 0 |
| `customer_zip_code_prefix` | 0 |
| `customer_city` | 0 |
| `customer_state` | 0 |

No se identificaron valores faltantes en ninguna de las columnas.

### 5.3. Validación de identificadores

Se comprobó la unicidad de `customer_id` y se analizó la cantidad de identificadores distintos en `customer_unique_id`.

| Validación | Resultado |
|---|---:|
| Total de registros | 99.441 |
| `customer_id` duplicados | 0 |
| ¿Todos los `customer_id` son únicos? | Sí |
| `customer_unique_id` distintos | 96.096 |
| Apariciones duplicadas de `customer_unique_id` | 3.345 |

Los resultados indican que `customer_id` no presenta duplicados y puede considerarse una candidata a clave primaria.

Por otro lado, `customer_unique_id` presenta valores repetidos, lo que permite identificar clientes asociados a múltiples registros.

### 5.4. Frecuencia de los clientes

Se analizó la cantidad de veces que aparece cada `customer_unique_id` para identificar clientes con más de un registro.

| Cantidad de registros por cliente | Cantidad de clientes |
|---:|---:|
| 1 | 93.099 |
| 2 | 2.745 |
| 3 | 203 |
| 4 | 30 |
| 5 | 8 |
| 6 | 6 |
| 7 | 3 |
| 9 | 1 |
| 17 | 1 |
| **Total** | **96.096** |

Se identificaron **2.997 clientes con más de un registro**.

La mayoría de los clientes recurrentes aparecen dos veces, mientras que la frecuencia máxima observada corresponde a un cliente con 17 registros.

Estos resultados permiten distinguir entre la cantidad de registros de la tabla y la cantidad de clientes únicos. No obstante, la frecuencia de aparición no permite determinar por sí sola cuántas compras fueron efectivamente completadas, ya que todavía no se han considerado los estados de las órdenes asociadas.

### 5.5. Validación de códigos postales

Se inspeccionó la columna `customer_zip_code_prefix`, considerando que representa un prefijo postal y no una variable cuantitativa.

| Validación | Resultado |
|---|---:|
| Códigos postales distintos | 14.994 |
| Códigos postales iguales a cero | 0 |
| Códigos postales negativos | 0 |

También se identificaron los diez prefijos postales más frecuentes:

| Código postal | Cantidad de registros |
|---:|---:|
| 22790 | 142 |
| 24220 | 124 |
| 22793 | 121 |
| 24230 | 117 |
| 22775 | 110 |
| 29101 | 101 |
| 13212 | 95 |
| 35162 | 93 |
| 22631 | 89 |
| 38400 | 87 |

No se identificaron valores iguales a cero ni negativos. La existencia de prefijos con mayor frecuencia no representa por sí misma una anomalía.

### 5.6. Distribución geográfica

Se analizaron las cantidades de ciudades y estados distintos, junto con la distribución de registros por ubicación.

Se identificaron:

- **4.119 ciudades distintas.**
- **27 estados distintos.**

Los estados con mayor cantidad de registros son:

| Estado | Cantidad de registros |
|---|---:|
| SP | 41.746 |
| RJ | 12.852 |
| MG | 11.635 |
| RS | 5.466 |
| PR | 5.045 |
| SC | 3.637 |
| BA | 3.380 |
| DF | 2.140 |
| ES | 2.033 |
| GO | 2.020 |

São Paulo concentra aproximadamente el 42 % de los registros, seguido por Río de Janeiro y Minas Gerais.

Las ciudades con mayor cantidad de registros son:

| Ciudad | Cantidad de registros |
|---|---:|
| sao paulo | 15.540 |
| rio de janeiro | 6.882 |
| belo horizonte | 2.773 |
| brasilia | 2.131 |
| curitiba | 1.521 |
| campinas | 1.444 |
| porto alegre | 1.379 |
| salvador | 1.245 |
| guarulhos | 1.189 |
| sao bernardo do campo | 938 |
| niteroi | 849 |
| santo andre | 797 |
| osasco | 746 |
| santos | 713 |
| goiania | 692 |

Los resultados muestran una concentración geográfica importante en determinadas regiones, especialmente en el estado de São Paulo.

### 5.7. Consistencia entre código postal, ciudad y estado

Se analizaron las combinaciones geográficas existentes y la relación entre los prefijos postales y las ubicaciones registradas.

| Validación | Resultado |
|---|---:|
| Combinaciones geográficas distintas | 15.034 |
| Prefijos asociados a más de una ciudad | 39 |
| Prefijos asociados a más de un estado | 0 |

Se identificaron 39 prefijos postales asociados a más de una ciudad. Esto no implica necesariamente una inconsistencia, ya que el dataset contiene únicamente los primeros cinco dígitos del CEP brasileño, cuyo formato completo está compuesto por ocho dígitos.

No se identificaron prefijos asociados a más de un estado.

### 5.8. Integridad referencial con `orders`

Se comprobó la correspondencia entre los identificadores de clientes de ambas tablas.

| Validación | Resultado |
|---|---:|
| `customer_id` de `orders` sin correspondencia en `customers` | 0 |
| `customer_id` de `customers` sin correspondencia en `orders` | 0 |

Todos los identificadores de clientes presentes en `orders` existen en `customers`, y todos los registros de `customers` tienen al menos una orden asociada.

Esto respalda la relación de uno a muchos entre ambas tablas:

- `customers.customer_id`: candidata a clave primaria.
- `orders.customer_id`: clave foránea candidata.

La relación permitirá incorporar la información geográfica de los clientes al análisis de las órdenes y sus tiempos de entrega.

### 5.9. Consideraciones para análisis posteriores

La inspección permitió identificar una concentración importante de clientes en determinados estados y ciudades, así como la existencia de clientes asociados a múltiples registros.

La información geográfica podrá utilizarse posteriormente para investigar posibles diferencias en el desempeño logístico según la ubicación de los clientes.

No se realizaron modificaciones ni eliminaciones de registros durante esta inspección.

---

## 6. Decisiones metodológicas hasta el momento

A partir de las inspecciones realizadas, se establecen los siguientes criterios:

1. Conservar los registros originales durante la etapa exploratoria.
2. No reemplazar los valores faltantes durante la inspección inicial.
3. No eliminar ni modificar registros únicamente por presentar valores iguales a cero o alejados del promedio.
4. No considerar automáticamente los valores de flete igual a cero como errores.
5. Tener en cuenta el estado de los pedidos al interpretar las fechas faltantes.
6. Evitar utilizar intervalos temporales cronológicamente inválidos en los cálculos de duración correspondientes.
7. Investigar las anomalías antes de definir cualquier tratamiento.
8. Considerar las limitaciones de información al seleccionar las variables para los análisis posteriores.
9. Investigar la relación entre las características físicas de los productos, los costos de envío y el desempeño logístico en etapas posteriores.

## 7. Próximos pasos

La inspección continuará con las demás tablas del dataset.

Posteriormente se evaluarán las relaciones entre ellas, se definirá el modelo de datos y se prepararán las tablas necesarias para el análisis logístico.

Los resultados de esta etapa podrán actualizarse a medida que se realicen nuevas validaciones y se obtenga mayor contexto sobre los datos.