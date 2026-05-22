# -*- coding: utf-8 -*-
"""
Created on Thu Sep 11 13:14:17 2025

@author: titou
"""
import numpy as np
import datetime
import os
import csv
import pandas as pd


def read_data(debug):
    if debug:
        print("read_data")
    
    rabbit_path =  "thi.xlsx"
    
    if os.path.exists(rabbit_path):
        try:            
            df_rabbit = pd.read_excel(rabbit_path, header = 0, sheet_name = ["thi"])
            #df_rabbit = pd.read_csv(rabbit_path,header =0, sep=";")
            
                    #df = pd.merge(df_innova, df_rabbit, on="numero", how="left")  
                    
                    #dfs.append(df)
        except Exception as e:
            print(f"Erreur lors du chargement d'un des dossiers : {e}")
    
    print(df_rabbit)
    
    return df_rabbit #pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()





def formatage_RABBIT(df, debug=False):
    if debug:
        print("formatage_rabbit")

    dfs = []

    for sheet_name, dic in df.items():
        # Définition de la mesure
        if sheet_name == "Umidity":
            legend = "umidity"
        elif sheet_name == "Temperatura":
            legend = "temperature"
        elif sheet_name == "Ammoniaca":
            legend = "NH3"
        elif sheet_name == "Anidride carbonica":
            legend = "CO2"
        elif sheet_name == "PM 2.5":
            legend = "PM_2_5"
        elif sheet_name == "thi":
            legend = "THI"
        else:
            if debug:
                print(f"⚠️ Onglet ignoré: {sheet_name}")
            continue

        # Colonnes identifiant
        id_vars = ["Timestamp"]
       
        # Transformation en format long
        df_long = dic.melt(
            id_vars=id_vars,
            value_vars=[c for c in dic.columns if c in [1, 2, 3, 4, 5, 6]],
            var_name="id_rabbit",
            value_name=legend
        )

        # Conversion date
        df_long["date"] = pd.to_datetime(df_long["Timestamp"], errors="coerce").dt.date
        df_long["hour"] = pd.to_datetime(df_long["Timestamp"], errors="coerce").dt.time
        
        

        # Supprimer les lignes sans date OU sans heure
        df_long = df_long.dropna(subset=["date", "hour"])

        # Créer datetime
        df_long["datetime"] = pd.to_datetime(
            df_long["date"].astype(str) + " " + df_long["hour"].astype(str),
            errors="coerce"
        )

        dfs.append(df_long[["id_rabbit", "date", "hour", "datetime", legend]])

    if not dfs:
        return pd.DataFrame(columns=["date", "hour", "id_rabbit", "NH3", "CO2","PM_2_5", "temperature", "humidity"])

    # Fusionner tous les onglets
    df_all = pd.concat(dfs, ignore_index=True)
    
    # Regrouper par date/id/heure
    df_grouped = df_all.groupby(["date", "id_rabbit", "hour"], as_index=False).agg({
        "datetime": "first",
        "THI": "first"
    })

    # Ne garder que si gaz (ou gaz+climat)
    df_grouped["THI"] = df_grouped["THI"].str.replace(",", ".", regex=False)
    mask_has_gas = df_grouped[["THI"]].notna().any(axis=1)
    df_grouped = df_grouped[mask_has_gas]
    
    #Force to go to float all the value
    df_grouped[["THI"]] = df_grouped[["THI"]].apply(pd.to_numeric, errors="coerce")
    
    return df_grouped




def write_csv(df,file_name):
    
    df.to_csv(file_name, index=False,sep=";")


def main_dataframe(debug):
    if debug:
        print("MAIN_DATAFRAME")
        

    df_rabbit = read_data(debug)
    df_rabbit = formatage_RABBIT(df_rabbit, debug)
    write_csv(df_rabbit,"thi_formated.csv")
    
    #Timescale
    #ecrire new data
    
    return df_rabbit











