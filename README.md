

---
## 📊 Reporte de Calidad — Data Raw
```
============================================================
REPORTE DE CALIDAD — raw_data_customers.csv
============================================================

Dimensiones        : 10,300 filas × 18 columnas
Duplicados exactos : 300
Tasa de registros marcados como churn      : 30.75%

── Tipos y nulos por columna ──────────────────────────────
                        dtype  nulos  porcentaje_nulos  registros_unicos
customer_id               str      0              0.00             10000
nombre                    str      0              0.00              9838
email                     str      0              0.00              9561
telefono                  str      0              0.00             10000
fecha_registro            str      0              0.00              2546
antiguedad_dias       float64    822              7.98              1809
ciudad                    str    784              7.61                10
tipo_cliente              str    737              7.16                 3
canal_principal           str    807              7.83                 4
tiene_contrato          int64      0              0.00                 2
num_envios_6m         float64    776              7.53                33
valor_total_6m        float64    783              7.60              3494
ticket_promedio       float64    770              7.48               731
dias_ultimo_envio     float64    743              7.21               262
num_reclamos_6m       float64    827              8.03                 7
tasa_entrega_exitosa  float64    812              7.88              2717
nps_score             float64    828              8.04               101
churn                   int64      0              0.00                 2

── Estadísticas descriptivas (variables numéricas) ──────────────────
       antiguedad_dias  tiene_contrato  num_envios_6m  valor_total_6m  ticket_promedio  dias_ultimo_envio  num_reclamos_6m  tasa_entrega_exitosa  nps_score     churn
count          9478.00        10300.00        9524.00         9517.00          9530.00            9557.00           9473.0               9488.00    9472.00  10300.00
mean           1276.05            0.35           9.31      1147234.33         23253.75              44.56              1.2                  0.88       6.41      0.31
std             528.59            0.48           6.43      5412622.43         16633.58              44.81              1.1                  0.08       2.09      0.46
min             367.00            0.00           0.00            0.00          3000.00               1.00              0.0                  0.61       0.00      0.00
25%             819.25            0.00           4.00        44700.00         11500.00              13.00              0.0                  0.83       5.00      0.00
50%            1274.00            0.00           8.00       171200.00         15900.00              31.00              1.0                  0.88       6.50      0.00
75%            1729.00            1.00          14.00       447600.00         32900.00              62.00              2.0                  0.93       8.00      1.00
max            2191.00            1.00          33.00     49999000.00         92400.00             365.00              6.0                  1.00      10.00      1.00

── Outliers por variable numérica continua (método IQR) ───
                            Q1         Q3        IQR    lim_inf     lim_sup  n_outliers  pct_out
variable                                                                                        
antiguedad_dias         819.25    1729.00     909.75    -545.38     3093.62           0     0.00
num_envios_6m             4.00      14.00      10.00     -11.00       29.00          10     0.10
valor_total_6m        44700.00  447600.00  402900.00 -559650.00  1051950.00         389     4.09
ticket_promedio       11500.00   32900.00   21400.00  -20600.00    65000.00         190     1.99
dias_ultimo_envio        13.00      62.00      49.00     -60.50      135.50         441     4.61
num_reclamos_6m           0.00       2.00       2.00      -3.00        5.00           7     0.07
tasa_entrega_exitosa      0.83       0.93       0.11       0.66        1.10          35     0.37
nps_score                 5.00       8.00       3.00       0.50       12.50          30     0.32

── Muestra de fechas potencialmente corruptas ─────────────
Fechas no estándar (no YYYY-MM-DD): 1,032
fecha_registro
99/99/9999     235
20201006         3
20231124         3
07/10/2020       2
12-06-2022       2
20230513         2
08-07-2022       2
10 Mar 2023      2
26/05/2019       2
11/07/2023       2
Name: count, dtype: int64

── Distribución de categóricas ────────────────────────────

ciudad:
ciudad
Bogotá          2893
Medellín        1891
Cali            1436
Barranquilla     972
NaN              784
Cartagena        669
Name: count, dtype: int64

tipo_cliente:
tipo_cliente
Natural      4721
Empresa      2921
Ecommerce    1921
NaN           737
Name: count, dtype: int64

canal_principal:
canal_principal
App             3262
Web             2821
Punto físico    2485
API              925
NaN              807
Name: count, dtype: int64

tiene_contrato:
tiene_contrato
0    6673
1    3627
Name: count, dtype: int64

Gráfica guardada en: 4_outputs\1_figures\01_eda_overview.png

✅ EDA completado.

```


---
## 🔒 Reporte de Anonimización
```
============================================================
REPORTE DE ANONIMIZACIÓN
============================================================

Filas cargadas : 10,300
Columnas antes de la anonimización: ['customer_id', 'nombre', 'email', 'telefono', 'fecha_registro', 'antiguedad_dias', 'ciudad', 'tipo_cliente', 'canal_principal', 'tiene_contrato', 'num_envios_6m', 'valor_total_6m', 'ticket_promedio', 'dias_ultimo_envio', 'num_reclamos_6m', 'tasa_entrega_exitosa', 'nps_score', 'churn']

── Variables PII identificadas ────────────────────────────
  ✖ nombre          → será eliminada
  ✖ email           → será eliminada
  ✖ telefono        → será eliminada
  ⚙ customer_id     → será hasheada (SHA-256)

── Muestra de customer_id hasheado ────────────────────────
0    eba190fb9ed9cc38
1    4ac66c326fa997c5
2    d82c91ffabf02a54
3    90867e0226bd9f39
4    ec8f73f35fe3a31f

── Columnas después de anonimización ──────────────────────
['customer_id', 'fecha_registro', 'antiguedad_dias', 'ciudad', 'tipo_cliente', 'canal_principal', 'tiene_contrato', 'num_envios_6m', 'valor_total_6m', 'ticket_promedio', 'dias_ultimo_envio', 'num_reclamos_6m', 'tasa_entrega_exitosa', 'nps_score', 'churn']

Columnas eliminadas : ['nombre', 'email', 'telefono']
Columnas restantes  : 15
Filas conservadas   : 10,300

── Verificación PII ───────────────────────────────────────
  ✅ Ninguna columna PII presente en el dataset.

Dataset anonimizado guardado en: 1_data\2_cleaned\02_anonymized.csv

```
