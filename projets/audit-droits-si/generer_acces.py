"""
Génère deux tables (utilisateurs et accès) type Active Directory,
avec des anomalies de droits réalistes à détecter lors de l'audit.

Sorties : utilisateurs.csv, acces.csv

Auteur : Suz Didolène Massamouna
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(21)
DATE_AUDIT = pd.Timestamp("2025-12-31")

N_USERS = 250
departements = ["Finance", "RH", "IT", "Commercial", "Production", "Direction"]
dep_p = [0.16, 0.10, 0.14, 0.22, 0.30, 0.08]
ressources = ["ERP-Finance", "Paie-RH", "CRM", "Messagerie", "VPN", "Sauvegarde",
              "AD-Admin", "Compta-Validation", "Compta-Paiement"]
niveaux = ["Lecture", "Écriture", "Admin"]

prenoms = ["Camille", "Lucas", "Sarah", "Yanis", "Léa", "Hugo", "Inès", "Nathan",
           "Manon", "Adam", "Chloé", "Rayan", "Jade", "Louis", "Nora", "Karim"]
noms = ["Martin", "Bernard", "Dubois", "Thomas", "Petit", "Durand", "Leroy",
        "Moreau", "Simon", "Laurent", "Garcia", "Diallo", "Nguyen", "Faure"]

# --- Table utilisateurs ---
users = []
for i in range(N_USERS):
    statut = rng.choice(["Actif", "Inactif", "Parti"], p=[0.80, 0.12, 0.08])
    # date de dernière connexion
    if statut == "Parti":
        jours = rng.integers(120, 400)
    elif statut == "Inactif":
        jours = rng.integers(95, 300)
    else:
        jours = rng.integers(0, 80)
    derniere = DATE_AUDIT - pd.Timedelta(days=int(jours))
    users.append({
        "id_utilisateur": f"U{1000 + i}",
        "nom": f"{rng.choice(prenoms)} {rng.choice(noms)}",
        "departement": rng.choice(departements, p=dep_p),
        "statut": statut,
        "derniere_connexion": derniere.strftime("%Y-%m-%d"),
    })
df_users = pd.DataFrame(users)

# --- Table accès ---
# Ressources "métier" attribuables à tous (l'accès AD-Admin est réservé à l'IT)
ressources_base = [r for r in ressources if r != "AD-Admin"]


def date_attrib():
    return (DATE_AUDIT - pd.Timedelta(days=int(rng.integers(30, 900)))).strftime("%Y-%m-%d")


acces = []
for u in df_users.itertuples():
    nb = rng.integers(1, 6)
    res = rng.choice(ressources_base, size=nb, replace=False)
    for r in res:
        if u.departement == "IT":
            niv = rng.choice(niveaux, p=[0.40, 0.35, 0.25])   # l'IT a plus de droits élevés
        else:
            niv = rng.choice(niveaux, p=[0.62, 0.35, 0.03])   # Admin rare hors IT
        acces.append({"id_utilisateur": u.id_utilisateur, "ressource": r,
                      "niveau": niv, "date_attribution": date_attrib()})
    # L'accès AD-Admin n'est légitimement attribué qu'à une partie de l'IT
    if u.departement == "IT" and rng.random() < 0.5:
        acces.append({"id_utilisateur": u.id_utilisateur, "ressource": "AD-Admin",
                      "niveau": "Admin", "date_attribution": date_attrib()})
df_acces = pd.DataFrame(acces)

# Anomalie injectée : 5 utilisateurs hors IT possédant un accès AD-Admin (droit excessif)
hors_it = df_users[(df_users["statut"] == "Actif") & (df_users["departement"] != "IT")].sample(5, random_state=4)["id_utilisateur"]
for uid in hors_it:
    acces.append({"id_utilisateur": uid, "ressource": "AD-Admin",
                  "niveau": "Admin", "date_attribution": "2024-06-01"})
df_acces = pd.DataFrame(acces)

# --- Injection volontaire d'anomalies ---
# 1. Comptes orphelins : accès vers des utilisateurs inexistants
for k in range(8):
    df_acces = pd.concat([df_acces, pd.DataFrame([{
        "id_utilisateur": f"U9{900 + k}", "ressource": rng.choice(ressources),
        "niveau": rng.choice(niveaux), "date_attribution": "2024-03-15"}])], ignore_index=True)

# 2. Conflits de séparation des tâches : forcer quelques utilisateurs à avoir
#    Compta-Validation ET Compta-Paiement
cibles = df_users[df_users["statut"] == "Actif"].sample(6, random_state=2)["id_utilisateur"]
for uid in cibles:
    for r in ["Compta-Validation", "Compta-Paiement"]:
        df_acces = pd.concat([df_acces, pd.DataFrame([{
            "id_utilisateur": uid, "ressource": r, "niveau": "Écriture",
            "date_attribution": "2024-09-01"}])], ignore_index=True)

df_acces = df_acces.drop_duplicates(subset=["id_utilisateur", "ressource"]).reset_index(drop=True)

df_users.to_csv("utilisateurs.csv", index=False, encoding="utf-8")
df_acces.to_csv("acces.csv", index=False, encoding="utf-8")
print(f"OK : {len(df_users)} utilisateurs -> utilisateurs.csv")
print(f"OK : {len(df_acces)} lignes d'accès -> acces.csv")
