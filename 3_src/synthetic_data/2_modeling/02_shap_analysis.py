"""
02_shap_analysis.py

Explica las predicciones del modelo de regresión logística
usando valores SHAP (SHapley Additive exPlanations).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import joblib
import sys
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH   = Path("1_data\synthetic_data\2_cleaned\05_cleaned_customers.csv")
MODEL_PATH   = Path("1_data\synthetic_data\3_features\pipeline.pkl")
FIG_PATH     = Path("4_outputs\synthetic_data\1_figures")
METRICS_PATH = Path("4_outputs\synthetic_data\2_metrics")

METRICS_PATH.mkdir(parents=True, exist_ok=True)
FIG_PATH.mkdir(parents=True, exist_ok=True)

SEED = 42

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

report_file = open(METRICS_PATH / "07_shap_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, low_memory=False)
print("=" * 60)
print("REPORTE DE ANÁLISIS VALORES SHAP (SHapley Additive exPlanations)")
print("=" * 60)

# ── 2. Replicar preprocesamiento del script de entrenamiento ──────────────────
# Winsorización
p99 = df["valor_total_6m"].quantile(0.99)
df["valor_total_6m"] = df["valor_total_6m"].clip(upper=p99)

# Features adicionales
df["ratio_reclamos_envios"] = df["num_reclamos_6m"] / (df["num_envios_6m"] + 1)
df["segmento_recencia"] = pd.cut(
    df["dias_ultimo_envio"],
    bins=[0, 15, 45, 90, 365],
    labels=["activo", "reciente", "en_riesgo", "inactivo"]
).astype(str)

NUMERICAS = [
    "antiguedad_dias", "num_envios_6m", "valor_total_6m",
    "ticket_promedio", "dias_ultimo_envio", "num_reclamos_6m",
    "tasa_entrega_exitosa", "nps_score", "ratio_reclamos_envios"
]
CATEGORICAS = [
    "ciudad", "tipo_cliente", "canal_principal",
    "tiene_contrato", "segmento_recencia"
]

X = df[NUMERICAS + CATEGORICAS]
y = df["churn"]

# ── 3. Cargar pipeline ────────────────────────────────────────────────────────
pipeline = joblib.load(MODEL_PATH)
print(f"\nPipeline cargado desde: {MODEL_PATH}")

# ── 4. Transformar X con el preprocesador del pipeline ────────────────────────
preprocesador = pipeline.named_steps["preprocesamiento"]
X_transformado = preprocesador.transform(X)

# Recuperar nombres de columnas tras One Hot Encoding
ohe_features = preprocesador.named_transformers_["cat"]\
    .get_feature_names_out(CATEGORICAS).tolist()
feature_names = ohe_features + NUMERICAS

print(f"\nFeatures tras preprocesamiento : {len(feature_names)}")
print(f"  Categóricas (OHE) : {len(ohe_features)}")
print(f"  Numéricas         : {len(NUMERICAS)}")

# ── 5. Extraer modelo base del GridSearchCV ───────────────────────────────────
mejor_modelo = pipeline.named_steps["modelo"].best_estimator_
print(f"\nMejores parámetros:")
for k, v in pipeline.named_steps["modelo"].best_params_.items():
    print(f"  {k:12s}: {v}")

# ── 6. Calcular SHAP values ───────────────────────────────────────────────────
# Muestra de 1000 filas para eficiencia
np.random.seed(SEED)
idx_muestra    = np.random.choice(len(X_transformado), size=1000, replace=False)
X_muestra      = X_transformado[idx_muestra]

explainer   = shap.LinearExplainer(mejor_modelo, X_muestra)
shap_values = explainer.shap_values(X_muestra)

print(f"\nSHAP values calculados sobre muestra de 1.000 filas")

# ── 7. Importancia global (mean |SHAP|) ───────────────────────────────────────
importancia = pd.DataFrame({
    "feature"   : feature_names,
    "mean_shap" : np.abs(shap_values).mean(axis=0)
}).sort_values("mean_shap", ascending=False).reset_index(drop=True)

print(f"\n── Top 15 variables por importancia SHAP ──────────────────")
print(importancia.head(15).to_string())

# ── 8. Gráficas ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 7))
fig.suptitle("Análisis SHAP — Churn Prediction", fontsize=13, fontweight="bold")

# 8.1 Bar plot importancia global
top15 = importancia.head(15)
axes[0].barh(top15["feature"][::-1], top15["mean_shap"][::-1], color="#3498db")
axes[0].set_title("Importancia Global (mean |SHAP|)")
axes[0].set_xlabel("mean(|SHAP value|)")

# 8.2 Beeswarm manual (dot plot por feature)
top10_features = importancia.head(10)["feature"].tolist()
top10_idx      = [feature_names.index(f) for f in top10_features]
shap_top10     = shap_values[:, top10_idx]

for i, (feat, shap_col) in enumerate(zip(top10_features, shap_top10.T)):
    y_jitter = np.random.normal(i, 0.08, size=len(shap_col))
    axes[1].scatter(shap_col, y_jitter, alpha=0.3, s=8, c="#e74c3c")

axes[1].set_yticks(range(len(top10_features)))
axes[1].set_yticklabels(top10_features)
axes[1].axvline(0, color="black", lw=0.8, linestyle="--")
axes[1].set_title("Distribución SHAP — Top 10 Features")
axes[1].set_xlabel("SHAP value (impacto en predicción de churn)")

plt.tight_layout()
fig.savefig(FIG_PATH / "03_shap_analysis.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nGráfica guardada en: {FIG_PATH / '03_shap_analysis.png'}")

# ── 9. Interpretación resultados ───────────────────────────────────────────────
top3 = importancia.head(3)["feature"].tolist()
print(f"\n── Interpretación de resultados ───────────────────────────")
print(f"  Las 3 variables más influyentes en la predicción de churn:")
for i, feat in enumerate(top3, 1):
    shap_mean = importancia.loc[importancia["feature"]==feat, "mean_shap"].values[0]
    print(f"  {i}. {feat:35s} mean|SHAP|={shap_mean:.4f}")
print(f"""
  Interpretación general:
  - Valores SHAP positivos → aumentan la probabilidad de churn
  - Valores SHAP negativos → disminuyen la probabilidad de churn
  - mean|SHAP| alto → variable muy influyente en la explicabilidad del modelo
""")

# ── Cerrar captura ────────────────────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()

# ── Actualizar README ─────────────────────────────────────────────────────────
reporte_txt   = (METRICS_PATH / "07_shap_report.txt").read_text(encoding="utf-8")
readme_path   = Path("README.md")
readme_actual = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

marca = "---\n## 🔍 Reporte valores SHAP (SHapley Additive exPlanations)\n"
if marca in readme_actual:
    readme_actual = readme_actual[:readme_actual.index(marca)]

readme_path.write_text(
    readme_actual + f"\n\n---\n## 🔍 Reporte valores SHAP (SHapley Additive exPlanations)\n```\n{reporte_txt}\n```\n",
    encoding="utf-8"
)

print("✅ Análisis SHAP completado.")
print("✅ README.md actualizado.")