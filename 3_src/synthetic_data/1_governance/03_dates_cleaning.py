"""
03_date_cleaning.py
Limpieza y estandarización de la columna fecha_registro, para las columnas con 
formatos mixtos o corruptos.
Estrategia:
- Intentar ajustar desde múltiples formatos conocidos y compatibles con pandas.to_datetime()
- Fechas imposibles o no parseables → NaT (se imputarán)
- Generar columnas derivadas: año, mes, día_semana. De utilidad para análisis posteriores.
"""

import pandas as pd
import sys
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH  = Path("1_data/synthetic_data/2_cleaned/02_anonymized.csv")
OUTPUT_PATH = Path("1_data/synthetic_data/2_cleaned/03_dates_cleaned.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

METRICS_PATH = Path("4_outputs/synthetic_data/2_metrics")
METRICS_PATH.mkdir(parents=True, exist_ok=True)

# ── Captura de resumen de resultados ─────────────────────────────────────────
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

report_file = open(METRICS_PATH / "03_date_cleaning_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, low_memory=False)
print("=" * 60)
print("REPORTE DE LIMPIEZA DE FECHAS")
print("=" * 60)
print(f"\nFilas cargadas : {len(df):,}")

total_fechas        = len(df)
fechas_originales   = df["fecha_registro"].copy()

# ── 2. Diagnóstico previo ─────────────────────────────────────────────────────
estandar = df["fecha_registro"].str.match(r"^\d{4}-\d{2}-\d{2}$", na=False).sum()
print(f"\n── Diagnóstico previo ─────────────────────────────────────")
print(f"  Fechas estándar (YYYY-MM-DD) : {estandar:,}")
print(f"  Fechas no estándar           : {total_fechas - estandar:,}")
print(f"  Nulos                        : {df['fecha_registro'].isnull().sum():,}")

# ── 3. Parseo multi-formato ───────────────────────────────────────────────────
FORMATOS = [
    "%Y-%m-%d",   # estándar YYYY-MM-DD
    "%d/%m/%Y",   # DD/MM/YYYY
    "%m-%d-%Y",   # MM-DD-YYYY
    "%Y%m%d",     # YYYYMMDD
    "%d %b %Y",   # 15 Jan 2022
]

def parsear_fecha(valor):
    """Intenta ajustar una fecha con múltiples formatos. Retorna NaT si falla."""
    if pd.isnull(valor):
        return pd.NaT
    for fmt in FORMATOS:
        try:
            fecha = pd.to_datetime(valor, format=fmt)
            # Validar que la fecha obtenida esté en un rango razonable (2019-2024)
            if pd.Timestamp("2019-01-01") <= fecha <= pd.Timestamp("2024-12-31"):
                return fecha
        except Exception:
            continue
    return pd.NaT  # imposible de ajustar o fuera de rango

print(f"\n── Aplicando parseo multi-formato ─────────────────────────")
df["fecha_registro"] = df["fecha_registro"].apply(parsear_fecha)

# ── 4. Diagnóstico posterior ──────────────────────────────────────────────────
parseadas  = df["fecha_registro"].notna().sum()
no_parsead = df["fecha_registro"].isna().sum()

print(f"  Fechas ajustadas exitosamente : {parseadas:,}")
print(f"  Fechas no ajustables (→ NaT)  : {no_parsead:,}")
print(f"  Tasa de recuperación de fechas: {parseadas/total_fechas:.2%}")

# ── 5. Columnas derivadas ─────────────────────────────────────────────────────
df["anio_registro"] = df["fecha_registro"].dt.year.astype("Int64")
df["mes_registro"]  = df["fecha_registro"].dt.month.astype("Int64")
df["dia_semana_registro"] = df["fecha_registro"].dt.dayofweek.astype("Int64")  # 0=Lunes

print(f"\n── Columnas derivadas creadas ─────────────────────────────")
print(f"  anio_registro : {df['anio_registro'].value_counts().sort_index().to_dict()}")
print(f"  mes_registro  : valores 1-12, nulos={df['mes_registro'].isna().sum()}")
print(f"  dia_semana    : valores 0-6,  nulos={df['dia_semana_registro'].isna().sum()}")

# ── 6. Muestra de fechas recuperadas ─────────────────────────────────────────
print(f"\n── Muestra de fechas recuperadas ──────────────────────────")
muestra = pd.DataFrame({
    "original" : fechas_originales,
    "ajustada" : df["fecha_registro"]
}).dropna(subset=["ajustada"]).head(8)
print(muestra.to_string())

# ── 7. Guardar ────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_PATH, index=False)
print(f"\nDataset guardado en: {OUTPUT_PATH}")

# ── Cerrar captura ────────────────────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()

# ── Actualizar README ─────────────────────────────────────────────────────────
reporte_txt = (METRICS_PATH / "03_date_cleaning_report.txt").read_text(encoding="utf-8")
readme_path = Path("README.md")
readme_actual = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

marca = "---\n## 📅 Reporte de Limpieza de Fechas\n"
if marca in readme_actual:
    readme_actual = readme_actual[:readme_actual.index(marca)]

readme_path.write_text(
    readme_actual + f"\n\n---\n## 📅 Reporte de Limpieza de Fechas\n```\n{reporte_txt}\n```\n",
    encoding="utf-8"
)

print("✅ Limpieza de fechas completada.")
print("✅ README.md actualizado.")