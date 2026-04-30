"""
02_anonymization.py
Buenas prácticas de tratamiento de datos sensibles (ley 1582 de 2012)
Anonimización de variables sensibles (PII):
- nombre, email, telefono → eliminadas del dataset
- customer_id → reemplazado por hash SHA-256
"""

import pandas as pd
import hashlib # Para hashing de variable customer_id
import sys
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH  = Path("1_data/synthetic_data/1_raw/raw_data_customers.csv")
OUTPUT_PATH = Path("1_data/synthetic_data/2_cleaned/02_anonymized.csv")
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

METRICS_PATH = Path("4_outputs/synthetic_data/2_metrics")
METRICS_PATH.mkdir(parents=True, exist_ok=True)

# ── Captura de resultados en archivo .txt ────────────────────────────────────────────
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

report_file = open(METRICS_PATH / "02_anonymization_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, low_memory=False)
print("=" * 60)
print("REPORTE DE ANONIMIZACIÓN")
print("=" * 60)
print(f"\nFilas cargadas : {len(df):,}")
print(f"Columnas antes de la anonimización: {list(df.columns)}")

# ── 2. Identificar PII ────────────────────────────────────────────────────────
PII_COLS    = ["nombre", "email", "telefono"]
ID_COL      = "customer_id"

print(f"\n── Variables PII identificadas ────────────────────────────")
for col in PII_COLS:
    print(f"  ✖ {col:15s} → será eliminada")
print(f"  ⚙ {ID_COL:15s} → será hasheada (SHA-256)")

# ── 3. Hashear customer_id ────────────────────────────────────────────────────
# Aplica la función de hash a cada valor de customer_id para que genere un hash 
# único de 16 caracteres (en lugar del ID original)
# Esto garantiza que no se pueda revertir al ID original, protegiendo la identidad
# del cliente.
def sha256_hash(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]

# Aplicar la función fila por fila a la columna customer_id
df[ID_COL] = df[ID_COL].apply(sha256_hash)

print(f"\n── Muestra de customer_id hasheado ────────────────────────")
print(df[ID_COL].head(5).to_string())

# ── 4. Eliminar columnas PII ──────────────────────────────────────────────────
df.drop(columns=PII_COLS, inplace=True)

print(f"\n── Columnas después de anonimización ──────────────────────")
print(list(df.columns))
print(f"\nColumnas eliminadas : {PII_COLS}")
print(f"Columnas restantes  : {len(df.columns)}")
print(f"Filas conservadas   : {len(df):,}")

# ── 5. Verificación: confirmar que no queda PII ───────────────────────────────
print(f"\n── Verificación PII ───────────────────────────────────────")
pii_restante = [col for col in PII_COLS if col in df.columns]
if pii_restante:
    print(f"  ⚠ Columnas PII aún presentes: {pii_restante}")
else:
    print("  ✅ Ninguna columna PII presente en el dataset.")

# ── 6. Guardar ────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_PATH, index=False)
print(f"\nDataset anonimizado guardado en: {OUTPUT_PATH}")

# ── Cerrar captura en archivo .txt ────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()

# ── Actualizar README ─────────────────────────────────────────────────────────
reporte_txt = (METRICS_PATH / "02_anonymization_report.txt").read_text(encoding="utf-8")
readme_path = Path("README.md")
readme_actual = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

marca = "---\n## 🔒 Reporte de Anonimización\n"
if marca in readme_actual:
    readme_actual = readme_actual[:readme_actual.index(marca)]

readme_path.write_text(
    readme_actual + f"\n\n---\n## 🔒 Reporte de Anonimización\n```\n{reporte_txt}\n```\n",
    encoding="utf-8"
)

print("✅ Anonimización completada.")
print("✅ README.md actualizado.")