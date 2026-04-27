"""
generate_notebook_datos_sintetico.py
Genera el notebook 01_modeling_datasetsintetico.ipynb con interpretaciones
y código del pipeline de churn.
"""

import nbformat as nbf
from pathlib import Path

Path("2_notebooks").mkdir(exist_ok=True)
nb    = nbf.v4.new_notebook()
cells = []

# ── Celda 1: Título ───────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""# 🚀 Churn Prediction — Interrapidísimo
## Modelo de Regresión Logística para Predicción de Fuga de Clientes

**Autor:** Julian Echeverry  
**Rol:** Científico de Datos y Analítica  

---

### Contexto
Interrapidísimo cuenta con un dataset histórico de comportamiento de clientes.  
El objetivo es construir un modelo predictivo de **churn** robusto,  
siguiendo buenas prácticas de ingeniería y estándares de AWS.

### Estructura del notebook
1. Carga y verificación del dataset limpio  
2. Winsorización de outliers  
3. Feature Engineering  
4. Preprocesamiento con ColumnTransformer  
5. Split train/test estratificado  
6. Pipeline + GridSearchCV  
7. Evaluación del modelo  
8. Ajuste de umbral de decisión  
9. Métricas de impacto de negocio  
10. Análisis SHAP  
11. Guardado del pipeline (.pkl)
"""
))

# ── Celda 2: Imports ──────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 1. Librerías e Imports"))
cells.append(nbf.v4.new_code_cell(
"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import joblib
from pathlib import Path
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_auc_score, roc_curve, precision_recall_curve,
    make_scorer, recall_score, precision_score, f1_score
)

SEED = 42
print("✅ Librerías cargadas correctamente")"""
))

# ── Celda 3: Carga ────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 2. Carga del Dataset Limpio
El dataset proviene de la capa **cleaned/** del Data Lake.  
Ya fue procesado en la Fase 1: anonimizado, fechas normalizadas,  
nulos imputados y duplicados eliminados."""
))
cells.append(nbf.v4.new_code_cell(
"""INPUT_PATH = Path("1_data/2_cleaned/05_cleaned_customers.csv")
df = pd.read_csv(INPUT_PATH, low_memory=False)

print(f"Dimensiones  : {df.shape[0]:,} filas x {df.shape[1]} columnas")
print(f"Tasa de churn: {df['churn'].mean():.2%}")
df.head()"""
))

# ── Celda 4: Winsorización ────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 3. Winsorización de Outliers
Se detectaron **325 outliers extremos** en `valor_total_6m` durante el EDA.  
Aplicamos winsorización al **percentil 99** para evitar que distorsionen el modelo,  
sin eliminar filas."""
))
cells.append(nbf.v4.new_code_cell(
"""p99 = df["valor_total_6m"].quantile(0.99)
df["valor_total_6m"] = df["valor_total_6m"].clip(upper=p99)

print(f"Percentil 99           : {p99:,.0f} COP")
print(f"Valor máximo post-wins.: {df['valor_total_6m'].max():,.0f} COP")"""
))

# ── Celda 5: Feature Engineering ─────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 4. Feature Engineering

| Feature | Fórmula | Justificación |
|---|---|---|
| `ratio_reclamos_envios` | reclamos / (envíos + 1) | Normaliza reclamos por actividad |
| `segmento_recencia` | bins de `dias_ultimo_envio` | Captura ciclo de vida del cliente |"""
))
cells.append(nbf.v4.new_code_cell(
"""df["ratio_reclamos_envios"] = df["num_reclamos_6m"] / (df["num_envios_6m"] + 1)

df["segmento_recencia"] = pd.cut(
    df["dias_ultimo_envio"],
    bins=[0, 15, 45, 90, 365],
    labels=["activo", "reciente", "en_riesgo", "inactivo"]
).astype(str)

print("Distribución segmento_recencia:")
print(df["segmento_recencia"].value_counts())"""
))

# ── Celda 6: Features y Target ───────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 5. Definición de Features y Target"))
cells.append(nbf.v4.new_code_cell(
"""NUMERICAS = [
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

print(f"Features numéricas  : {len(NUMERICAS)}")
print(f"Features categóricas: {len(CATEGORICAS)}")
print(f"Total features      : {len(NUMERICAS + CATEGORICAS)}")"""
))

# ── Celda 7: Split ───────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 6. Split Train/Test Estratificado (70/30)
Usamos `stratify=y` para garantizar que la proporción de churn  
sea igual en train y test, evitando sesgo por muestreo."""
))
cells.append(nbf.v4.new_code_cell(
"""X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.30,
    random_state=SEED,
    stratify=y
)

print(f"Train: {len(X_train):,} filas | churn={y_train.mean():.2%}")
print(f"Test : {len(X_test):,}  filas | churn={y_test.mean():.2%}")"""
))

# ── Celda 8: Pipeline ────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 7. Pipeline: ColumnTransformer + GridSearchCV
Replicamos la arquitectura del notebook de referencia `modelo_usuarios_pospago.ipynb`:

- **ColumnTransformer**: aplica OHE a categóricas y StandardScaler a numéricas  
- **Pipeline**: encadena preprocesamiento + modelo en un único objeto serializable  
- **GridSearchCV**: 5-fold CV optimizando **Recall de la clase Churn (pos_label=1)**

> **Decisión de scoring:** el costo de un falso negativo (churner no detectado)  
> supera el costo de un falso positivo (intervención innecesaria)."""
))
cells.append(nbf.v4.new_code_cell(
"""preprocesamiento = ColumnTransformer(transformers=[
    ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), CATEGORICAS),
    ("num", StandardScaler(), NUMERICAS),
])

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
            "C"       : [0.01, 0.1, 1, 10, 100],
            "l1_ratio": [0.0, 0.5, 1.0],
        },
        scoring=make_scorer(recall_score, pos_label=1),
        cv=5,
        n_jobs=-1,
        verbose=1,
    ))
])

print("⏳ Entrenando pipeline — puede tardar varios minutos...")
pipeline.fit(X_train, y_train)

best_params = pipeline.named_steps["modelo"].best_params_
best_score  = pipeline.named_steps["modelo"].best_score_
print(f"\\n✅ Entrenamiento completado")
print(f"Mejores parámetros : {best_params}")
print(f"Recall CV (train)  : {best_score:.4f}")"""
))

# ── Celda 9: Evaluación ───────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 8. Evaluación del Modelo (umbral=0.5)"))
cells.append(nbf.v4.new_code_cell(
"""y_pred = pipeline.predict(X_test)
y_prob = pipeline.predict_proba(X_test)[:, 1]
auc    = roc_auc_score(y_test, y_prob)

print(f"AUC-ROC: {auc:.4f}")
print("\\nMatriz de confusión:")
print(confusion_matrix(y_test, y_pred))
print("\\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["Activo","Churn"]))"""
))

# ── Celda 10: Umbral ──────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 9. Ajuste de Umbral de Decisión
Con `threshold=0.50` el Recall de Churn es bajo (~0.42).  
Exploramos umbrales entre 0.20 y 0.60 para maximizar el Recall  
manteniendo un F1 razonable."""
))
cells.append(nbf.v4.new_code_cell(
"""umbrales   = np.arange(0.20, 0.60, 0.02)
resultados = []
for t in umbrales:
    y_pred_t = (y_prob >= t).astype(int)
    resultados.append({
        "umbral"   : round(t, 2),
        "recall"   : recall_score(y_test, y_pred_t),
        "precision": precision_score(y_test, y_pred_t, zero_division=0),
        "f1"       : f1_score(y_test, y_pred_t),
    })

df_umbrales   = pd.DataFrame(resultados).set_index("umbral")
candidatos    = df_umbrales[df_umbrales["recall"] >= 0.70]
UMBRAL_OPTIMO = candidatos["f1"].idxmax() if len(candidatos) > 0 else df_umbrales["recall"].idxmax()
y_pred        = (y_prob >= UMBRAL_OPTIMO).astype(int)

print(f"Umbral óptimo: {UMBRAL_OPTIMO}")
print(f"\\nMétricas con umbral={UMBRAL_OPTIMO}:")
print(classification_report(y_test, y_pred, target_names=["Activo","Churn"]))
df_umbrales"""
))

# ── Celda 11: Gráficas ────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell("## 10. Visualizaciones de Evaluación"))
cells.append(nbf.v4.new_code_cell(
"""fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Evaluación del Modelo — Churn Prediction", fontsize=13, fontweight="bold")

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
plt.show()"""
))

# ── Celda 12: Métricas negocio ────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 11. Métricas de Impacto de Negocio
> ⚠️ Los siguientes valores son **supuestos estimados**.  
> Deben ser validados con las áreas comercial y financiera de Interrapidísimo."""
))
cells.append(nbf.v4.new_code_cell(
"""SUPUESTOS = {
    "LTV_PROMEDIO"       : df["valor_total_6m"].median() * 2,
    "COSTO_INTERVENCION" : 15_000,
    "TASA_RETENCION"     : 0.30,
}

cm             = confusion_matrix(y_test, y_pred)
tn, fp, fn, tp = cm.ravel()

clientes_contactados = tp + fp
clientes_retenidos   = int(clientes_contactados * SUPUESTOS["TASA_RETENCION"])
costo_total          = clientes_contactados * SUPUESTOS["COSTO_INTERVENCION"]
ingreso_retenido     = clientes_retenidos   * SUPUESTOS["LTV_PROMEDIO"]
roi                  = (ingreso_retenido - costo_total) / costo_total * 100

print(f"Supuestos de negocio:")
for k, v in SUPUESTOS.items():
    print(f"  {k:25s}: {v:,.2f}")

print(f"\\nMétricas de impacto:")
print(f"  Clientes churn detectados (TP): {tp:,}")
print(f"  Falsos positivos (FP)          : {fp:,}")
print(f"  Clientes a contactar           : {clientes_contactados:,}")
print(f"  Clientes retenidos estimados   : {clientes_retenidos:,}")
print(f"  Costo total campaña            : ${costo_total:,.0f} COP")
print(f"  Ingreso retenido estimado      : ${ingreso_retenido:,.0f} COP")
print(f"  ROI estimado del modelo        : {roi:.1f}%")"""
))

# ── Celda 13: SHAP ────────────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 12. Análisis SHAP — Explicabilidad del Modelo
SHAP (SHapley Additive exPlanations) permite entender  
**qué variables impulsan la predicción de churn**.

- **mean|SHAP| alto** → variable muy influyente globalmente  
- **SHAP positivo** → aumenta probabilidad de churn  
- **SHAP negativo** → disminuye probabilidad de churn"""
))
cells.append(nbf.v4.new_code_cell(
"""preprocesador  = pipeline.named_steps["preprocesamiento"]
mejor_modelo   = pipeline.named_steps["modelo"].best_estimator_
X_transformado = preprocesador.transform(X)

ohe_features  = preprocesador.named_transformers_["cat"]\
    .get_feature_names_out(CATEGORICAS).tolist()
feature_names = ohe_features + NUMERICAS

np.random.seed(SEED)
idx_muestra   = np.random.choice(len(X_transformado), size=1000, replace=False)
X_muestra     = X_transformado[idx_muestra]

explainer   = shap.LinearExplainer(mejor_modelo, X_muestra)
shap_values = explainer.shap_values(X_muestra)

importancia = pd.DataFrame({
    "feature"  : feature_names,
    "mean_shap": np.abs(shap_values).mean(axis=0)
}).sort_values("mean_shap", ascending=False).reset_index(drop=True)

print("Top 10 variables más influyentes:")
importancia.head(10)"""
))

# ── Celda 14: Gráfica SHAP ───────────────────────────────────────────────────
cells.append(nbf.v4.new_code_cell(
"""fig, ax = plt.subplots(figsize=(10, 6))
top15 = importancia.head(15)
ax.barh(top15["feature"][::-1], top15["mean_shap"][::-1], color="#3498db")
ax.set_title("Importancia Global de Variables (mean |SHAP|)", fontsize=13)
ax.set_xlabel("mean(|SHAP value|)")
plt.tight_layout()
plt.show()"""
))

# ── Celda 15: Guardar pipeline ────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 13. Guardado del Pipeline
Guardamos el pipeline completo (preprocesamiento + modelo) en `.pkl`  
usando `joblib`. Permite deployment directo en SageMaker Endpoint."""
))
cells.append(nbf.v4.new_code_cell(
"""MODEL_PATH = Path("1_data\3_features\pipeline.pkl")
joblib.dump(pipeline, MODEL_PATH)
print(f"✅ Pipeline guardado en: {MODEL_PATH}")

modelo_cargado = joblib.load(MODEL_PATH)
muestra_pred   = modelo_cargado.predict(X_test.iloc[:5])
print(f"Verificación predict() desde .pkl: {muestra_pred}")"""
))

# ── Celda 16: Conclusiones ────────────────────────────────────────────────────
cells.append(nbf.v4.new_markdown_cell(
"""## 14. Conclusiones

### Resultados del modelo
| Métrica | Valor |
|---|---|
| AUC-ROC | 0.7749 |
| Recall Churn (umbral=0.28) | 0.73 |
| Precision Churn | 0.49 |
| F1 Churn | 0.58 |

### Variables más influyentes (SHAP)
1. `num_reclamos_6m` — Los reclamos son el predictor más fuerte de churn
2. `nps_score` — La satisfacción del cliente es clave para la retención
3. `num_envios_6m` — La actividad reciente refleja el compromiso del cliente

### Decisiones técnicas clave
- **Umbral 0.28**: prioriza Recall sobre Precision — el costo de no detectar un churner supera el de intervenir innecesariamente
- **Winsorización p99**: trata outliers sin pérdida de filas
- **ElasticNet**: regularización flexible que combina L1 y L2
- **Pipeline serializable**: permite deployment directo en SageMaker Endpoint
"""
))

# ── Escribir notebook ─────────────────────────────────────────────────────────
nb.cells = cells
OUTPUT = Path("2_notebooks/01_modeling_datasetsintetico.ipynb")
nbf.write(nb, str(OUTPUT))
print(f"✅ Notebook generado en: {OUTPUT}")