"""
generate_synthetic_data.py
Genera archivo de datos crudos raw_data_customers.csv con:
- 10.300 filas
- tasa de churn ~20-35% de filas
- variables sensibles
- nulos (~8% de filas)
- duplicados (~3% de filas)
- fechas mal formateadas (~10% de filas)
- 325 outliers extremos en valor_total_6m.
"""

import pandas as pd
import numpy as np
from faker import Faker
from pathlib import Path

# ── Configuración ─────────────────────────────────────────────────────────────
SEED        = 42
N           = 10_000
OUTPUT_PATH = Path("1_data/1_raw/raw_data_customers.csv")

rng  = np.random.default_rng(SEED)
fake = Faker("es_CO")
Faker.seed(SEED)

# ── 1. Columnas base ──────────────────────────────────────────────────────────
customer_ids = [f"CLI{str(i).zfill(6)}" for i in range(1, N + 1)]

ciudades = [
    "Bogotá","Medellín","Cali","Barranquilla","Bucaramanga",
    "Cartagena","Cúcuta","Pereira","Manizales","Pasto"
]
tipos_cliente   = ["Natural","Empresa","Ecommerce"]
canales         = ["App","Web","Punto físico","API"]

ciudad          = rng.choice(ciudades,      N, p=[.30,.20,.15,.10,.07,.07,.04,.04,.02,.01])
tipo_cliente    = rng.choice(tipos_cliente, N, p=[.50,.30,.20])
canal_principal = rng.choice(canales,       N, p=[.35,.30,.25,.10])
tiene_contrato  = rng.choice([0, 1],        N, p=[.65,.35])

# ── 2. Fechas de registro (2019-2024) ─────────────────────────────────────────
dias_offset     = rng.integers(0, 365 * 5, N)
fecha_registro  = pd.to_datetime("2019-01-01") + pd.to_timedelta(dias_offset, unit="D")
antiguedad_dias = (pd.Timestamp("2024-12-31") - fecha_registro).days

# ── 3. Variables de comportamiento ────────────────────────────────────────────
num_reclamos_6m      = rng.poisson(lam=1.2, size=N)
tasa_entrega_exitosa = np.clip(rng.normal(0.88, 0.08, N), 0.50, 1.00)
nps_score            = np.clip(rng.normal(6.5, 2.2, N), 0, 10).round(1)

base_envios   = np.where(tipo_cliente == "Ecommerce", 18,
                np.where(tipo_cliente == "Empresa",   12, 4))
num_envios_6m = np.clip(rng.poisson(lam=base_envios, size=N), 0, None)

base_ticket     = np.where(tipo_cliente == "Ecommerce", 18_000,
                  np.where(tipo_cliente == "Empresa",   45_000, 12_000))
ticket_promedio = np.clip(
    rng.normal(base_ticket, base_ticket * 0.30, N), 3_000, None
).round(-2)

valor_total_6m    = (num_envios_6m * ticket_promedio).round(-2)
dias_ultimo_envio = np.clip(rng.exponential(scale=45, size=N), 1, 365).astype(int)

# ── 4. Variable objetivo: churn (logit recalibrado) ───────────────────────────
# Normalizar variables para que los coeficientes sean comparables
reclamos_norm  = (num_reclamos_6m - 1.2) / 1.1
nps_norm       = (nps_score - 6.5) / 2.2
recencia_norm  = (dias_ultimo_envio - 45) / 45
envios_norm    = (num_envios_6m - 8) / 6
entrega_norm   = (tasa_entrega_exitosa - 0.88) / 0.08

logit = (
    -0.80                        # intercepto: ~31% base antes de features
    + 0.80  * reclamos_norm      # más reclamos  → más churn
    - 0.70  * nps_norm           # mayor NPS     → menos churn
    + 0.60  * recencia_norm      # más días sin enviar → más churn
    - 0.50  * envios_norm        # más envíos    → menos churn
    - 0.60  * tiene_contrato     # contrato      → retiene
    - 0.50  * entrega_norm       # buena entrega → retiene
)

prob_churn = 1 / (1 + np.exp(-logit))
churn      = rng.binomial(1, prob_churn, N)
print(f"Tasa de churn generada: {churn.mean():.2%}")

# ── 5. Variables sensibles (PII) ──────────────────────────────────────────────
nombres   = [fake.name()         for _ in range(N)]
emails    = [fake.email()        for _ in range(N)]
telefonos = [fake.phone_number() for _ in range(N)]

# ── 6. Ensamblar DataFrame ────────────────────────────────────────────────────
df = pd.DataFrame({
    "customer_id"         : customer_ids,
    "nombre"              : nombres,
    "email"               : emails,
    "telefono"            : telefonos,
    "fecha_registro"      : fecha_registro.strftime("%Y-%m-%d"),  # string desde inicio
    "antiguedad_dias"     : antiguedad_dias,
    "ciudad"              : ciudad,
    "tipo_cliente"        : tipo_cliente,
    "canal_principal"     : canal_principal,
    "tiene_contrato"      : tiene_contrato,
    "num_envios_6m"       : num_envios_6m,
    "valor_total_6m"      : valor_total_6m,
    "ticket_promedio"     : ticket_promedio,
    "dias_ultimo_envio"   : dias_ultimo_envio,
    "num_reclamos_6m"     : num_reclamos_6m,
    "tasa_entrega_exitosa": tasa_entrega_exitosa.round(4),
    "nps_score"           : nps_score,
    "churn"               : churn,
})

# ── 7. Suciedad: outliers extremos en valor_total_6m (325 filas) ──────────────
outlier_idx = rng.choice(N, size=325, replace=False)
df.loc[outlier_idx, "valor_total_6m"] = rng.uniform(
    5_000_000, 50_000_000, size=325
).round(-3)

# ── 8. Suciedad: fechas mal formateadas (~10%) — compatible Windows ───────────
bad_date_idx = rng.choice(N, size=int(N * 0.10), replace=False)

def corromper_fecha(fecha_str, formato_id):
    """Recibe string 'YYYY-MM-DD', devuelve formato corrupto."""
    try:
        d = pd.Timestamp(fecha_str)
        if formato_id == 0:
            return f"{d.day:02d}/{d.month:02d}/{d.year}"        # DD/MM/YYYY
        elif formato_id == 1:
            return f"{d.month:02d}-{d.day:02d}-{d.year}"       # MM-DD-YYYY
        elif formato_id == 2:
            return f"{d.year}{d.month:02d}{d.day:02d}"         # YYYYMMDD
        elif formato_id == 3:
            meses = ["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"]
            return f"{d.day} {meses[d.month-1]} {d.year}"      # 15 Jan 2022
        else:
            return "99/99/9999"
    except Exception:
        return "99/99/9999"

formato_ids = rng.integers(0, 5, size=len(bad_date_idx))
for i, fmt_id in zip(bad_date_idx, formato_ids):
    df.loc[i, "fecha_registro"] = corromper_fecha(
        df.loc[i, "fecha_registro"], int(fmt_id)
    )

# ── 9. Suciedad: nulos aleatorios (~8%) ───────────────────────────────────────
nullable_cols = [
    "antiguedad_dias","ciudad","tipo_cliente","canal_principal",
    "num_envios_6m","valor_total_6m","ticket_promedio",
    "dias_ultimo_envio","num_reclamos_6m","tasa_entrega_exitosa","nps_score",
]
total_cells = N * len(nullable_cols)
n_nulls     = int(total_cells * 0.08)
null_rows   = rng.integers(0, N,                  size=n_nulls)
null_cols   = rng.integers(0, len(nullable_cols), size=n_nulls)
for r, c in zip(null_rows, null_cols):
    df.loc[r, nullable_cols[c]] = np.nan

# ── 10. Suciedad: duplicados (~3%) ────────────────────────────────────────────
n_dupes  = int(N * 0.03)
dup_idx  = rng.choice(N, size=n_dupes, replace=False)
df_dupes = df.iloc[dup_idx].copy()
df       = pd.concat([df, df_dupes], ignore_index=True)
df       = df.sample(frac=1, random_state=SEED).reset_index(drop=True)

# ── 11. Guardar ───────────────────────────────────────────────────────────────
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)

print(f"Dataset guardado en  : {OUTPUT_PATH}")
print(f"Filas totales        : {len(df):,}")
print(f"\nNulos por columna:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
print(f"\nMuestra fechas corruptas:")
print(df.loc[bad_date_idx[:8], 'fecha_registro'].values)