"""
04_imputation_dedup.py
Imputación de valores nulos y eliminación de duplicados.

Estrategias:

- Variables Numéricas continuas : mediana (robusta a outliers)
- Variables Categóricas         : moda (valor más frecuente)
- Fechas NaT                    : se conservan como NaT, se ignorarán en el modelo
- Filas Duplicadas              : eliminación con el método de pandas drop_duplicates()
"""

import pandas as pd
import numpy as np
import sys
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH  = Path("1_data/2_cleaned/03_dates_cleaned.csv")
OUTPUT_PATH = Path("1_data/2_cleaned/04_imputed.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

METRICS_PATH = Path("4_outputs/2_metrics")
METRICS_PATH.mkdir(parents=True, exist_ok=True)

# ── Captura de resumen de resultados ──────────────────────────────────────────
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

report_file = open(METRICS_PATH / "04_imputation_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, low_memory=False)
print("=" * 60)
print("REPORTE DE IMPUTACIÓN Y ELIMINACIÓN DE DUPLICADOS")
print("=" * 60)
print(f"\nFilas cargadas  : {len(df):,}")
print(f"Nulos totales   : {df.isnull().sum().sum():,}") # el segundo sum() suma todos los valores de la Serie, devuelve un solo número
print(f"Duplicados      : {df.duplicated().sum():,}")

# ── 2. Eliminación de duplicados ──────────────────────────────────────────────
filas_antes = len(df)
df.drop_duplicates(inplace=True)
df.reset_index(drop=True, inplace=True)
filas_despues = len(df)

print(f"\n── Deduplicación ──────────────────────────────────────────")
print(f"  Filas antes    : {filas_antes:,}")
print(f"  Duplicados eliminados : {filas_antes - filas_despues:,}")
print(f"  Filas después  : {filas_despues:,}")

# ── 3. Definir columnas por tipo ──────────────────────────────────────────────
NUMERICAS = [
    "antiguedad_dias", "num_envios_6m", "valor_total_6m",
    "ticket_promedio", "dias_ultimo_envio", "num_reclamos_6m",
    "tasa_entrega_exitosa", "nps_score"
]
CATEGORICAS = ["ciudad", "tipo_cliente", "canal_principal"]
FECHAS_NAT  = ["fecha_registro", "anio_registro", "mes_registro", "dia_semana"]

# ── 4. Imputación de variables numéricas — mediana ───────────────────────────────
print(f"\n── Imputación de variables numéricas — mediana ──────────────────────────")
resumen_num = []
for col in NUMERICAS:
    n_nulos  = df[col].isnull().sum()
    mediana  = df[col].median()
    df[col]  = df[col].fillna(mediana)
    resumen_num.append({
        "variable" : col,
        "nulos_imp": n_nulos,
        "mediana"  : round(mediana, 4)
    })

df_resumen_num = pd.DataFrame(resumen_num).set_index("variable")
print(df_resumen_num.to_string())

# ── 5. Imputación de variables categóricas — moda ───────────────────────────────────────────
print(f"\n── Imputación de variables categóricas (moda) ───────────────────────────")
resumen_cat = []
for col in CATEGORICAS:
    n_nulos = df[col].isnull().sum()
    moda    = df[col].mode()[0]
    df[col] = df[col].fillna(moda)
    resumen_cat.append({
        "variable" : col,
        "nulos_imp": n_nulos,
        "moda"     : moda
    })

df_resumen_cat = pd.DataFrame(resumen_cat).set_index("variable")
print(df_resumen_cat.to_string())

# ── 6. Fechas NaT — conservar sin imputar ────────────────────────────────────
nat_count = df["fecha_registro"].isnull().sum()
print(f"\n── Fechas NaT conservadas (excluidas del modelo) ──────────")
print(f"  fecha_registro NaT : {nat_count:,}")
print(f"  Columnas excluidas del modelo: {FECHAS_NAT}")

# ── 7. Verificación final ─────────────────────────────────────────────────────
nulos_restantes = df[NUMERICAS + CATEGORICAS].isnull().sum().sum()
print(f"\n── Verificación final ─────────────────────────────────────")
print(f"  Nulos restantes en features  : {nulos_restantes:,}")
print(f"  Filas finales                : {len(df):,}")
print(f"  Tasa de churn conservada     : {df['churn'].mean():.2%}")

# ── 8. Guardar ────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_PATH, index=False)
print(f"\nDataset guardado en: {OUTPUT_PATH}")

# ── Cerrar captura ────────────────────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()

# ── Actualizar README ─────────────────────────────────────────────────────────
reporte_txt  = (METRICS_PATH / "04_imputation_report.txt").read_text(encoding="utf-8")
readme_path  = Path("README.md")
readme_actual = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

marca = "---\n## 🔧 Reporte de Imputación y Deduplicación\n"
if marca in readme_actual:
    readme_actual = readme_actual[:readme_actual.index(marca)]

readme_path.write_text(
    readme_actual + f"\n\n---\n## 🔧 Reporte de Imputación y Deduplicación\n```\n{reporte_txt}\n```\n",
    encoding="utf-8"
)

print("✅ Imputación y deduplicación completadas.")
print("✅ README.md actualizado.")