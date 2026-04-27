"""
01_eda_quality_report.py
Análisis exploratorio y reporte de calidad del dataset crudo.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# ── Imprimir y guardar informe de resultados en archivo txt ───────────────────────
import sys

METRICS_PATH = Path("4_outputs/2_metrics")
METRICS_PATH.mkdir(parents=True, exist_ok=True)

class Tee:
    """Escribe simultáneamente en consola y en archivo txt."""
    def __init__(self, *files):
        self.files = files
    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()
    def flush(self):
        for f in self.files:
            f.flush()

report_file = open(METRICS_PATH / "01_quality_report.txt", "w", encoding="utf-8")
sys.stdout = Tee(sys.stdout, report_file)

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH  = Path("1_data/1_raw/raw_data_customers.csv")
FIG_PATH    = Path("4_outputs/1_figures")
FIG_PATH.mkdir(parents=True, exist_ok=True)

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, low_memory=False)
print("=" * 60)
print("REPORTE DE CALIDAD — raw_data_customers.csv")
print("=" * 60)
print(f"\nDimensiones        : {df.shape[0]:,} filas × {df.shape[1]} columnas")
print(f"Duplicados exactos : {df.duplicated().sum():,}")
print(f"Tasa de registros marcados como churn      : {df['churn'].mean():.2%}")

# ── 2. Tipos de datos y nulos ─────────────────────────────────────────────────
print("\n── Tipos y nulos por columna ──────────────────────────────")
resumen = pd.DataFrame({
    "dtype"      : df.dtypes,
    "nulos"      : df.isnull().sum(),
    "porcentaje_nulos"  : (df.isnull().sum() / len(df) * 100).round(2),
    "registros_unicos"     : df.nunique(),
})
print(resumen.to_string())

# ── 3. Estadísticas descriptivas numéricas ────────────────────────────────────
print("\n── Estadísticas descriptivas (variables numéricas) ──────────────────")
num_cols = df.select_dtypes(include=np.number).columns.tolist()
print(df[num_cols].describe().round(2).to_string())

# ── 4. Detección de outliers (IQR) — todas las numéricas continuas ────────────
continuas = [
    "antiguedad_dias", "num_envios_6m", "valor_total_6m",
    "ticket_promedio", "dias_ultimo_envio", "num_reclamos_6m",
    "tasa_entrega_exitosa", "nps_score"
]

print("\n── Outliers por variable numérica continua (método IQR) ───")
resumen_outliers = []
for col in continuas:
    serie = df[col].dropna()
    q1    = serie.quantile(0.25)
    q3    = serie.quantile(0.75)
    iqr   = q3 - q1
    lim_inf = q1 - 1.5 * iqr
    lim_sup = q3 + 1.5 * iqr
    n_out   = ((serie < lim_inf) | (serie > lim_sup)).sum()
    resumen_outliers.append({
        "variable"  : col,
        "Q1"        : round(q1, 2),
        "Q3"        : round(q3, 2),
        "IQR"       : round(iqr, 2),
        "lim_inf"   : round(lim_inf, 2),
        "lim_sup"   : round(lim_sup, 2),
        "n_outliers": n_out,
        "pct_out"   : round(n_out / len(serie) * 100, 2),
    })

df_outliers = pd.DataFrame(resumen_outliers).set_index("variable")
print(df_outliers.to_string())

# ── 5. Revisión de consistencia en el formato de fechas ───────────────────────
print("\n── Muestra de fechas potencialmente corruptas ─────────────")
# Detecta fechas que NO siguen el formato YYYY-MM-DD (ej. 2023-08-15)
# con patrones regex y el operador de negación ~
fechas_no_estandar = df[~df["fecha_registro"].str.match(
    r"^\d{4}-\d{2}-\d{2}$", na=False
)]
print(f"Fechas no estándar (no YYYY-MM-DD): {len(fechas_no_estandar):,}")
print(fechas_no_estandar["fecha_registro"].value_counts().head(10))

# ── 6. Distribución de variables categóricas ──────────────────────────────────
print("\n── Distribución de categóricas ────────────────────────────")
for col in ["ciudad","tipo_cliente","canal_principal","tiene_contrato"]:
    print(f"\n{col}:\n{df[col].value_counts(dropna=False).head(6)}")

# ── 7. Gráficas ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(16, 10))
fig.suptitle("EDA — raw_data_customers", fontsize=14, fontweight="bold")

# 7.1 Distribución variable churn
axes[0,0].bar(["Activo (0)","Churn (1)"],
              df["churn"].value_counts().sort_index().values,
              color=["#2ecc71","#e74c3c"])
axes[0,0].set_title("Distribución variable Churn")
axes[0,0].set_ylabel("Clientes")

# 7.2 Nulos por columna
nulos = df.isnull().sum().sort_values(ascending=False)
nulos = nulos[nulos > 0]
axes[0,1].barh(nulos.index, nulos.values, color="#3498db")
axes[0,1].set_title("Nulos por columna")
axes[0,1].set_xlabel("Cantidad")

# 7.3 Boxplots de todas las continuas
axes[0,2].boxplot(
    [df[col].dropna() for col in continuas],
    labels=[c.replace("_"," ") for c in continuas],
    patch_artist=True,
    boxprops=dict(facecolor="#9b59b6", color="#2c3e50")
)
axes[0,2].set_title("Outliers — variables continuas")
axes[0,2].tick_params(axis="x", rotation=45)

# 7.4 Net Promoter Score vs Churn
df.boxplot(column="nps_score", by="churn", ax=axes[1,0], 
           boxprops=dict(color="#2c3e50"))
axes[1,0].set_title("NPS Score por Churn")
axes[1,0].set_xlabel("Churn")
plt.sca(axes[1,0])
plt.title("NPS Score según categoría Churn")

# 7.5 Reclamos vs Churn
df.boxplot(column="num_reclamos_6m", by="churn", ax=axes[1,1],
           boxprops=dict(color="#2c3e50"))
axes[1,1].set_title("Reclamos por Churn")
axes[1,1].set_xlabel("Churn")
plt.sca(axes[1,1])
plt.title("Reclamos por Churn")

# 7.6 Churn por tipo de cliente
churn_tipo = df.groupby("tipo_cliente")["churn"].mean().sort_values(ascending=False)
axes[1,2].bar(churn_tipo.index, churn_tipo.values, color="#e67e22")
axes[1,2].set_title("Tasa Churn por Tipo Cliente")
axes[1,2].set_ylabel("Tasa de Churn")
axes[1,2].set_ylim(0, 0.5)

plt.tight_layout()
fig.savefig(FIG_PATH / "01_eda_overview.png", dpi=150, bbox_inches="tight")
plt.show()
print(f"\nGráfica guardada en: {FIG_PATH / '01_eda_overview.png'}")
print("\n✅ EDA completado.")

# ── Cerrar captura y escribir resumen de resultados en README ───────────────────
sys.stdout = sys.__stdout__  # restaurar stdout normal
report_file.close()

# Leer el reporte generado
reporte_txt = (METRICS_PATH / "01_quality_report.txt").read_text(encoding="utf-8")

# Escribir sección en README.md
readme_path = Path("README.md")
separador   = "\n\n---\n## 📊 Reporte de Calidad — Data Raw\n```\n"
cierre      = "\n```\n"

# Leer README actual
readme_actual = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Eliminar sección anterior si ya existe (para no duplicar en cada ejecución)
marca_inicio = "---\n## 📊 Reporte de Calidad — Data Raw\n"
if marca_inicio in readme_actual:
    readme_actual = readme_actual[:readme_actual.index("---\n## 📊 Reporte de Calidad")]

# Agregar sección actualizada
readme_nuevo = readme_actual + separador + reporte_txt + cierre
readme_path.write_text(readme_nuevo, encoding="utf-8")

print("✅ Reporte guardado en 4_outputs/2_metrics/01_quality_report.txt")
print("✅ README.md actualizado con el reporte de calidad.")