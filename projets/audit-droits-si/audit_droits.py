"""
Audit analytique des droits d'accès (gouvernance SI).
Croise les tables utilisateurs et accès pour cartographier les habilitations,
détecter les anomalies de droits et générer un rapport de conformité.

Auteur : Suz Didolène Massamouna
Outils : Python, pandas (audit de données type Active Directory)
"""
import os
import pandas as pd
import matplotlib.pyplot as plt

PURPLE = "#6b4eff"
PURPLE_DARK = "#4c32cb"
DATE_AUDIT = pd.Timestamp("2025-12-31")
SEUIL_INACTIF = 90  # jours

os.makedirs("images", exist_ok=True)

users = pd.read_csv("utilisateurs.csv", parse_dates=["derniere_connexion"])
acces = pd.read_csv("acces.csv")

users["jours_inactif"] = (DATE_AUDIT - users["derniere_connexion"]).dt.days

# Fusion (left sur accès pour repérer les orphelins)
df = acces.merge(users, on="id_utilisateur", how="left")

anomalies = {}

# 1. Comptes orphelins : accès rattaché à un utilisateur inexistant
orphelins = df[df["statut"].isna()]["id_utilisateur"].nunique()
anomalies["Comptes orphelins"] = orphelins

# 2. Accès d'utilisateurs ayant quitté l'entreprise (statut = Parti)
acces_partis = df[df["statut"] == "Parti"]["id_utilisateur"].nunique()
anomalies["Accès de comptes partis"] = acces_partis

# 3. Comptes inactifs (>90 j) conservant des accès
inactifs_avec_acces = df[(df["statut"] != "Parti") &
                         (df["jours_inactif"] > SEUIL_INACTIF)]["id_utilisateur"].nunique()
anomalies["Comptes inactifs avec accès"] = inactifs_avec_acces

# 4. Droits Admin hors service IT
admin_hors_it = df[(df["niveau"] == "Admin") &
                   (df["departement"] != "IT") &
                   (df["statut"].notna())]["id_utilisateur"].nunique()
anomalies["Droits Admin hors IT"] = admin_hors_it

# 5. Conflits de séparation des tâches (Validation + Paiement)
pivot = acces[acces["ressource"].isin(["Compta-Validation", "Compta-Paiement"])]
sod = pivot.groupby("id_utilisateur")["ressource"].nunique()
conflits_sod = int((sod >= 2).sum())
anomalies["Conflits séparation des tâches"] = conflits_sod

# 6. Utilisateurs actifs sans aucun accès (comptes dormants)
sans_acces = set(users["id_utilisateur"]) - set(acces["id_utilisateur"])
anomalies["Utilisateurs sans accès"] = len(sans_acces)

total_anomalies = sum(anomalies.values())
nb_users = len(users)
nb_acces = len(acces)

print("=== Audit des droits SI ===")
print(f"Utilisateurs : {nb_users} | Lignes d'accès : {nb_acces}")
for k, v in anomalies.items():
    print(f"  - {k} : {v}")
print(f"TOTAL anomalies : {total_anomalies}")

# --- Export du détail des anomalies critiques ---
critiques = pd.concat([
    df[df["statut"] == "Parti"].assign(anomalie="Compte parti avec accès"),
    df[(df["statut"] != "Parti") & (df["jours_inactif"] > SEUIL_INACTIF)].assign(anomalie="Compte inactif avec accès"),
    df[df["statut"].isna()].assign(anomalie="Compte orphelin"),
])[["id_utilisateur", "nom", "departement", "statut", "ressource", "niveau", "anomalie"]]
critiques.to_csv("anomalies_detectees.csv", index=False, encoding="utf-8")

# --- Rapport de conformité ---
with open("rapport_conformite.md", "w", encoding="utf-8") as f:
    f.write("# Rapport de conformité des droits d'accès\n\n")
    f.write(f"*Date d'audit : {DATE_AUDIT.date()} — Seuil d'inactivité : {SEUIL_INACTIF} jours*\n\n")
    f.write(f"- Utilisateurs analysés : **{nb_users}**\n")
    f.write(f"- Lignes d'accès analysées : **{nb_acces}**\n")
    f.write(f"- **Anomalies détectées : {total_anomalies}**\n\n")
    f.write("| Type d'anomalie | Nombre |\n|---|---|\n")
    for k, v in anomalies.items():
        f.write(f"| {k} | {v} |\n")

# --- Graphique des anomalies ---
fig, ax = plt.subplots(figsize=(9, 4.6))
noms_a = list(anomalies.keys())
vals = list(anomalies.values())
ax.barh(noms_a, vals, color=PURPLE)
for i, v in enumerate(vals):
    ax.text(v + 0.2, i, str(v), va="center", fontsize=10, fontweight="bold")
ax.set_title("Anomalies de droits détectées", fontsize=13, fontweight="bold", color=PURPLE_DARK)
ax.invert_yaxis()
plt.tight_layout(); plt.savefig("images/anomalies.png"); plt.close()
print("\nRapport et graphique générés.")
