"""
Génère un jeu de données réaliste d'incidents ITSM (type GLPI / ServiceNow).
Sortie : incidents.csv

Auteur : Suz Didolène Massamouna
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
N = 3200
ANNEE = 2025

priorites = ["P1 - Critique", "P2 - Haute", "P3 - Moyenne", "P4 - Basse"]
prio_p = [0.07, 0.20, 0.45, 0.28]
sla_cible = {"P1 - Critique": 4, "P2 - Haute": 8, "P3 - Moyenne": 24, "P4 - Basse": 72}  # heures

categories = ["Réseau", "Poste de travail", "Messagerie", "Applicatif métier", "Téléphonie", "Sécurité"]
cat_p = [0.15, 0.30, 0.18, 0.20, 0.07, 0.10]

equipes = ["Support N1", "Support N2", "Infrastructure", "Sécurité SI"]
equipe_p = [0.45, 0.30, 0.18, 0.07]

sources = ["GLPI", "ServiceNow"]
source_p = [0.6, 0.4]

# Dates d'ouverture réparties sur l'année (léger pic rentrée sept.)
mois_w = np.array([1.0, 1.0, 1.05, 1.0, 0.95, 0.8, 0.7, 0.85, 1.2, 1.1, 1.05, 0.9])
mois_w = mois_w / mois_w.sum()
mois = rng.choice(np.arange(1, 13), size=N, p=mois_w)
jours = rng.integers(1, 28, size=N)
heures = rng.integers(7, 20, size=N)
date_ouv = pd.to_datetime({"year": ANNEE, "month": mois, "day": jours,
                           "hour": heures, "minute": rng.integers(0, 60, size=N)})

prio = rng.choice(priorites, size=N, p=prio_p)

# Délai de résolution (heures) : dépend de la priorité, avec dispersion
base = np.array([sla_cible[p] for p in prio], dtype=float)
facteur = rng.lognormal(mean=-0.15, sigma=0.6, size=N)   # parfois < SLA, parfois >
delai_h = np.round(base * facteur, 1)
delai_h = np.clip(delai_h, 0.2, None)

# 92% des incidents sont résolus, les autres encore en cours
resolu = rng.random(N) < 0.92
date_res = date_ouv + pd.to_timedelta(np.where(resolu, delai_h, np.nan), unit="h")

sla_respecte = np.where(resolu, delai_h <= base, np.nan)

df = pd.DataFrame({
    "id_incident": [f"INC{200000 + i}" for i in range(N)],
    "date_ouverture": date_ouv.dt.strftime("%Y-%m-%d %H:%M"),
    "date_resolution": pd.Series(date_res).dt.strftime("%Y-%m-%d %H:%M"),
    "priorite": prio,
    "categorie": rng.choice(categories, size=N, p=cat_p),
    "equipe": rng.choice(equipes, size=N, p=equipe_p),
    "source": rng.choice(sources, size=N, p=source_p),
    "statut": np.where(resolu, "Résolu", "En cours"),
    "sla_cible_h": base.astype(int),
    "delai_resolution_h": np.where(resolu, delai_h, np.nan),
    "sla_respecte": np.where(resolu, np.where(sla_respecte == 1, "Oui", "Non"), ""),
})

df = df.sort_values("date_ouverture").reset_index(drop=True)
df.to_csv("incidents.csv", index=False, encoding="utf-8")
print(f"OK : {len(df)} incidents -> incidents.csv")
print(f"Résolus : {resolu.sum()} | En cours : {(~resolu).sum()}")
