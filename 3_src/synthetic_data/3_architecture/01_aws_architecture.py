"""
01_aws_architecture.py
Diagrama de arquitectura AWS para el pipeline de churn prediction,
para productivizar el modelo, en un escenario con millones de registros de clientes,
manejados con contenedores Docker en SageMaker con el fin de distribuir cargas
de trabajo y optimizar costos.

Componentes:    S3 → Glue → ECR :: Para ingesta, limpieza, feature engineering.
                SageMaker → Endpoint + Batch Transform :: Para entrenamiento, inferencia en tiempo real y scoring masivo.
             +  CloudWatch + Model Registry :: Monitoreo y gobernanza.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from pathlib import Path

FIG_PATH = Path("4_outputs\synthetic_data\1_figures")
FIG_PATH.mkdir(parents=True, exist_ok=True)

# ── Colores AWS ───────────────────────────────────────────────────────────────
AWS_ORANGE = "#FF9900"
AWS_DARK   = "#232F3E"
AWS_BLUE   = "#1A73E8"
AWS_GREEN  = "#2ECC71"
AWS_RED    = "#E74C3C"
AWS_PURPLE = "#8E44AD"
AWS_TEAL   = "#17A589"
AWS_PINK   = "#E91E8C"
WHITE      = "#FFFFFF"

fig, ax = plt.subplots(figsize=(26, 15))
ax.set_xlim(0, 26)
ax.set_ylim(0, 15)
ax.axis("off")
fig.patch.set_facecolor(AWS_DARK)
ax.set_facecolor(AWS_DARK)

# ── Helpers ───────────────────────────────────────────────────────────────────
def draw_box(ax, x, y, w, h, color, label, sublabel="", radius=0.3):
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle=f"round,pad=0.05,rounding_size={radius}",
                         facecolor=color, edgecolor=WHITE,
                         linewidth=1.5, zorder=3)
    ax.add_patch(box)
    ax.text(x + w/2, y + h/2 + (0.18 if sublabel else 0),
            label, ha="center", va="center",
            fontsize=8.5, fontweight="bold", color=WHITE, zorder=4)
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.22, sublabel,
                ha="center", va="center",
                fontsize=7, color=WHITE, alpha=0.85, zorder=4)

def draw_arrow(ax, x1, y1, x2, y2, color=AWS_ORANGE, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color=color,
                                lw=2.0, mutation_scale=18), zorder=5)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my + 0.15, label, ha="center", fontsize=7,
                color=color, zorder=6)

def draw_section(ax, x, y, w, h, label, color):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.1,rounding_size=0.4",
                          facecolor=color, edgecolor=WHITE,
                          linewidth=1.0, alpha=0.12, zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.2, y + h - 0.25, label,
            ha="left", va="top", fontsize=8.5, fontweight="bold",
            color=WHITE, alpha=0.75, zorder=2)

# ── Título ────────────────────────────────────────────────────────────────────
ax.text(13, 14.4,
        "Arquitectura AWS — Pipeline Churn Prediction | Interrapidísimo",
        ha="center", fontsize=14, fontweight="bold", color=AWS_ORANGE)
ax.text(13, 14.0,
        "Escenario: millones de registros · Contenedores Docker · S3 · Glue · ECR · SageMaker · CloudWatch",
        ha="center", fontsize=8.5, color=WHITE, alpha=0.7)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — DATA LAKE S3
# ══════════════════════════════════════════════════════════════════════════════
draw_section(ax, 0.3, 8.2, 4.8, 5.0, "① Data Lake — Amazon S3", AWS_ORANGE)
draw_box(ax, 0.6, 11.5, 4.2, 0.9, AWS_ORANGE, "S3 · Capa RAW",
         "Particionado: s3://bucket/raw/year/month/")
draw_box(ax, 0.6, 10.2, 4.2, 0.9, AWS_ORANGE, "S3 · Capa CLEANED",
         "Anonimizado · Fechas · Imputado")
draw_box(ax, 0.6,  8.9, 4.2, 0.9, AWS_ORANGE, "S3 · Capa FEATURES",
         "pipeline.pkl · Parquet particionado")

draw_arrow(ax, 2.7, 11.5, 2.7, 11.1)
draw_arrow(ax, 2.7, 10.2, 2.7,  9.8)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — AWS GLUE
# ══════════════════════════════════════════════════════════════════════════════
draw_section(ax, 5.5, 8.2, 4.8, 5.0, "② ETL & Catálogo — AWS Glue", AWS_TEAL)
draw_box(ax, 5.8, 11.5, 4.2, 0.9, AWS_TEAL, "Glue Crawler",
         "Catalogación automática · Esquemas")
draw_box(ax, 5.8, 10.2, 4.2, 0.9, AWS_TEAL, "Glue Job PySpark (G.2X)",
         "Workers escalables · Millones de filas")
draw_box(ax, 5.8,  8.9, 4.2, 0.9, AWS_TEAL, "Glue Data Catalog",
         "Metadatos · Linaje · Particiones")

draw_arrow(ax, 8.0, 11.5, 8.0, 11.1)
draw_arrow(ax, 8.0, 10.2, 8.0,  9.8)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — AMAZON ECR (NUEVA)
# ══════════════════════════════════════════════════════════════════════════════
draw_section(ax, 10.7, 8.2, 4.6, 5.0, "③ Contenedores — Amazon ECR", AWS_PINK)
draw_box(ax, 11.0, 11.5, 4.0, 0.9, AWS_PINK, "ECR Repository",
         "Imágenes Docker versionadas")
draw_box(ax, 11.0, 10.2, 4.0, 0.9, AWS_PINK, "Docker · Processing Image",
         "Limpieza · Feature Engineering")
draw_box(ax, 11.0,  8.9, 4.0, 0.9, AWS_PINK, "Docker · Training Image",
         "scikit-learn · LogisticRegression")

draw_arrow(ax, 13.0, 11.5, 13.0, 11.1)
draw_arrow(ax, 13.0, 10.2, 13.0,  9.8)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — SAGEMAKER
# ══════════════════════════════════════════════════════════════════════════════
draw_section(ax, 15.7, 8.2, 4.8, 5.0, "④ ML — Amazon SageMaker", AWS_BLUE)
draw_box(ax, 16.0, 11.5, 4.2, 0.9, AWS_BLUE, "SageMaker Pipelines",
         "Orquestación reproducible")
draw_box(ax, 16.0, 10.2, 4.2, 0.9, AWS_BLUE, "Processing + Training Job",
         "Contenedor Docker desde ECR")
draw_box(ax, 16.0,  8.9, 4.2, 0.9, AWS_BLUE, "SageMaker Clarify",
         "SHAP · Explicabilidad · Sesgo")

draw_arrow(ax, 18.1, 11.5, 18.1, 11.1)
draw_arrow(ax, 18.1, 10.2, 18.1,  9.8)

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — MODEL REGISTRY + SERVING (dual: RT + Batch)
# ══════════════════════════════════════════════════════════════════════════════
draw_section(ax, 20.9, 8.2, 4.8, 5.0, "⑤ Registro & Serving", AWS_GREEN)
draw_box(ax, 21.2, 11.5, 4.2, 0.9, AWS_GREEN, "SageMaker Model Registry",
         "Versionado · Aprobación · Linaje")
draw_box(ax, 21.2, 10.2, 4.2, 0.9, AWS_GREEN, "Endpoint (Auto Scaling)",
         "Inferencia tiempo real · REST API")
draw_box(ax, 21.2,  8.9, 4.2, 0.9, AWS_GREEN, "Batch Transform",
         "Scoring masivo · Millones de registros")

draw_arrow(ax, 23.3, 11.5, 23.3, 11.1)
draw_arrow(ax, 23.3, 10.2, 23.3,  9.8)

# ══════════════════════════════════════════════════════════════════════════════
# FLECHAS PRINCIPALES (flujo horizontal)
# ══════════════════════════════════════════════════════════════════════════════
draw_arrow(ax,  5.1, 10.25,  5.5, 10.25, label="Parquet")
draw_arrow(ax, 10.3, 10.25, 10.7, 10.25, label="Pull imagen")
draw_arrow(ax, 15.3, 10.25, 15.7, 10.25, label="Deploy")
draw_arrow(ax, 20.7, 10.25, 20.9, 10.25, label="Registro")

# Flecha ECR → SageMaker (Docker pull)
draw_arrow(ax, 15.0, 9.35, 15.7, 9.35, AWS_PINK, "Docker pull")

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6 — CLOUDWATCH
# ══════════════════════════════════════════════════════════════════════════════
draw_section(ax, 0.3, 5.0, 25.4, 2.7, "⑥ Monitoreo Transversal — Amazon CloudWatch", AWS_RED)
draw_box(ax, 0.6,  5.5, 5.5, 1.0, AWS_RED, "CloudWatch Logs",
         "Logs Glue Jobs · Errores · Trazas")
draw_box(ax, 6.9,  5.5, 5.5, 1.0, AWS_RED, "CloudWatch Metrics",
         "Latencia · Throughput · CPU · Memoria")
draw_box(ax, 13.2, 5.5, 5.5, 1.0, AWS_RED, "SageMaker Model Monitor",
         "Data drift · Model drift · Alertas")
draw_box(ax, 19.5, 5.5, 5.8, 1.0, AWS_RED, "CloudWatch Alarms + SNS",
         "Notificaciones automáticas al equipo")

draw_arrow(ax,  6.1, 6.0,  6.9, 6.0)
draw_arrow(ax, 12.4, 6.0, 13.2, 6.0)
draw_arrow(ax, 18.7, 6.0, 19.5, 6.0)
draw_arrow(ax, 18.1, 8.2, 16.0, 6.5)  # SageMaker → Model Monitor

# ══════════════════════════════════════════════════════════════════════════════
# SECCIÓN 7 — SEGURIDAD
# ══════════════════════════════════════════════════════════════════════════════
draw_section(ax, 0.3, 1.8, 25.4, 2.7, "⑦ Seguridad & Gobernanza", AWS_PURPLE)
draw_box(ax, 0.6,  2.3, 5.5, 1.0, AWS_PURPLE, "IAM Roles & Policies",
         "Mínimo privilegio por servicio")
draw_box(ax, 6.9,  2.3, 5.5, 1.0, AWS_PURPLE, "S3 Encryption (SSE-S3)",
         "Datos en reposo cifrados")
draw_box(ax, 13.2, 2.3, 5.5, 1.0, AWS_PURPLE, "VPC + PrivateLink",
         "Tráfico interno sin internet público")
draw_box(ax, 19.5, 2.3, 5.8, 1.0, AWS_PURPLE, "AWS CloudTrail",
         "Auditoría de accesos y cambios")

# ══════════════════════════════════════════════════════════════════════════════
# LEYENDA
# ══════════════════════════════════════════════════════════════════════════════
leyenda = [
    (AWS_ORANGE, "S3 Data Lake"),
    (AWS_TEAL,   "AWS Glue"),
    (AWS_PINK,   "ECR · Docker"),
    (AWS_BLUE,   "SageMaker"),
    (AWS_GREEN,  "Serving"),
    (AWS_RED,    "CloudWatch"),
    (AWS_PURPLE, "Seguridad"),
]
for i, (color, label) in enumerate(leyenda):
    ax.text(0.8 + i * 3.7, 1.2, "■", color=color, fontsize=12)
    ax.text(1.2 + i * 3.7, 1.2, label, color=WHITE, fontsize=7.5)

ax.text(13, 0.6,
        "Flujo: Ingesta → ETL (Glue) → Contenedor Docker (ECR) → Entrenamiento → Registro → Serving (RT + Batch) → Monitoreo",
        ha="center", color=WHITE, fontsize=8, alpha=0.6)

# ── Guardar ───────────────────────────────────────────────────────────────────
output_file = FIG_PATH / "04_aws_architecture.png"
plt.savefig(output_file, dpi=150, bbox_inches="tight",
            facecolor=AWS_DARK, edgecolor="none")
plt.close()
print(f"✅ Diagrama guardado en: {output_file}")