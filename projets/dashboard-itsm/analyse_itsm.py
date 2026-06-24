"""
Analyse de la performance ITSM (incidents).
Calcule les indicateurs d'un tableau de bord d'aide à la décision
(volumes, MTTR, respect des SLA) et génère les graphiques.

Auteur : Suz Didolène Massamouna
Outils : Python, pandas, matplotlib (données modélisées pour Power BI / Excel)
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

PURPLE = "#6b4eff"
PURPLE_DARK = "#4c32cb"
PALETTE = ["#6b4eff", "#9b87ff", "#4c32cb", "#b9a8ff", "#7c5cff", "#5639e6"]

os.makedirs("images", exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.grid": True,
                     "grid.color": "#eeeeee", "figure.dpi": 110})

df = pd.read_csv("incidents.csv", parse_dates=["date_ouverture"])
resolus = df[df["statut"] == "Résolu"].copy()

# --- KPIs ---
total = len(df)
nb_resolus = len(resolus)
taux_resolution = nb_resolus / total
mttr = resolus["delai_resolution_h"].mean()           # délai moyen de résolution
taux_sla = (resolus["sla_respecte"] == "Oui").mean()   # % SLA respecté
nb_p1 = (df["priorite"] == "P1 - Critique").sum()

print("=== Indicateurs ITSM ===")
print(f"Incidents (total)         : {total}")
print(f"Taux de résolution        : {taux_resolution:.1%}")
print(f"MTTR (délai moyen)        : {mttr:.1f} h")
print(f"Respect du SLA            : {taux_sla:.1%}")
print(f"Incidents critiques (P1)  : {nb_p1}")

# --- 1. Volume d'incidents par mois ---
vol_mois = df.set_index("date_ouverture").resample("MS").size()
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(vol_mois.index, vol_mois.values, marker="o", color=PURPLE, linewidth=2.5)
ax.fill_between(vol_mois.index, vol_mois.values, color=PURPLE, alpha=0.08)
ax.set_title("Volume d'incidents par mois", fontsize=13, fontweight="bold", color=PURPLE_DARK)
ax.set_ylabel("Nombre d'incidents")
plt.tight_layout(); plt.savefig("images/volume_mensuel.png"); plt.close()

# --- 2. Répartition par catégorie ---
par_cat = df["categorie"].value_counts()
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(par_cat.index, par_cat.values, color=PALETTE)
ax.set_title("Incidents par catégorie", fontsize=13, fontweight="bold", color=PURPLE_DARK)
plt.xticks(rotation=20, ha="right")
plt.tight_layout(); plt.savefig("images/par_categorie.png"); plt.close()

# --- 3. MTTR moyen par priorité ---
ordre = ["P1 - Critique", "P2 - Haute", "P3 - Moyenne", "P4 - Basse"]
mttr_prio = resolus.groupby("priorite")["delai_resolution_h"].mean().reindex(ordre)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(mttr_prio.index, mttr_prio.values, color=PURPLE)
ax.set_title("Délai moyen de résolution (MTTR) par priorité", fontsize=13, fontweight="bold", color=PURPLE_DARK)
ax.set_ylabel("Heures")
plt.tight_layout(); plt.savefig("images/mttr_priorite.png"); plt.close()

# --- 4. Taux de respect du SLA par priorité ---
sla_prio = resolus.assign(ok=resolus["sla_respecte"].eq("Oui")).groupby("priorite")["ok"].mean().reindex(ordre)
fig, ax = plt.subplots(figsize=(8, 4.2))
bars = ax.bar(sla_prio.index, sla_prio.values * 100, color=PALETTE)
ax.set_title("Taux de respect du SLA par priorité", fontsize=13, fontweight="bold", color=PURPLE_DARK)
ax.set_ylabel("% SLA respecté"); ax.set_ylim(0, 100)
for b, v in zip(bars, sla_prio.values):
    ax.text(b.get_x() + b.get_width() / 2, v * 100 + 1, f"{v:.0%}", ha="center", fontsize=9)
plt.tight_layout(); plt.savefig("images/sla_priorite.png"); plt.close()

# --- Synthèse ---
with open("synthese.md", "w", encoding="utf-8") as f:
    f.write("# Synthèse ITSM\n\n")
    f.write(f"- Incidents traités : {total}\n")
    f.write(f"- Taux de résolution : {taux_resolution:.1%}\n")
    f.write(f"- MTTR (délai moyen) : {mttr:.1f} h\n")
    f.write(f"- Respect du SLA : {taux_sla:.1%}\n")
    f.write(f"- Catégorie n°1 : {par_cat.index[0]} ({par_cat.iloc[0]} incidents)\n")

print("\nGraphiques générés dans images/.")
