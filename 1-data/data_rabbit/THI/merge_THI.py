# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 10:28:15 2025

@author: titou
"""
import pandas as pd


df2 = pd.read_csv("thi_formated.csv", sep=";")
df1 = pd.read_csv("current_df_rabbit.csv",sep=";")

df1["datetime"] = pd.to_datetime(df1["datetime"])
df2["datetime"] = pd.to_datetime(df2["datetime"])

# =========================
# 3. Définition des clés
# =========================
keys = ["id_rabbit", "datetime"]

# =========================
# 4. Nettoyage de df2
#    (suppression des colonnes redondantes)
# =========================
common_cols = df1.columns.intersection(df2.columns)
cols_to_drop = [c for c in common_cols if c not in keys]

df2_clean = df2.drop(columns=cols_to_drop)

# =========================
# 5. (Optionnel) suppression doublons df2
# =========================
df2_clean = df2_clean.drop_duplicates(subset=keys)

# =========================
# 6. Fusion
# =========================
df_merge = pd.merge(
    df1,
    df2_clean,
    on=keys,
    how="left"
)

# =========================
# 7. Export CSV
# =========================
df_merge.to_csv(
    "fichier_fusionne.csv",
    index=False,
    sep=";",
    encoding="utf-8-sig"
)

print("✅ Fusion terminée : fichier_fusionne.csv")