"""
01_clean_real.py
Pipeline de limpieza completo para raw_data_customers_lpgr.csv
Pasos: carga → nulos → duplicados → fechas → PII → outliers → guardado
"""

import pandas as pd
import numpy as np
import hashlib
import sys
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH  = Path("1_data/real_data/1_raw/raw_data_customers_lpgr.csv")
OUTPUT_PATH = Path("1_data/real_data/2_cleaned/01_cleaned_real.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

METRICS_PATH = Path("4_outputs/real_data/2_metrics")
METRICS_PATH.mkdir(parents=True, exist_ok=True)

# ── Captura de output ─────────────────────────────────────────────────────────
class Tee:
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

report_file = open(METRICS_PATH / "01_clean_real_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga ──────────────────────────────────────────────────────────────────

# Alerta: Este dataset tiene problemas de formato (comillas, delimitadores) 
# que pueden causar que se cargue como una sola columna. 
# Se intentará cargar con diferentes parámetros para corregirlo.

filas = []
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    for linea in f:
        linea = linea.strip().strip('"')
        filas.append(linea.split(","))

df = pd.DataFrame(filas[1:], columns=filas[0])

# Convertir tipos de datos
df["churn_label"]      = pd.to_numeric(df["churn_label"],      errors="coerce")
df["monthly_spend"]    = pd.to_numeric(df["monthly_spend"],    errors="coerce")
df["total_shipments"]  = pd.to_numeric(df["total_shipments"],  errors="coerce")

print("=" * 60)
print("REPORTE DE LIMPIEZA — raw_data_customers_lpgr.csv")
print("=" * 60)
print(f"\nFilas cargadas  : {len(df):,}")
print(f"Columnas        : {list(df.columns)}")

# ── 2. Estandarizar nulos (NULL, N/A, vacíos → NaN) ──────────────────────────
# Limpiar comillas dobles en columnas y valores
df.columns = df.columns.str.strip().str.replace('"', '')
df = df.apply(lambda col: col.str.strip().str.replace('"', '') if col.dtype == "object" else col)

# Estandarizar nulos
df.replace(["NULL", "N/A", "", " "], np.nan, inplace=True)
print(f"\n── Columnas después de limpiar comillas ───────────────────")
print(list(df.columns))
print(f"\n── Nulos estandarizados (NULL/N/A → NaN) ──────────────────")
print(df.isnull().sum()[df.isnull().sum() > 0].to_string())

# ── 3. Eliminar duplicados ────────────────────────────────────────────────────
print(df.head(2))
print(df.dtypes)
print(df.index)

filas_antes = len(df)
df = df.drop_duplicates(subset=["customer_id"], keep="first")
df = df.reset_index(drop=True)
print(f"\n── Deduplicación ──────────────────────────────────────────")
print(f"  Filas antes              : {filas_antes:,}")
print(f"  Duplicados eliminados    : {filas_antes - len(df):,}")
print(f"  Filas después            : {len(df):,}")

# ── 4. Limpieza de fechas ─────────────────────────────────────────────────────
FORMATOS = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]

def parsear_fecha(valor):
    if pd.isnull(valor):
        return pd.NaT
    for fmt in FORMATOS:
        try:
            return pd.to_datetime(valor, format=fmt)
        except Exception:
            continue
    return pd.NaT

print(f"\n── Limpieza de fechas ─────────────────────────────────────")
for col in ["signup_date", "last_purchase_date"]:
    antes = df[col].isnull().sum()
    df[col] = df[col].apply(parsear_fecha)
    despues = df[col].isnull().sum()
    print(f"  {col:25s}: NaT antes={antes} | NaT después={despues}")

# Calcular antiguedad_dias y dias_ultimo_envio
hoy = pd.Timestamp("2025-06-20")
df["antiguedad_dias"]  = (hoy - df["signup_date"]).dt.days
df["dias_ultimo_envio"] = (hoy - df["last_purchase_date"]).dt.days

print(f"  antiguedad_dias    : calculado desde signup_date")
print(f"  dias_ultimo_envio  : calculado desde last_purchase_date")

# ── 5. Limpieza de monthly_spend ──────────────────────────────────────────────
print(f"\n── Limpieza de monthly_spend ──────────────────────────────")
df["monthly_spend"] = pd.to_numeric(df["monthly_spend"], errors="coerce")

# Valores negativos → NaN
negativos = (df["monthly_spend"] < 0).sum()
df.loc[df["monthly_spend"] < 0, "monthly_spend"] = np.nan
print(f"  Valores negativos → NaN : {negativos}")

# Outliers por IQR
q1  = df["monthly_spend"].quantile(0.25)
q3  = df["monthly_spend"].quantile(0.75)
iqr = q3 - q1
lim_sup = q3 + 1.5 * iqr
outliers = (df["monthly_spend"] > lim_sup).sum()
p99 = df["monthly_spend"].quantile(0.99)
df["monthly_spend"] = df["monthly_spend"].clip(upper=p99)
print(f"  Outliers detectados (IQR): {outliers}")
print(f"  Winsorización p99  : {p99:,.2f}")

# ── 6. Limpieza de total_shipments ────────────────────────────────────────────
print(f"\n── Limpieza de total_shipments ────────────────────────────")
df["total_shipments"] = pd.to_numeric(df["total_shipments"], errors="coerce")
q3_ship  = df["total_shipments"].quantile(0.75)
iqr_ship = q3_ship - df["total_shipments"].quantile(0.25)
lim_ship = q3_ship + 1.5 * iqr_ship
out_ship = (df["total_shipments"] > lim_ship).sum()
p99_ship = df["total_shipments"].quantile(0.99)
df["total_shipments"] = df["total_shipments"].clip(upper=p99_ship)
print(f"  Outliers detectados (IQR): {out_ship}")
print(f"  Winsorización p99  : {p99_ship:,.2f}")

# ── 7. Imputación de nulos ────────────────────────────────────────────────────
print(f"\n── Imputación de nulos ────────────────────────────────────")
for col in ["monthly_spend", "total_shipments", "antiguedad_dias", "dias_ultimo_envio"]:
    n_nulos = df[col].isnull().sum()
    mediana = df[col].median()
    df[col] = df[col].fillna(mediana)
    print(f"  {col:25s}: {n_nulos} nulos → mediana={mediana:.2f}")

# churn_label: imputar con moda
n_churn = df["churn_label"].isnull().sum()
moda_churn = df["churn_label"].mode()[0]
df["churn_label"] = df["churn_label"].fillna(moda_churn)
print(f"  {'churn_label':25s}: {n_churn} nulos → moda={moda_churn}")

# ── 8. Anonimización PII ──────────────────────────────────────────────────────
print(f"\n── Anonimización PII ──────────────────────────────────────")
PII_COLS = ["full_name", "email", "phone", "home_address"]

def sha256_hash(value):
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]

df["customer_id"] = df["customer_id"].apply(sha256_hash)
print(f"  customer_id hasheado (SHA-256)")

df.drop(columns=PII_COLS, inplace=True)
print(f"  Columnas PII eliminadas: {PII_COLS}")

# ── 9. Renombrar columnas para consistencia ───────────────────────────────────
df.rename(columns={
    "monthly_spend"  : "valor_mensual",
    "total_shipments": "num_envios_total",
    "churn_label"    : "churn",
    "signup_date"    : "fecha_registro",
    "last_purchase_date": "fecha_ultimo_envio"
}, inplace=True)

# ── 10. Resumen final ─────────────────────────────────────────────────────────
print(f"\n── Resumen final ──────────────────────────────────────────")
print(f"  Filas finales   : {len(df):,}")
print(f"  Columnas        : {list(df.columns)}")
print(f"  Nulos restantes : {df.isnull().sum().sum():,}")
print(f"  Tasa de churn   : {df['churn'].mean():.2%}")
print(f"\n{df.describe().round(2).to_string()}")

# ── 11. Guardar ───────────────────────────────────────────────────────────────
print(f"Guardando en: {OUTPUT_PATH.resolve()}")
df.to_csv(OUTPUT_PATH, index=False)
print(f"Filas guardadas: {len(df)}")
print(f"\nDataset limpio guardado en: {OUTPUT_PATH}")

# ── Cerrar captura ────────────────────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()
print("✅ Limpieza completada.")
print(f"✅ Reporte guardado en: {METRICS_PATH / '01_clean_real_report.txt'}")