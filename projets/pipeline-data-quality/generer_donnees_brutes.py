"""
Génère une base de données métier "sale" et réaliste, à nettoyer :
valeurs manquantes, doublons, formats incohérents (dates, téléphones,
e-mails, montants, casse, espaces superflus).

Sortie : donnees_brutes.csv

Auteur : Suz Didolène Massamouna
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(11)
N = 1500

prenoms = ["Camille", "Lucas", "Sarah", "Yanis", "Léa", "Hugo", "Inès", "Nathan",
           "Manon", "Adam", "Chloé", "Rayan", "Jade", "Louis", "Nora"]
noms = ["Martin", "Bernard", "Dubois", "Thomas", "Robert", "Petit", "Durand",
        "Leroy", "Moreau", "Simon", "Laurent", "Garcia", "Diallo", "Nguyen"]
villes_sales = ["paris", "PARIS", " Paris", "Lyon ", "lyon", "LYON", "Marseille",
                "marseille ", " Toulouse", "Bordeaux", "bordeaux", "Lille "]

def tel_format(num):
    s = f"06{num:08d}"[:10]
    style = rng.integers(0, 4)
    if style == 0:   return " ".join(s[i:i+2] for i in range(0, 10, 2))   # 06 12 34 56 78
    if style == 1:   return s                                              # 0612345678
    if style == 2:   return "+33" + s[1:]                                  # +33612345678
    return ".".join(s[i:i+2] for i in range(0, 10, 2))                     # 06.12.34.56.78

def date_format(y, m, d):
    style = rng.integers(0, 3)
    if style == 0:   return f"{y}-{m:02d}-{d:02d}"
    if style == 1:   return f"{d:02d}/{m:02d}/{y}"
    return f"{d:02d}-{m:02d}-{y}"

def montant_format(v):
    style = rng.integers(0, 3)
    if style == 0:   return f"{v:.2f}"                       # 1200.50
    if style == 1:   return f"{v:,.2f}".replace(",", " ").replace(".", ",")  # 1 200,50
    return f"€{v:.2f}"                                       # €1200.50

rows = []
for i in range(N):
    p = rng.choice(prenoms); n = rng.choice(noms)
    email = f"{p}.{n}{1000 + i}@example.com"
    # casse / espaces incohérents sur l'e-mail
    if rng.random() < 0.5: email = email.upper()
    if rng.random() < 0.3: email = "  " + email + " "
    rows.append({
        "id_client": 1000 + i,
        "prenom": ("  " + p) if rng.random() < 0.2 else p,
        "nom": (n + "  ") if rng.random() < 0.2 else n,
        "email": email,
        "telephone": tel_format(rng.integers(0, 99999999)),
        "date_inscription": date_format(rng.integers(2021, 2026), rng.integers(1, 13), rng.integers(1, 28)),
        "ville": rng.choice(villes_sales),
        "montant_achats": montant_format(round(rng.uniform(10, 3000), 2)),
    })

df = pd.DataFrame(rows)

# Injecter des valeurs manquantes
for col, frac in [("email", 0.06), ("telephone", 0.08), ("ville", 0.05), ("montant_achats", 0.07)]:
    idx = rng.choice(df.index, size=int(len(df) * frac), replace=False)
    df.loc[idx, col] = np.nan

# Injecter des doublons (lignes entières répétées)
dups = df.sample(120, random_state=3)
df = pd.concat([df, dups], ignore_index=True)
df = df.sample(frac=1, random_state=5).reset_index(drop=True)

df.to_csv("donnees_brutes.csv", index=False, encoding="utf-8")
print(f"OK : {len(df)} lignes (dont doublons) -> donnees_brutes.csv")
print(f"Valeurs manquantes : {int(df.isna().sum().sum())}")
print(f"Doublons exacts : {int(df.duplicated().sum())}")
