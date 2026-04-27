

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


---
## 📅 Reporte de Limpieza de Fechas
```
============================================================
REPORTE DE LIMPIEZA DE FECHAS
============================================================

Filas cargadas : 10,300

── Diagnóstico previo ─────────────────────────────────────
  Fechas estándar (YYYY-MM-DD) : 9,268
  Fechas no estándar           : 1,032
  Nulos                        : 0

── Aplicando parseo multi-formato ─────────────────────────
  Fechas ajustadas exitosamente : 10,065
  Fechas no ajustables (→ NaT)  : 235
  Tasa de recuperación de fechas: 97.72%

── Columnas derivadas creadas ─────────────────────────────
  anio_registro : {np.int64(2019): 2022, np.int64(2020): 1994, np.int64(2021): 1955, np.int64(2022): 2082, np.int64(2023): 2012}
  mes_registro  : valores 1-12, nulos=235
  dia_semana    : valores 0-6,  nulos=235

── Muestra de fechas recuperadas ──────────────────────────
     original   ajustada
0  2022-11-06 2022-11-06
1  11-08-2023 2023-11-08
2  2020-08-22 2020-08-22
3  2021-07-17 2021-07-17
4  2019-05-07 2019-05-07
5  2023-06-23 2023-06-23
6  2020-12-24 2020-12-24
7  2021-06-12 2021-06-12

Dataset guardado en: 1_data\2_cleaned\03_dates_cleaned.csv

```


---
## 🔧 Reporte de Imputación y Deduplicación
```
============================================================
REPORTE DE IMPUTACIÓN Y ELIMINACIÓN DE DUPLICADOS
============================================================

Filas cargadas  : 10,300
Nulos totales   : 9,629
Duplicados      : 300

── Deduplicación ──────────────────────────────────────────
  Filas antes    : 10,300
  Duplicados eliminados : 300
  Filas después  : 10,000

── Imputación de variables numéricas — mediana ──────────────────────────
                      nulos_imp      mediana
variable                                    
antiguedad_dias             808    1273.0000
num_envios_6m               753       8.0000
valor_total_6m              760  172600.0000
ticket_promedio             755   15900.0000
dias_ultimo_envio           717      31.0000
num_reclamos_6m             803       1.0000
tasa_entrega_exitosa        794       0.8788
nps_score                   797       6.5000

── Imputación de variables categóricas (moda) ───────────────────────────
                 nulos_imp     moda
variable                           
ciudad                 758   Bogotá
tipo_cliente           715  Natural
canal_principal        786      App

── Fechas NaT conservadas (excluidas del modelo) ──────────
  fecha_registro NaT : 226
  Columnas excluidas del modelo: ['fecha_registro', 'anio_registro', 'mes_registro', 'dia_semana']

── Verificación final ─────────────────────────────────────
  Nulos restantes en features  : 0
  Filas finales                : 10,000
  Tasa de churn conservada     : 30.83%

Dataset guardado en: 1_data\2_cleaned\04_imputed.csv

```


---
## ✅ Reporte — Capa Cleaned Final
```
============================================================
REPORTE — CAPA CLEANED FINAL
============================================================

── Columnas eliminadas (fechas NaT / no usadas en modelo) ─
  ✖ fecha_registro
  ✖ anio_registro
  ✖ mes_registro
  ✖ dia_semana_registro

── Resumen final ──────────────────────────────────────────
  Filas                : 10,000
  Columnas             : 14
  Nulos restantes      : 0
  Tasa de churn        : 30.83%

── Columnas del dataset limpio ────────────────────────────
   1. customer_id
   2. antiguedad_dias
   3. ciudad
   4. tipo_cliente
   5. canal_principal
   6. tiene_contrato
   7. num_envios_6m
   8. valor_total_6m
   9. ticket_promedio
  10. dias_ultimo_envio
  11. num_reclamos_6m
  12. tasa_entrega_exitosa
  13. nps_score
  14. churn

── Tipos de datos finales ─────────────────────────────────
customer_id                 str
antiguedad_dias         float64
ciudad                      str
tipo_cliente                str
canal_principal             str
tiene_contrato            int64
num_envios_6m           float64
valor_total_6m          float64
ticket_promedio         float64
dias_ultimo_envio       float64
num_reclamos_6m         float64
tasa_entrega_exitosa    float64
nps_score               float64
churn                     int64

── Estadísticas descriptivas finales ──────────────────────
             customer_id  antiguedad_dias  ciudad tipo_cliente canal_principal  tiene_contrato  num_envios_6m  valor_total_6m  ticket_promedio  dias_ultimo_envio  num_reclamos_6m  tasa_entrega_exitosa  nps_score     churn
count              10000         10000.00   10000        10000           10000        10000.00       10000.00        10000.00         10000.00           10000.00         10000.00              10000.00   10000.00  10000.00
unique             10000              NaN      10            3               4             NaN            NaN             NaN              NaN                NaN              NaN                   NaN        NaN       NaN
top     eba190fb9ed9cc38              NaN  Bogotá      Natural             App             NaN            NaN             NaN              NaN                NaN              NaN                   NaN        NaN       NaN
freq                   1              NaN    3567         5294            3959             NaN            NaN             NaN              NaN                NaN              NaN                   NaN        NaN       NaN
mean                 NaN          1275.94     NaN          NaN             NaN            0.35           9.20      1076646.90         22712.49              43.59             1.19                  0.88       6.42      0.31
std                  NaN           506.98     NaN          NaN             NaN            0.48           6.18      5232119.28         16134.41              43.29             1.05                  0.07       2.01      0.46
min                  NaN           367.00     NaN          NaN             NaN            0.00           0.00            0.00          3000.00               1.00             0.00                  0.61       0.00      0.00
25%                  NaN           855.00     NaN          NaN             NaN            0.00           4.00        47500.00         11900.00              14.00             0.00                  0.83       5.10      0.00
50%                  NaN          1273.00     NaN          NaN             NaN            0.00           8.00       172600.00         15900.00              31.00             1.00                  0.88       6.50      0.00
75%                  NaN          1694.00     NaN          NaN             NaN            1.00          14.00       422425.00         29900.00              59.00             2.00                  0.93       7.80      1.00
max                  NaN          2191.00     NaN          NaN             NaN            1.00          33.00     49999000.00         92400.00             365.00             6.00                  1.00      10.00      1.00

── Decisiones técnicas de limpieza ────────────────────────
  1. ANONIMIZACIÓN
     - Columnas PII eliminadas    : nombre, email, telefono
     - customer_id                : hasheado con SHA-256 (16 caracteres)

  2. FECHAS
     - Formatos corruptos parseados con 5 formatos alternativos
     - Fechas no parseables       : conservadas como NaT
     - Columnas derivadas         : excluidas del modelo

  3. NULOS
     - Numéricas continuas        : imputadas con mediana
     - Categóricas                : imputadas con moda
     - Fechas NaT                 : excluidas del modelo

  4. DUPLICADOS
     - Método                     : drop_duplicates() exacto
     - Filas eliminadas           : ~300 (3% del total)

  5. OUTLIERS
     - valor_total_6m             : 325 outliers extremos detectados
     - Tratamiento                : conservados en dataset limpio (se
       tratarán en feature engineering)

Dataset final guardado en: 1_data\2_cleaned\05_cleaned_customers.csv

```




---
## 🤖 Reporte de Modelado
```
============================================================
REPORTE DE MODELADO — CHURN PREDICTION
============================================================

Filas cargadas  : 10,000
Tasa de churn   : 30.83%

── Winsorización valor_total_6m ───────────────────────────
  Percentil 99   : 34,425,300
  Valor máximo post-winsorización: 34,425,300

── Features adicionales creadas ───────────────────────────
  ratio_reclamos_envios  : reclamos / (envíos + 1)
  segmento_recencia      : categorización de dias_ultimo_envio
  Distribución segmento_recencia:
segmento_recencia
reciente     3893
activo       2772
en_riesgo    2099
inactivo     1236

── Features del modelo ────────────────────────────────────
  Numéricas   (9): ['antiguedad_dias', 'num_envios_6m', 'valor_total_6m', 'ticket_promedio', 'dias_ultimo_envio', 'num_reclamos_6m', 'tasa_entrega_exitosa', 'nps_score', 'ratio_reclamos_envios']
  Categóricas (5): ['ciudad', 'tipo_cliente', 'canal_principal', 'tiene_contrato', 'segmento_recencia']

── Split train/test ───────────────────────────────────────
  Train : 7,000 filas | churn=30.83%
  Test  : 3,000  filas | churn=30.83%

── Entrenando pipeline (GridSearchCV, 5-fold, scoring=recall)...
Fitting 5 folds for each of 15 candidates, totalling 75 fits

── Mejores parámetros ─────────────────────────────────────
  C           : 1
  l1_ratio    : 0.9
  Recall CV (train): 0.4546

── Métricas en test ───────────────────────────────────────
  AUC-ROC : 0.7749

Matriz de confusión:
[[1883  192]
 [ 541  384]]

Classification Report:
              precision    recall  f1-score   support

      Activo       0.78      0.91      0.84      2075
       Churn       0.67      0.42      0.51       925

    accuracy                           0.76      3000
   macro avg       0.72      0.66      0.67      3000
weighted avg       0.74      0.76      0.74      3000


── Búsqueda de umbral óptimo (max Recall clase Churn) ─────
          recall  precision        f1
umbral                               
0.20    0.844324   0.436557  0.575534
0.22    0.809730   0.447967  0.576819
0.24    0.781622   0.462276  0.580956
0.26    0.756757   0.475867  0.584307
0.28    0.727568   0.488744  0.584709
0.30    0.701622   0.499615  0.583633
0.32    0.669189   0.507793  0.577425
0.34    0.651892   0.528947  0.584019
0.36    0.628108   0.554389  0.588951
0.38    0.597838   0.569516  0.583333
0.40    0.568649   0.594350  0.581215
0.42    0.537297   0.606838  0.569954
0.44    0.502703   0.623324  0.556553
0.46    0.475676   0.638607  0.545229
0.48    0.443243   0.653907  0.528351
0.50    0.415135   0.666667  0.511659
0.52    0.383784   0.686654  0.492372
0.54    0.360000   0.713062  0.478448
0.56    0.328649   0.722090  0.451709
0.58    0.311351   0.730964  0.436694

  Umbral óptimo seleccionado: 0.28

── Métricas con umbral=0.28 ────────────────────
  AUC-ROC : 0.7749
[[1371  704]
 [ 252  673]]
              precision    recall  f1-score   support

      Activo       0.84      0.66      0.74      2075
       Churn       0.49      0.73      0.58       925

    accuracy                           0.68      3000
   macro avg       0.67      0.69      0.66      3000
weighted avg       0.73      0.68      0.69      3000


── Métricas de impacto de negocio ─────────────────────────

── Supuestos de negocio (configurables) ───────────────────
  LTV_PROMEDIO             : 345,200.00
  COSTO_INTERVENCION       : 15,000.00
  TASA_RETENCION           : 0.30

── Métricas de impacto ────────────────────────────────────
  Clientes churn detectados (TP) : 673
  Falsos positivos (FP)          : 704
  Clientes a contactar           : 1,377
  Clientes retenidos estimados   : 413
  Costo total campaña            : $20,655,000 COP
  Ingreso retenido estimado      : $142,567,600 COP
  ROI estimado del modelo        : 590.2%

  ⚠ Supuestos estimados — validar con áreas comercial y financiera para mayor precisión en métricas de negocio

Gráfica guardada en: 4_outputs\1_figures\02_model_evaluation.png

── Pipeline guardado en: 1_data\3_features\pipeline.pkl
  Verificación predict() desde .pkl: [0 0 0 1 0]

```
