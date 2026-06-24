"""
Pipeline d'industrialisation du nettoyage de données.
Lit donnees_brutes.csv, applique un nettoyage automatisé (valeurs manquantes,
dédoublonnage strict, standardisation des formats) et produit :
  - donnees_propres.csv  (données nettoyées)
  - rapport_qualite.md   (rapport avant / après)
  - images/avant_apres.png

Auteur : Suz Didolène Massamouna
Outils : Python, pandas
"""
import os
import re
import pandas as pd
import matplotlib.pyplot as plt

PURPLE = "#6b4eff"
PURPLE_DARK = "#4c32cb"
os.makedirs("images", exist_ok=True)

df = pd.read_csv("donnees_brutes.csv", dtype=str)
n_depart = len(df)

# --- Mesure qualité AVANT ---
manquantes_avant = int(df.isna().sum().sum())
doublons_avant = int(df.duplicated().sum())


def nettoyer_telephone(val):
    if pd.isna(val):
        return None
    chiffres = re.sub(r"\D", "", str(val))          # ne garder que les chiffres
    if chiffres.startswith("33"):
        chiffres = "0" + chiffres[2:]
    if len(chiffres) == 10:
        return "+33 " + " ".join(chiffres[i:i+2] for i in range(0, 10, 2))[1:].strip()
    return None


def nettoyer_montant(val):
    if pd.isna(val):
        return None
    s = re.sub(r"[€\s]", "", str(val)).replace(",", ".")
    try:
        return round(float(s), 2)
    except ValueError:
        return None


# --- 1. Standardisation des formats ---
df["prenom"] = df["prenom"].str.strip().str.title()
df["nom"] = df["nom"].str.strip().str.title()
df["email"] = df["email"].str.strip().str.lower()
df["ville"] = df["ville"].str.strip().str.title()
df["telephone"] = df["telephone"].apply(nettoyer_telephone)
df["montant_achats"] = df["montant_achats"].apply(nettoyer_montant)
df["date_inscription"] = pd.to_datetime(df["date_inscription"], dayfirst=True,
                                        errors="coerce", format="mixed").dt.strftime("%Y-%m-%d")

# --- 2. Gestion des valeurs manquantes ---
# montant manquant -> 0 (pas d'achat connu) ; ville manquante -> "Inconnu"
df["montant_achats"] = df["montant_achats"].fillna(0.0)
df["ville"] = df["ville"].fillna("Inconnu")
df["telephone"] = df["telephone"].fillna("Non renseigné")
df["date_inscription"] = df["date_inscription"].fillna("Non renseigné")
# e-mail = donnée critique : on supprime les lignes sans e-mail
df = df[df["email"].notna() & (df["email"] != "")]

# --- 3. Dédoublonnage strict ---
df = df.drop_duplicates()                       # doublons exacts
df = df.drop_duplicates(subset="email", keep="first")  # un client = un e-mail

df = df.reset_index(drop=True)
n_final = len(df)
manquantes_apres = int(df.isna().sum().sum())
doublons_apres = int(df.duplicated().sum())

df.to_csv("donnees_propres.csv", index=False, encoding="utf-8")

# --- Rapport ---
with open("rapport_qualite.md", "w", encoding="utf-8") as f:
    f.write("# Rapport de qualité des données\n\n")
    f.write("| Indicateur | Avant | Après |\n|---|---|---|\n")
    f.write(f"| Lignes | {n_depart} | {n_final} |\n")
    f.write(f"| Valeurs manquantes | {manquantes_avant} | {manquantes_apres} |\n")
    f.write(f"| Doublons exacts | {doublons_avant} | {doublons_apres} |\n\n")
    f.write(f"- Lignes supprimées (doublons / e-mail manquant) : **{n_depart - n_final}**\n")
    f.write("- Formats standardisés : téléphone (+33), dates (AAAA-MM-JJ), montants (float), casse harmonisée.\n")

print("=== Nettoyage terminé ===")
print(f"Lignes : {n_depart} -> {n_final}")
print(f"Valeurs manquantes : {manquantes_avant} -> {manquantes_apres}")
print(f"Doublons : {doublons_avant} -> {doublons_apres}")

# --- Graphique avant / après ---
labels = ["Valeurs\nmanquantes", "Doublons", "Lignes"]
avant = [manquantes_avant, doublons_avant, n_depart]
apres = [manquantes_apres, doublons_apres, n_final]
x = range(len(labels)); w = 0.38
fig, ax = plt.subplots(figsize=(8, 4.4))
ax.bar([i - w/2 for i in x], avant, width=w, label="Avant", color="#c4b8f0")
ax.bar([i + w/2 for i in x], apres, width=w, label="Après", color=PURPLE)
ax.set_xticks(list(x)); ax.set_xticklabels(labels)
ax.set_title("Qualité des données : avant / après nettoyage", fontsize=13, fontweight="bold", color=PURPLE_DARK)
ax.legend()
plt.tight_layout(); plt.savefig("images/avant_apres.png"); plt.close()
print("Graphique -> images/avant_apres.png")
