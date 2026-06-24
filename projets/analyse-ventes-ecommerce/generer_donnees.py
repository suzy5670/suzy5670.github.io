"""
Génère un jeu de données e-commerce réaliste (1 an de commandes).
Sortie : ventes_ecommerce.csv

Auteur : Suz Didolène Massamouna
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)  # résultat reproductible

# --- Catalogue produits : catégorie -> [(produit, prix unitaire)] ---
catalogue = {
    "Électronique": [("Casque audio Bluetooth", 79.90), ("Montre connectée", 149.00),
                     ("Enceinte portable", 59.90), ("Chargeur sans fil", 24.90),
                     ("Écouteurs sans fil", 119.00)],
    "Mode":         [("T-shirt coton bio", 19.90), ("Jean slim", 49.90),
                     ("Sneakers", 89.00), ("Veste légère", 69.90), ("Écharpe laine", 29.90)],
    "Maison":       [("Lampe de bureau LED", 34.90), ("Set de couverts", 44.90),
                     ("Plaid polaire", 24.90), ("Diffuseur d'huiles", 39.90), ("Cadre photo", 14.90)],
    "Beauté":       [("Crème hydratante", 22.90), ("Parfum 50ml", 59.00),
                     ("Palette maquillage", 34.90), ("Sérum visage", 29.90)],
    "Sport":        [("Tapis de yoga", 29.90), ("Haltères 5kg", 39.90),
                     ("Gourde isotherme", 19.90), ("Bandes élastiques", 15.90)],
    "Livres":       [("Roman best-seller", 18.90), ("Livre de cuisine", 24.90),
                     ("BD édition limitée", 29.90)],
}

# Poids de saisonnalité par mois (pics en novembre/décembre = fêtes)
saison = {1: 0.7, 2: 0.7, 3: 0.85, 4: 0.9, 5: 0.95, 6: 0.85,
          7: 0.8, 8: 0.75, 9: 1.0, 10: 1.05, 11: 1.5, 12: 1.7}

canaux = ["Site web", "Application mobile", "Marketplace"]
canaux_p = [0.50, 0.35, 0.15]

regions = ["Île-de-France", "Auvergne-Rhône-Alpes", "Provence-Alpes-Côte d'Azur",
           "Nouvelle-Aquitaine", "Occitanie", "Hauts-de-France", "Grand Est", "Bretagne"]
regions_p = [0.28, 0.16, 0.12, 0.10, 0.10, 0.09, 0.08, 0.07]

paiements = ["Carte bancaire", "PayPal", "Virement"]
paiements_p = [0.62, 0.30, 0.08]

# Aplatir le catalogue
produits = [(cat, nom, prix) for cat, items in catalogue.items() for nom, prix in items]

N = 6000  # nombre de lignes de commande
ANNEE = 2024

# Tirer les mois selon la saisonnalité
mois_list = np.array(list(saison.keys()))
mois_poids = np.array(list(saison.values()))
mois_poids = mois_poids / mois_poids.sum()
mois = rng.choice(mois_list, size=N, p=mois_poids)
jours = rng.integers(1, 28, size=N)
dates = pd.to_datetime({"year": ANNEE, "month": mois, "day": jours})

# Tirer les produits (l'électronique se vend un peu plus)
idx = rng.integers(0, len(produits), size=N)
cats = [produits[i][0] for i in idx]
noms = [produits[i][1] for i in idx]
prix = np.array([produits[i][2] for i in idx])

quantites = rng.choice([1, 2, 3, 4], size=N, p=[0.55, 0.27, 0.12, 0.06])
remises = rng.choice([0.0, 0.0, 0.0, 0.10, 0.20], size=N)  # promo occasionnelle
montants = np.round(quantites * prix * (1 - remises), 2)

df = pd.DataFrame({
    "id_commande": [f"CMD{100000 + i}" for i in range(N)],
    "date": dates.dt.strftime("%Y-%m-%d"),
    "id_client": [f"CLI{c:05d}" for c in rng.integers(1, 2200, size=N)],  # ~2200 clients
    "categorie": cats,
    "produit": noms,
    "quantite": quantites,
    "prix_unitaire": prix,
    "remise": remises,
    "montant": montants,
    "canal": rng.choice(canaux, size=N, p=canaux_p),
    "region": rng.choice(regions, size=N, p=regions_p),
    "paiement": rng.choice(paiements, size=N, p=paiements_p),
})

df = df.sort_values("date").reset_index(drop=True)
df.to_csv("ventes_ecommerce.csv", index=False, encoding="utf-8")
print(f"OK : {len(df)} lignes -> ventes_ecommerce.csv")
print(f"Chiffre d'affaires total simulé : {df['montant'].sum():,.0f} €")
