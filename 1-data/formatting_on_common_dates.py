# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 09:23:17 2025

@author: titou
"""

import numpy as np
import datetime
import os
import csv
import pandas as pd
import shutil


def read_data(debug):
    if debug:
        print("read_data")
    
    
    innova_path = "data_innova/current_df_innova.csv"
    rabbit_path = "data_rabbit/current_df_rabbit.csv"
    meteo_station_path = "data_meteo_station/current_df_meteostation.csv"
    envea_path = "data_envea/current_df_envea.csv"
    
    
    df_meteo_station = None
    df_envea = None
    
    if os.path.exists(innova_path) and os.path.exists(rabbit_path):
        try:
            df_innova = pd.read_csv(innova_path, sep=";")
            df_rabbit = pd.read_csv(rabbit_path, sep=";")
                   
        except Exception as e:
            raise ValueError(f"Error while loading RABBIT or INNOVA dataframe: {e}")
    
    if os.path.exists(meteo_station_path):
        try:
            df_meteo_station = pd.read_csv(meteo_station_path, sep=";")
        except Exception as e:
            print(f"Error while loading the METEO STATION dataframe: {e}")
    
    if os.path.exists(envea_path):
        try:
            df_envea = pd.read_csv(envea_path, sep=";")
        except Exception as e:
            print(f"Error while loading the ENVEA dataframe: {e}")
            
        
    
    return df_innova, df_rabbit, df_meteo_station, df_envea #pd.concat(dfs, ignore_index=True) if dfs else pd.DataFrame()


def formating_common_dates(df_R, df_I, df_MS,df_E, debug=False):
    """
    Garde uniquement les lignes des dataframes ou df_R et df_I ont une date commune.
    
    Paramètres
    ----------
    df_R : pd.DataFrame
        DataFrame formaté Rabbit (doit contenir une colonne 'date')
    df_I : pd.DataFrame
        DataFrame formaté Innova (doit contenir une colonne 'date')
    df_MS : pd.DataFrame
        DataFrame formaté meteo_station (doit contenir une colonne 'date')
    df_E : pd.DataFrame
        DataFrame formaté Envea (doit contenir une colonne 'date')
    debug : bool, optionnel
        Affiche les infos intermédiaires si True

    Retour
    ------
    df_R_filtre, df_I_filtre : pd.DataFrame, pd.DataFrame
        Deux DataFrames réduits aux dates communes
    """
    
    if df_I is not None and df_R is not None:
        dates_R = set(df_R["date"].unique())
        dates_I = set(df_I["date"].unique())
    else:
        raise ValueError("Dataframe rabbit or dataframe innova is empty")
    # Intersection
    dates_communes = dates_R & dates_I
    
    if debug:
        print(f"Dates Rabbit : {len(dates_R)}")
        print(f"Dates Innova : {len(dates_I)}")
        print(f"Dates communes : {len(dates_communes)}")
    
    # Filtrage
    df_R_filtre = df_R[df_R["date"].isin(dates_communes)].copy()
    df_I_filtre = df_I[df_I["date"].isin(dates_communes)].copy()
    if df_E is not None:
        df_E_filtre = df_E[df_E["date"].isin(dates_communes)].copy()
    else:
        df_E_filtre = None
    if df_MS is not None:
        df_MS_filtre = df_MS[df_MS["date"].isin(dates_communes)].copy()
    else:
        df_MS_filtre = None
    
    return df_R_filtre, df_I_filtre, df_MS_filtre, df_E_filtre



def write_csv(df,output_dir,file_name):
    #Create file if it doesnt exist
    os.makedirs(output_dir, exist_ok=True)  

    output_file = os.path.join(output_dir, file_name)

    # Save
    if df is not None:
        df.to_csv(output_file, index=False)
    return

def main_dataframe(debug):
    if debug:
        print("MAIN_DATAFRAME")
    
    df_innova, df_rabbit, df_meteo_station,df_envea = read_data(debug)
    df_rabbit, df_innova, df_meteo_station, df_envea = formating_common_dates(df_rabbit, df_innova,df_meteo_station,df_envea, debug)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Répertoires absolus
    base_dir = "data_common_dates"
    backup_dir = os.path.join(base_dir, "backup_files", timestamp)

    # Création du dossier de backup
    os.makedirs(backup_dir, exist_ok=True)

    if debug:
        print(f"Répertoire courant : {base_dir}")
        print(f"Sauvegarde dans : {backup_dir}")

    # Déplacement des CSV existants vers le dossier backup
    moved_files = 0
    for file in os.listdir(base_dir):
        if file.endswith(".csv"):
            src = os.path.join(base_dir, file)
            dst = os.path.join(backup_dir, file)
            shutil.move(src, dst)
            moved_files += 1
            if debug:
                print(f"Déplacé : {src} → {dst}")

    if debug and moved_files == 0:
        print("Aucun fichier CSV à déplacer.")
    
    
    df_rabbit.to_csv("data_common_dates/current_df_rabbit_CD.csv",sep=";", index=False)
    df_innova.to_csv("data_common_dates/current_df_innova_CD.csv",sep=";", index=False)
    df_meteo_station.to_csv("data_common_dates/current_df_meteo_station_CD.csv",sep=";", index=False)
    #df_envea.to_csv("data_common_dates/current_df_envea_CD.csv",sep=";")
    
    # write_csv(df_rabbit,"data_common_dates","current_df_rabbit_CD.csv",sep=";")
    # write_csv(df_innova,"data_common_dates","current_df_innova_CD.csv")
    # write_csv(df_meteo_station,"data_common_dates","current_df_meteostation_CD.csv")
    # write_csv(df_envea,"data_common_dates","current_df_envea_CD.csv")
    
    #Timescale
    #ecrire new data
    
    return 