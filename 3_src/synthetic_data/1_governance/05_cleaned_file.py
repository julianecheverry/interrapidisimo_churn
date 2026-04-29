"""
05_cleaned_file.py
Consolida el pipeline de limpieza y genera el dataset final
de la capa cleaned/ listo para feature engineering.
"""

import pandas as pd
import sys
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH  = Path("1_data/2_cleaned/04_imputed.csv")
OUTPUT_PATH = Path("1_data/2_cleaned/05_cleaned_customers.csv")

METRICS_PATH = Path("4_outputs/2_metrics")
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

report_file = open(METRICS_PATH / "05_cleaned_layer_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, low_memory=False)
print("=" * 60)
print("REPORTE — CAPA CLEANED FINAL")
print("=" * 60)

# ── 2. Eliminar columnas excluidas del modelo ─────────────────────────────────
EXCLUIR = ["fecha_registro", "anio_registro", "mes_registro", "dia_semana_registro"]
df.drop(columns=EXCLUIR, inplace=True)

print(f"\n── Columnas eliminadas (fechas NaT / no usadas en modelo) ─")
for col in EXCLUIR:
    print(f"  ✖ {col}")

# ── 3. Resumen final del dataset ──────────────────────────────────────────────
print(f"\n── Resumen final ──────────────────────────────────────────")
print(f"  Filas                : {len(df):,}")
print(f"  Columnas             : {len(df.columns)}")
print(f"  Nulos restantes      : {df.isnull().sum().sum():,}")
print(f"  Tasa de churn        : {df['churn'].mean():.2%}")
print(f"\n── Columnas del dataset limpio ────────────────────────────")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col}")

# ── 4. Tipos de datos finales ─────────────────────────────────────────────────
print(f"\n── Tipos de datos finales ─────────────────────────────────")
print(df.dtypes.to_string())

# ── 5. Estadísticas descriptivas finales ──────────────────────────────────────
print(f"\n── Estadísticas descriptivas finales ──────────────────────")
print(df.describe(include="all").round(2).to_string())

# ── 6. Decisiones de limpieza documentadas ────────────────────────────────────
print(f"""
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
""")

# ── 7. Guardar ────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_PATH, index=False)
print(f"Dataset final guardado en: {OUTPUT_PATH}")

# ── Cerrar captura ────────────────────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()

# ── Actualizar README ─────────────────────────────────────────────────────────
reporte_txt   = (METRICS_PATH / "05_cleaned_layer_report.txt").read_text(encoding="utf-8")
readme_path   = Path("README.md")
readme_actual = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

marca = "---\n## ✅ Reporte — Capa Cleaned Final\n"
if marca in readme_actual:
    readme_actual = readme_actual[:readme_actual.index(marca)]

readme_path.write_text(
    readme_actual + f"\n\n---\n## ✅ Reporte — Capa Cleaned Final\n```\n{reporte_txt}\n```\n",
    encoding="utf-8"
)

print("✅ Capa cleaned/ consolidada.")
print("✅ README.md actualizado.")