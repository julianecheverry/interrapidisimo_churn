"""
02_model_real.py
Pipeline de modelado para dataset real raw_data_customers_lpgr.csv
Features disponibles: valor_mensual, num_envios_total,
                      antiguedad_dias, dias_ultimo_envio
Modelo: Regresión Logística con Pipeline + GridSearchCV
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, precision_recall_curve,
    make_scorer, recall_score, precision_score, f1_score
)

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH   = Path("1_data/real_data/2_cleaned/01_cleaned_real.csv")
MODEL_PATH   = Path("1_data/real_data/3_features/pipeline_real.pkl")
METRICS_PATH = Path("4_outputs/real_data/2_metrics")
FIG_PATH     = Path("4_outputs/real_data/1_figures")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
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

report_file = open(METRICS_PATH / "02_model_real_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH)
print("=" * 60)
print("REPORTE DE MODELADO — DATASET REAL")
print("=" * 60)
print(f"\nFilas cargadas  : {len(df):,}")
print(f"Tasa de churn   : {df['churn'].mean():.2%}")
print(f"Columnas        : {list(df.columns)}")

# ── 2. Features disponibles ───────────────────────────────────────────────────
NUMERICAS = [
    "valor_mensual",
    "num_envios_total",
    "antiguedad_dias",
    "dias_ultimo_envio"
]

print(f"\n── Features del modelo ────────────────────────────────────")
print(f"  Numéricas ({len(NUMERICAS)}): {NUMERICAS}")
print(f"\n  Nota: dataset real no contiene nps_score, num_reclamos_6m")
print(f"  ni variables categóricas suficientes para OHE.")
print(f"  Se modela solo con features numéricas disponibles.")

X = df[NUMERICAS].copy()
y = df["churn"].astype(int)

# Imputar nulo restante
X = X.fillna(X.median())

# ── 3. Feature Engineering ────────────────────────────────────────────────────
X["gasto_por_envio"] = X["valor_mensual"] / (X["num_envios_total"] + 1)

NUMERICAS_FINAL = NUMERICAS + ["gasto_por_envio"]
print(f"\n── Feature Engineering ────────────────────────────────────")
print(f"  gasto_por_envio = valor_mensual / (num_envios_total + 1)")

# ── 4. Split train/test ───────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X[NUMERICAS_FINAL], y,
    test_size=0.30,
    random_state=SEED,
    stratify=y
)
print(f"\n── Split train/test ───────────────────────────────────────")
print(f"  Train : {len(X_train):,} filas | churn={y_train.mean():.2%}")
print(f"  Test  : {len(X_test):,}  filas | churn={y_test.mean():.2%}")

# ── 5. Pipeline + GridSearchCV ────────────────────────────────────────────────
pipeline = Pipeline(steps=[
    ("scaler", StandardScaler()),
    ("modelo", GridSearchCV(
        estimator=LogisticRegression(
            penalty="elasticnet",
            solver="saga",
            max_iter=1000,
            random_state=SEED
        ),
        param_grid={
            "C"       : [0.01, 0.1, 1, 10, 100],
            "l1_ratio": [0.0, 0.5, 1.0],
        },
        scoring=make_scorer(recall_score, pos_label=1),
        cv=5,
        n_jobs=-1,
        verbose=0,
    ))
])

print(f"\n── Entrenando pipeline (GridSearchCV 5-fold)...")
pipeline.fit(X_train, y_train)

best_params = pipeline.named_steps["modelo"].best_params_
best_score  = pipeline.named_steps["modelo"].best_score_
print(f"\n── Mejores parámetros ─────────────────────────────────────")
for k, v in best_params.items():
    print(f"  {k:12s}: {v}")
print(f"  Recall CV (train): {best_score:.4f}")

# ── 6. Evaluación ─────────────────────────────────────────────────────────────
y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]
auc    = roc_auc_score(y_test, y_prob)

print(f"\n── Métricas con umbral=0.5 ────────────────────────────────")
print(f"  AUC-ROC : {auc:.4f}")
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["Activo","Churn"]))

# ── 7. Ajuste de umbral ───────────────────────────────────────────────────────
umbrales   = np.arange(0.20, 0.60, 0.02)
resultados = []
for t in umbrales:
    y_pred_t = (y_prob >= t).astype(int)
    resultados.append({
        "umbral"   : round(t, 2),
        "recall"   : recall_score(y_test, y_pred_t, zero_division=0),
        "precision": precision_score(y_test, y_pred_t, zero_division=0),
        "f1"       : f1_score(y_test, y_pred_t, zero_division=0),
    })

df_umbrales   = pd.DataFrame(resultados).set_index("umbral")
candidatos    = df_umbrales[df_umbrales["recall"] >= 0.70]
UMBRAL_OPTIMO = candidatos["f1"].idxmax() if len(candidatos) > 0 else df_umbrales["recall"].idxmax()
y_pred        = (y_prob >= UMBRAL_OPTIMO).astype(int)

print(f"\n── Métricas con umbral={UMBRAL_OPTIMO} ────────────────────")
print(f"  AUC-ROC : {auc:.4f}")
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["Activo","Churn"]))

# ── 8. Métricas de negocio ────────────────────────────────────────────────────
print(f"\n── Métricas de impacto de negocio ─────────────────────────")
SUPUESTOS = {
    "LTV_PROMEDIO"       : df["valor_mensual"].median() * 12,
    "COSTO_INTERVENCION" : 15_000,
    "TASA_RETENCION"     : 0.30,
}
for k, v in SUPUESTOS.items():
    print(f"  {k:25s}: {v:,.2f}")

cm             = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()
clientes_contactados = tp + fp
clientes_retenidos   = int(clientes_contactados * SUPUESTOS["TASA_RETENCION"])
costo_total          = clientes_contactados * SUPUESTOS["COSTO_INTERVENCION"]
ingreso_retenido     = clientes_retenidos   * SUPUESTOS["LTV_PROMEDIO"]
roi                  = (ingreso_retenido - costo_total) / costo_total * 100 if costo_total > 0 else 0

print(f"\n  Clientes churn detectados (TP): {tp:,}")
print(f"  Falsos positivos (FP)          : {fp:,}")
print(f"  Costo total campaña            : ${costo_total:,.0f} COP")
print(f"  Ingreso retenido estimado      : ${ingreso_retenido:,.0f} COP")
print(f"  ROI estimado                   : {roi:.1f}%")
print(f"\n  ⚠ Supuestos estimados — validar con área comercial")

# ── 9. Gráficas ───────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Evaluación del Modelo — Dataset Real", fontsize=13, fontweight="bold")

sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt="d", cmap="Blues",
            xticklabels=["Activo","Churn"], yticklabels=["Activo","Churn"], ax=axes[0])
axes[0].set_title("Matriz de Confusión")
axes[0].set_ylabel("Real")
axes[0].set_xlabel("Predicho")

fpr, tpr, _ = roc_curve(y_test, y_prob)
axes[1].plot(fpr, tpr, color="#e74c3c", lw=2, label=f"AUC={auc:.3f}")
axes[1].plot([0,1],[0,1], "k--", lw=1)
axes[1].set_title("Curva ROC")
axes[1].set_xlabel("Tasa Falsos Positivos")
axes[1].set_ylabel("Tasa Verdaderos Positivos")
axes[1].legend()

precision_arr, recall_arr, _ = precision_recall_curve(y_test, y_prob)
axes[2].plot(recall_arr, precision_arr, color="#3498db", lw=2)
axes[2].set_title("Curva Precision-Recall")
axes[2].set_xlabel("Recall")
axes[2].set_ylabel("Precision")

plt.tight_layout()
fig.savefig(FIG_PATH / "02_model_real_evaluation.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nGráfica guardada en: {FIG_PATH / '02_model_real_evaluation.png'}")

# ── 10. Guardar pipeline ──────────────────────────────────────────────────────
joblib.dump(pipeline, MODEL_PATH)
print(f"\n── Pipeline guardado en: {MODEL_PATH}")

modelo_cargado = joblib.load(MODEL_PATH)
muestra_pred   = modelo_cargado.predict(X_test.iloc[:5])
print(f"  Verificación predict() desde .pkl: {muestra_pred}")

# ── Cerrar captura ────────────────────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()
print("✅ Modelado dataset real completado.")
print(f"✅ Pipeline guardado en: {MODEL_PATH}")