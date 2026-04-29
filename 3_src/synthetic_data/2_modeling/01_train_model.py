"""
06_train_model.py
Pipeline completo de modelado para predicción de churn con una regresión logística.

Estrategia de ejecución:
- ColumnTransformer: OneHotEncoder + StandardScaler
- Pipeline: preprocesamiento + LogisticRegression
- GridSearchCV con scoring='recall'
- Guardado del pipeline en .pkl con joblib
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
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, precision_recall_curve,
    make_scorer, recall_score, # para scoring personalizado en GridSearchCV
    precision_score, f1_score 
)

# ── Configuración ─────────────────────────────────────────────────────────────
INPUT_PATH   = Path("1_data/2_cleaned/05_cleaned_customers.csv")
MODEL_PATH   = Path("1_data/3_features/pipeline.pkl")
METRICS_PATH = Path("4_outputs/2_metrics")
FIG_PATH     = Path("4_outputs/1_figures")

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
METRICS_PATH.mkdir(parents=True, exist_ok=True)
FIG_PATH.mkdir(parents=True, exist_ok=True)

SEED = 42

# ── Captura de resultados ───────────────────────────────────────────────────
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

report_file = open(METRICS_PATH / "06_model_report.txt", "w", encoding="utf-8")
sys.stdout  = Tee(sys.stdout, report_file)

# ── 1. Carga ──────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_PATH, low_memory=False)
print("=" * 60)
print("REPORTE DE MODELADO — CHURN PREDICTION")
print("=" * 60)
print(f"\nFilas cargadas  : {len(df):,}")
print(f"Tasa de churn   : {df['churn'].mean():.2%}")

# ── 2. Winsorización de valor_total_6m (percentil 99) ────────────────────────
p99 = df["valor_total_6m"].quantile(0.99)
df["valor_total_6m"] = df["valor_total_6m"].clip(upper=p99)
print(f"\n── Winsorización valor_total_6m ───────────────────────────")
print(f"  Percentil 99   : {p99:,.0f}")
print(f"  Valor máximo post-winsorización: {df['valor_total_6m'].max():,.0f}")

# ── 3. Ingeniería de características ─────────────────────────────────────────
# Ratio reclamos por envío (evitar división por cero)
df["ratio_reclamos_envios"] = df["num_reclamos_6m"] / (df["num_envios_6m"] + 1)

# Segmento de recencia(días desde el último envío)
df["segmento_recencia"] = pd.cut(
    df["dias_ultimo_envio"],
    bins=[0, 15, 45, 90, 365],
    labels=["activo", "reciente", "en_riesgo", "inactivo"]
).astype(str)

print(f"\n── Features adicionales creadas ───────────────────────────")
print(f"  ratio_reclamos_envios  : reclamos / (envíos + 1)")
print(f"  segmento_recencia      : categorización de dias_ultimo_envio")
print(f"  Distribución segmento_recencia:")
print(df["segmento_recencia"].value_counts().to_string())

# ── 4. Definir X e y ──────────────────────────────────────────────────────────
EXCLUIR = ["customer_id", "churn"]
X = df.drop(columns=EXCLUIR)
y = df["churn"]

# Columnas por tipo
NUMERICAS = [
    "antiguedad_dias", "num_envios_6m", "valor_total_6m",
    "ticket_promedio", "dias_ultimo_envio", "num_reclamos_6m",
    "tasa_entrega_exitosa", "nps_score", "ratio_reclamos_envios"
]
CATEGORICAS = [
    "ciudad", "tipo_cliente", "canal_principal",
    "tiene_contrato", "segmento_recencia"
]

print(f"\n── Features del modelo ────────────────────────────────────")
print(f"  Numéricas   ({len(NUMERICAS)}): {NUMERICAS}")
print(f"  Categóricas ({len(CATEGORICAS)}): {CATEGORICAS}")

# ── 5. Split train/test estratificado (70/30) ─────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X[NUMERICAS + CATEGORICAS], y,
    test_size=0.30, # 30% para test, 70% para train
    random_state=SEED,
    stratify=y # Mantener proporción de churn en ambos sets
)
print(f"\n── Split train/test ───────────────────────────────────────")
print(f"  Train : {len(X_train):,} filas | churn={y_train.mean():.2%}")
print(f"  Test  : {len(X_test):,}  filas | churn={y_test.mean():.2%}")

# ── 6. ColumnTransformer ──────────────────────────────────────────────────────
preprocesamiento = ColumnTransformer(transformers=[
    ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), CATEGORICAS),
    ("num", StandardScaler(), NUMERICAS),
])

# ── 7. Pipeline + GridSearchCV ────────────────────────────────────────────────
# Se usa GridSearchCV para encontrar los mejores hiperparámetros de la regresión 
# logística
pipeline = Pipeline(steps=[
    ("preprocesamiento", preprocesamiento),
    ("modelo", GridSearchCV(
        estimator=LogisticRegression(
        penalty="elasticnet",
        solver="saga",
        max_iter=1000,
        random_state=SEED
    ),
        param_grid={
            "C"        : [0.01, 0.1, 1, 10, 100],
            "l1_ratio" : [0.1, 0.5, 0.9] # 0.0=L2, 1.0=L1, 0.5=ElasticNet
        },
        scoring=make_scorer(recall_score, pos_label=1),
 # priorizamos recall para capturar la mayor cantidad de churners posibles
        cv=5, # 5-fold cross-validation, robustece el aprendizaje
        n_jobs=-1,
        verbose=1,
    ))
])

print(f"\n── Entrenando pipeline (GridSearchCV, 5-fold, scoring=recall)...")
pipeline.fit(X_train, y_train)

# ── 8. Mejores parámetros ─────────────────────────────────────────────────────
best_params = pipeline.named_steps["modelo"].best_params_
best_score  = pipeline.named_steps["modelo"].best_score_
print(f"\n── Mejores parámetros ─────────────────────────────────────")
for k, v in best_params.items():
    print(f"  {k:12s}: {v}")
print(f"  Recall CV (train): {best_score:.4f}")

# ── 9. Evaluación en test ─────────────────────────────────────────────────────
y_pred      = pipeline.predict(X_test)
y_prob      = pipeline.predict_proba(X_test)[:, 1]
auc         = roc_auc_score(y_test, y_prob)

print(f"\n── Métricas en test ───────────────────────────────────────")
print(f"  AUC-ROC : {auc:.4f}")
print(f"\nMatriz de confusión:")
print(confusion_matrix(y_test, y_pred))
print(f"\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Activo","Churn"]))

# ── 9b. Ajuste de umbral de decisión ─────────────────────────────────────────
# Con threshold=0.5 el recall de churn es menor.
# Se propone bajar el umbral para capturar más churners (a costa de más falsos positivos)

print(f"\n── Búsqueda de umbral óptimo (max Recall clase Churn) ─────")
umbrales   = np.arange(0.20, 0.60, 0.02)
resultados = []
for t in umbrales:
    y_pred_t = (y_prob >= t).astype(int)
    resultados.append({
        "umbral"   : round(t, 2),
        "recall"   : recall_score(y_test, y_pred_t),
        "precision": precision_score(y_test, y_pred_t, zero_division=0),
        "f1"       : f1_score(y_test, y_pred_t),
    })

df_umbrales = pd.DataFrame(resultados).set_index("umbral")
print(df_umbrales.to_string())

# Seleccionar umbral con recall >= 0.70 y mayor f1, si existe
candidatos  = df_umbrales[df_umbrales["recall"] >= 0.70]
if len(candidatos) > 0:
    UMBRAL_OPTIMO = candidatos["f1"].idxmax()
else:
    UMBRAL_OPTIMO = df_umbrales["recall"].idxmax()

print(f"\n  Umbral óptimo seleccionado: {UMBRAL_OPTIMO}")
y_pred = (y_prob >= UMBRAL_OPTIMO).astype(int)  # reemplaza y_pred para métricas

print(f"\n── Métricas con umbral={UMBRAL_OPTIMO} ────────────────────")
print(f"  AUC-ROC : {auc:.4f}")
print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["Activo","Churn"]))

# ── 10. Métricas de impacto para el negocio ───────────────────────────────────
print(f"\n── Métricas de impacto de negocio ─────────────────────────")
# NOTA: Los siguientes valores son supuestos estimados.
# En producción deben ser provistos por el área financiera/comercial
# de Interrapidísimo.
SUPUESTOS = {
# se puede calcular como el valor total de compras en 6 meses multiplicado por un factor de retención anual
# (ej. 2x para estimar 1 año)
"LTV_PROMEDIO"      : df["valor_total_6m"].median() * 2,  # estimado anual
# COP por cliente contactado por multiples canales (teléfono, email, SMS)
# Tiempo agente call center (15 min) = 7,000 COP
# Descuento o incentivo ofrecido = 5,000 COP
# Costo operativo (SMS, email, sistema) = 3,000 COP
"COSTO_INTERVENCION" : 15_000,
"TASA_RETENCION"      : 0.30,     # % de clientes contactados que se retienen
}

print(f"\n── Supuestos de negocio (configurables) ───────────────────")
for k, v in SUPUESTOS.items():
    print(f"  {k:25s}: {v:,.2f}")


# Matriz de confusión
cm       = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

# Métricas de negocio
clientes_contactados = tp + fp
clientes_retenidos   = int(clientes_contactados * SUPUESTOS["TASA_RETENCION"])
costo_total          = clientes_contactados * SUPUESTOS["COSTO_INTERVENCION"]
ingreso_retenido     = clientes_retenidos   * SUPUESTOS["LTV_PROMEDIO"]
roi                  = (ingreso_retenido - costo_total) / costo_total * 100

print(f"\n── Métricas de impacto ────────────────────────────────────")
print(f"  Clientes churn detectados (TP) : {tp:,}")
print(f"  Falsos positivos (FP)          : {fp:,}")
print(f"  Clientes a contactar           : {clientes_contactados:,}")
print(f"  Clientes retenidos estimados   : {clientes_retenidos:,}")
print(f"  Costo total campaña            : ${costo_total:,.0f} COP")
print(f"  Ingreso retenido estimado      : ${ingreso_retenido:,.0f} COP")
print(f"  ROI estimado del modelo        : {roi:.1f}%")
print(f"\n  ⚠ Supuestos estimados — validar con áreas comercial y financiera para mayor precisión en métricas de negocio")

# ── 11. Gráficas ──────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Evaluación del Modelo — Churn Prediction", fontsize=13, fontweight="bold")

# 11.1 Matriz de confusión
sns.heatmap(
    confusion_matrix(y_test, y_pred),
    annot=True, fmt="d", cmap="Blues",
    xticklabels=["Activo","Churn"],
    yticklabels=["Activo","Churn"],
    ax=axes[0]
)
axes[0].set_title("Matriz de Confusión")
axes[0].set_ylabel("Real")
axes[0].set_xlabel("Predicho")

# 11.2 Curva ROC
fpr, tpr, _ = roc_curve(y_test, y_prob)
axes[1].plot(fpr, tpr, color="#e74c3c", lw=2, label=f"AUC = {auc:.3f}")
axes[1].plot([0,1],[0,1], "k--", lw=1)
axes[1].set_title("Curva ROC")
axes[1].set_xlabel("Tasa Falsos Positivos")
axes[1].set_ylabel("Tasa Verdaderos Positivos")
axes[1].legend()

# 11.3 Curva Precision-Recall
precision, recall, _ = precision_recall_curve(y_test, y_prob)
axes[2].plot(recall, precision, color="#3498db", lw=2)
axes[2].set_title("Curva Precision-Recall")
axes[2].set_xlabel("Recall")
axes[2].set_ylabel("Precision")

plt.tight_layout()
fig.savefig(FIG_PATH / "02_model_evaluation.png", dpi=150, bbox_inches="tight")
plt.close()
print(f"\nGráfica guardada en: {FIG_PATH / '02_model_evaluation.png'}")

# ── 12. Guardar pipeline ──────────────────────────────────────────────────────
joblib.dump(pipeline, MODEL_PATH)
print(f"\n── Pipeline guardado en: {MODEL_PATH}")

# ── 13. Verificar pipeline desde .pkl ────────────────────────────────────────
modelo_cargado = joblib.load(MODEL_PATH)
muestra_pred   = modelo_cargado.predict(X_test.iloc[:5])
print(f"  Verificación predict() desde .pkl: {muestra_pred}")

# ── Cerrar captura ────────────────────────────────────────────────────────────
sys.stdout = sys.__stdout__
report_file.close()

# ── Actualizar README ─────────────────────────────────────────────────────────
reporte_txt   = (METRICS_PATH / "06_model_report.txt").read_text(encoding="utf-8")
readme_path   = Path("README.md")
readme_actual = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

marca = "---\n## 🤖 Reporte de Modelado\n"
if marca in readme_actual:
    readme_actual = readme_actual[:readme_actual.index(marca)]

readme_path.write_text(
    readme_actual + f"\n\n---\n## 🤖 Reporte de Modelado\n```\n{reporte_txt}\n```\n",
    encoding="utf-8"
)

print("✅ Modelado completado.")
print("✅ Pipeline guardado en 1_data/3_features/pipeline.pkl")
print("✅ README.md actualizado.")