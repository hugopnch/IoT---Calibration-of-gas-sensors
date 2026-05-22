# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 15:12:57 2025

@author: titou
"""

import os
import glob
import pandas as pd

def merge_csv_folder(folder="data_meteo_station", output_file="merged_data.csv"):
    """
    Merge tous les fichiers CSV présents dans 'folder' en un seul CSV.
    
    Args:
        folder (str): Dossier contenant les fichiers CSV.
        output_file (str): Nom du fichier CSV final.

    Returns:
        pd.DataFrame: DataFrame fusionné.
    """
    # Cherche tous les CSV dans le dossier
    csv_files = glob.glob(os.path.join(folder, "*.csv"))
    
    if not csv_files:
        print("[!] Aucun fichier CSV trouvé.")
        return None
    
    print(f"[*] {len(csv_files)} fichiers trouvés dans {folder}. Fusion en cours...")

    # Lire et concaténer
    df_list = []
    for file in csv_files:
        try:
            df = pd.read_csv(file, sep=",", encoding="utf-8-sig")
            df_list.append(df)
        except Exception as e:
            print(f"[!] Erreur avec {file}: {e}")

    df_merged = pd.concat(df_list, ignore_index=True)

    # Sauvegarde en un seul CSV
    output_path = os.path.join(output_file)
    df_merged.to_csv(output_path, index=False, sep=";", encoding="utf-8-sig")

    print(f"[+] Fichier fusionné sauvegardé sous: {output_path}")
    print(f"[+] Total lignes: {len(df_merged)}")

    return df_merged

if __name__ == "__main__":
    df_final = merge_csv_folder("data_meteo_station/data_formated", "current_df_meteostation.csv")