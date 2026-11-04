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

## 4. Decisiones metodológicas hasta el momento

A partir de las inspecciones realizadas, se establecen los siguientes criterios:

1. Conservar los registros originales durante la etapa exploratoria.
2. No eliminar valores únicamente por encontrarse alejados del promedio.
3. No considerar automáticamente los valores de flete igual a cero como errores.
4. Tener en cuenta el estado de los pedidos al interpretar las fechas faltantes.
5. Evitar utilizar intervalos temporales cronológicamente inválidos en los cálculos de duración correspondientes.
6. Investigar las anomalías antes de definir cualquier tratamiento.

## 5. Próximos pasos

La inspección continuará con las demás tablas del dataset.

Posteriormente se evaluarán las relaciones entre ellas, se definirá el modelo de datos y se prepararán las tablas necesarias para el análisis logístico.

Los resultados de esta etapa podrán actualizarse a medida que se realicen nuevas validaciones y se obtenga mayor contexto sobre los datos.