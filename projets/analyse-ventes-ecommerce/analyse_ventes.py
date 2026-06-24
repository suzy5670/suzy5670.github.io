"""
Analyse des ventes e-commerce.
Lit ventes_ecommerce.csv, calcule les indicateurs clés et génère
les graphiques dans le dossier images/.

Auteur : Suz Didolène Massamouna
Outils : Python, pandas, matplotlib
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

PURPLE = "#6b4eff"
PURPLE_DARK = "#4c32cb"
PALETTE = ["#6b4eff", "#9b87ff", "#4c32cb", "#b9a8ff", "#7c5cff", "#5639e6"]

os.makedirs("images", exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.edgecolor": "#cccccc",
                     "axes.grid": True, "grid.color": "#eeeeee", "figure.dpi": 110})

# --- Chargement ---
df = pd.read_csv("ventes_ecommerce.csv", parse_dates=["date"])
df["mois"] = df["date"].dt.to_period("M").astype(str)

# --- Indicateurs clés (KPIs) ---
ca_total = df["montant"].sum()
nb_commandes = df["id_commande"].nunique()
panier_moyen = df["montant"].mean()
clients_uniques = df["id_client"].nunique()
articles_vendus = int(df["quantite"].sum())

print("=== Indicateurs clés ===")
print(f"Chiffre d'affaires total : {ca_total:,.0f} €")
print(f"Nombre de commandes      : {nb_commandes:,}")
print(f"Panier moyen             : {panier_moyen:,.2f} €")
print(f"Clients uniques          : {clients_uniques:,}")
print(f"Articles vendus          : {articles_vendus:,}")


def euro(x, pos):
    return f"{x:,.0f} €".replace(",", " ")


# --- 1. Chiffre d'affaires mensuel ---
ca_mois = df.groupby("mois")["montant"].sum()
fig, ax = plt.subplots(figsize=(9, 4.2))
ax.plot(ca_mois.index, ca_mois.values, marker="o", color=PURPLE, linewidth=2.5)
ax.fill_between(range(len(ca_mois)), ca_mois.values, color=PURPLE, alpha=0.08)
ax.set_title("Chiffre d'affaires mensuel", fontsize=13, fontweight="bold", color=PURPLE_DARK)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(euro))
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig("images/ca_mensuel.png")
plt.close()

# --- 2. Top 10 produits par CA ---
top_prod = df.groupby("produit")["montant"].sum().sort_values(ascending=True).tail(10)
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.barh(top_prod.index, top_prod.values, color=PURPLE)
ax.set_title("Top 10 des produits par chiffre d'affaires", fontsize=13, fontweight="bold", color=PURPLE_DARK)
ax.xaxis.set_major_formatter(mticker.FuncFormatter(euro))
plt.tight_layout()
plt.savefig("images/top_produits.png")
plt.close()

# --- 3. CA par catégorie ---
ca_cat = df.groupby("categorie")["montant"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.bar(ca_cat.index, ca_cat.values, color=PALETTE)
ax.set_title("Chiffre d'affaires par catégorie", fontsize=13, fontweight="bold", color=PURPLE_DARK)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(euro))
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig("images/ca_categorie.png")
plt.close()

# --- 4. Répartition des ventes par canal ---
ca_canal = df.groupby("canal")["montant"].sum().sort_values(ascending=False)
fig, ax = plt.subplots(figsize=(6, 5))
ax.pie(ca_canal.values, labels=ca_canal.index, autopct="%1.1f%%",
       colors=PALETTE, startangle=90, wedgeprops={"edgecolor": "white", "linewidth": 2})
ax.set_title("Répartition du CA par canal de vente", fontsize=13, fontweight="bold", color=PURPLE_DARK)
plt.tight_layout()
plt.savefig("images/ca_canal.png")
plt.close()

# --- Synthèse écrite ---
mois_top = ca_mois.idxmax()
cat_top = ca_cat.idxmax()
prod_top = top_prod.index[-1]
canal_top = ca_canal.idxmax()

with open("synthese.md", "w", encoding="utf-8") as f:
    f.write("# Synthèse de l'analyse\n\n")
    f.write(f"- **Chiffre d'affaires total** : {ca_total:,.0f} €\n")
    f.write(f"- **Commandes** : {nb_commandes:,} | **Panier moyen** : {panier_moyen:,.2f} €\n")
    f.write(f"- **Clients uniques** : {clients_uniques:,}\n")
    f.write(f"- **Meilleur mois** : {mois_top} (effet fêtes de fin d'année)\n")
    f.write(f"- **Catégorie n°1** : {cat_top}\n")
    f.write(f"- **Produit n°1** : {prod_top}\n")
    f.write(f"- **Canal principal** : {canal_top}\n")

print("\nGraphiques générés dans images/ et synthèse écrite (synthese.md).")
