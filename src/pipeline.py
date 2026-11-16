"""Pipeline UCI PhysioNet 2012: carga, métricas por tipo de UCI, índice de Swaroop,
proxy de costo (días de estadía) y modelo de mortalidad.

Uso: .venv/bin/python src/pipeline.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
EXT = ROOT / "data" / "extracted"
OUT = ROOT / "reports"
FIG = OUT / "figs"
FIG.mkdir(parents=True, exist_ok=True)

ICU_TYPES = {1: "Coronaria", 2: "Cirugía cardíaca", 3: "Médica", 4: "Quirúrgica"}
STATIC = ["Age", "Gender", "Height", "ICUType", "Weight"]


def load() -> pd.DataFrame:
    rows = []
    for s in ("a", "b"):
        outc = pd.read_csv(RAW / f"Outcomes-{s}.txt").set_index("RecordID")
        for f in (EXT / f"set-{s}").glob("*.txt"):
            d = pd.read_csv(f)
            st = d[(d.Time == "00:00") & d.Parameter.isin(STATIC + ["RecordID"])]
            r = st.set_index("Parameter").Value.to_dict()
            rid = int(r["RecordID"])
            r = {k: (np.nan if v < 0 else v) for k, v in r.items()}  # -1 = faltante
            r["RecordID"] = rid
            r["set"] = s
            rows.append(r)
    st = pd.DataFrame(rows).set_index("RecordID")
    df = st.join(pd.concat([pd.read_csv(RAW / f"Outcomes-{s}.txt") for s in "ab"]).set_index("RecordID"))
    df = df[df.Length_of_stay > 0].copy()  # LOS<=0 son registros inválidos
    df["Sexo"] = df.Gender.map({0: "F", 1: "M"})
    df["UCI"] = df.ICUType.map(ICU_TYPES)
    df["Muerte"] = df["In-hospital_death"].astype(int)
    df["Edad50"] = df.Age >= 50
    return df


def swaroop(deaths: pd.DataFrame) -> float:
    """Índice de Swaroop: defunciones de >=50 años por 100 defunciones totales."""
    return np.nan if len(deaths) == 0 else 100 * deaths.Edad50.mean()


def metrics_by_group(df: pd.DataFrame) -> pd.DataFrame:
    g = df.groupby("UCI")
    t = pd.DataFrame({
        "n": g.size(),
        "edad_mediana": g.Age.median(),
        "pct_mujeres": g.apply(lambda x: 100 * (x.Sexo == "F").mean()),
        "los_mediana": g.Length_of_stay.median(),
        "los_media": g.Length_of_stay.mean(),
        "los_total_dias": g.Length_of_stay.sum(),
        "mortalidad_pct": g.Muerte.mean() * 100,
        "swaroop": g.apply(lambda x: swaroop(x[x.Muerte == 1])),
        "saps1_media": g["SAPS-I"].mean(),
        "sofa_media": g.SOFA.mean(),
    })
    tot = t.los_total_dias.sum()
    t["pct_carga_dias"] = 100 * t.los_total_dias / tot  # proxy de costo
    return t.round(1)


def model(df: pd.DataFrame) -> dict:
    X = df[["Age", "Gender", "SAPS-I", "SOFA"]].copy()
    X = X.join(pd.get_dummies(df.UCI, drop_first=True).astype(float))
    X = X.fillna(X.median())
    y = df.Muerte
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)
    clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000))
    clf.fit(Xtr, ytr)
    p = clf.predict_proba(Xte)[:, 1]
    coefs = pd.Series(clf[-1].coef_[0], index=X.columns).sort_values()
    return {"auc": roc_auc_score(yte, p), "brier": brier_score_loss(yte, p),
            "n_train": len(Xtr), "n_test": len(Xte), "odds_ratios_std": np.exp(coefs).round(2).to_dict()}


def figures(df, t):
    order = t.sort_values("los_total_dias", ascending=False).index
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.8))
    ax[0].bar(order, t.loc[order, "pct_carga_dias"], color="#3b6ea5")
    ax[0].set_title("Carga de días UCI por tipo (proxy de costo)"); ax[0].set_ylabel("% del total de días")
    ax[1].bar(order, t.loc[order, "mortalidad_pct"], color="#b5483a")
    ax[1].set_title("Mortalidad hospitalaria"); ax[1].set_ylabel("%")
    for a in ax: a.tick_params(axis="x", rotation=20)
    fig.tight_layout(); fig.savefig(FIG / "carga_mortalidad.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 3.8))
    data = [df[df.UCI == u].Length_of_stay.clip(upper=60) for u in order]
    ax.boxplot(data, labels=order, showfliers=False)
    ax.set_title("Días de estadía por tipo de UCI (truncado a 60)"); ax.set_ylabel("días")
    fig.tight_layout(); fig.savefig(FIG / "los_boxplot.png", dpi=160); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 3.8))
    ax.bar(t.index, t.swaroop, color="#6b8e4e"); ax.set_ylim(0, 100)
    ax.set_title("Índice de Swaroop (muertes ≥50 años / 100 muertes)")
    ax.tick_params(axis="x", rotation=20)
    fig.tight_layout(); fig.savefig(FIG / "swaroop.png", dpi=160); plt.close(fig)


def main():
    df = load()
    t = metrics_by_group(df)
    gen = {
        "n": len(df), "mortalidad_pct": round(100 * df.Muerte.mean(), 1),
        "swaroop_global": round(swaroop(df[df.Muerte == 1]), 1),
        "edad_mediana": float(df.Age.median()), "los_mediana": float(df.Length_of_stay.median()),
        "pct_mujeres": round(100 * (df.Sexo == "F").mean(), 1),
        "faltantes_edad": int(df.Age.isna().sum()),
    }
    m = model(df)
    t.to_csv(OUT / "metricas_por_uci.csv")
    (OUT / "resumen.json").write_text(json.dumps({"global": gen, "modelo": m}, indent=2, ensure_ascii=False))
    figures(df, t)
    print(t.to_string()); print(gen); print(m)


if __name__ == "__main__":
    main()
