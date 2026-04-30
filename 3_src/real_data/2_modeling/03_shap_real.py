"""
03_shap_real.py
Análisis SHAP para el modelo entrenado con dataset real de 110 registros
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shap
import joblib
import sys
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH   = Path("1_data/real_data/2_cleaned/01_cleaned_real.csv")
MODEL_PATH   = Path("1_data/real_data/3_features/pipeline_real.pkl")
METRICS_PATH = Path("4_outputs/real_data/2_metrics")
FIG_PATH     = Path("4_outputs/real_data/1_figures")

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

report_file = open(METRICS_PATH / "03_shap_real_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga y preprocesamiento ───────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH)
print("=" * 60)
print("REPORTE SHAP — DATASET REAL")
print("=" * 60)

NUMERICAS = [
    "valor_mensual", "num_envios_total",
    "antiguedad_dias", "dias_ultimo_envio"
]

X = df[NUMERICAS].copy()
X = X.fillna(X.median())
X["gasto_por_envio"] = X["valor_mensual"] / (X["num_envios_total"] + 1)
NUMERICAS_FINAL = NUMERICAS + ["gasto_por_envio"]
X = X[NUMERICAS_FINAL]

# ── 2. Cargar pipeline ────────────────────────────────────────────────────────
pipeline     = joblib.load(MODEL_PATH)
scaler       = pipeline.named_steps["scaler"]
mejor_modelo = pipeline.named_steps["modelo"].best_estimator_

print(f"\nPipeline cargado desde: {MODEL_PATH}")
print(f"Mejores parámetros: {pipeline.named_steps['modelo'].best_params_}")

# ── 3. Transformar X ──────────────────────────────────────────────────────────
X_scaled = scaler.transform(X)

# ── 4. Calcular SHAP values ───────────────────────────────────────────────────
explainer   = shap.LinearExplainer(mejor_modelo, X_scaled)
shap_values = explainer.shap_values(X_scaled)

print(f"\nSHAP values calculados sobre {len(X)} filas")

# ── 5. Importancia global ─────────────────────────────────────────────────────
importancia = pd.DataFrame({
    "feature"  : NUMERICAS_FINAL,
    "mean_shap": np.abs(shap_values).mean(axis=0)
}).sort_values("mean_shap", ascending=False).reset_index(drop=True)

print(f"\n── Importancia global (mean |SHAP|) ───────────────────────")
print(importancia.to_string())

# ── 6. Interpretación narrativa ───────────────────────────────────────────────
top3 = importancia.head(3)["feature"].tolist()
print(f"\n── Top 3 variables más influyentes ────────────────────────")
for i, feat in enumerate(top3, 1):
    val = importancia.loc[importancia["feature"] == feat, "mean_shap"].values[0]
    print(f"  {i}. {feat:25s} mean|SHAP|={val:.4f}")

print(f"""
── Interpretación ─────────────────────────────────────────
  - SHAP positivo → aumenta probabilidad de churn
  - SHAP negativo → disminuye probabilidad de churn
  - mean|SHAP| alto → variable muy influyente globalmente
""")

# ── 7. Gráficas ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle("Análisis SHAP — Dataset Real", fontsize=13, fontweight="bold")

# Bar plot importancia global
axes[0].barh(importancia["feature"][::-1], importancia["mean_shap"][::-1], color="#3498db")
axes[0].set_title("Importancia Global (mean |SHAP|)")
axes[0].set_xlabel("mean(|SHAP value|)")

# Dot plot por feature
for i, feat in enumerate(NUMERICAS_FINAL):
    feat_idx  = NUMERICAS_FINAL.index(feat)
    shap_col  = shap_values[:, feat_idx]
    y_jitter  = np.random.normal(i, 0.08, size=len(shap_col))
    axes[1].scatter(shap_col, y_jitter, alpha=0.4, s=15, c="#e74c3c")

axes[1].set_yticks(range(len(NUMERICAS_FINAL)))
axes[1].set_yticklabels(NUMERICAS_FINAL)
axes[1].axvline(0, color="black", lw=0.8, linestyle="--")
axes[1].set_title("Distribución SHAP por Feature")
axes[1].set_xlabel("SHAP value")

plt.tight_layout()
fig.savefig(FIG_PATH / "03_shap_real.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"Gráfica guardada en: {FIG_PATH / '03_shap_real.png'}")

# ── Cerrar captura ────────────────────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()
print("✅ Análisis SHAP dataset real completado.")