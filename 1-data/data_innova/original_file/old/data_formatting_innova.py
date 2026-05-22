# -*- coding: utf-8 -*-
"""
Created on Thu Sep 11 13:14:17 2025

@author: titou
"""

import os
import csv
import pandas as pd


def read_data(debug):
    if debug:
        print("read_data")
    
    
    innova_path =  "INNOVA.xlsx"
        
    if os.path.exists(innova_path):
        try:
            xls_innova = pd.ExcelFile(innova_path)
            sheets_data_innova = xls_innova.sheet_names[1:]  # toutes sauf la première
            df_innova = pd.read_excel(innova_path, header =1, sheet_name = sheets_data_innova)
            
            
        except Exception as e:
            print(f"Erreur lors du chargement d'un des dossiers : {e}")
    
    return df_innova





def formatage_INNOVA(df, debug):
    if debug:
        print("formatage_INNOVA")
        
    dfs = []
    for sheet_name, dic in df.items():
        # Creation of an id_channel
        id_channel = int(sheet_name.split()[1])
        dic["id_channel"] = id_channel
        # print("*****************")
        # print(dic.columns)
        
        # Uniformisation of the Date format
        if "Date & Time" in dic.columns:
            dic.rename(columns={"Date & Time": "Date"}, inplace=True)
        if "Date" in dic.columns:
            dic["Date"] = pd.to_datetime(dic["Date"]).dt.date

        # Rename of the main columns
        dic.rename(columns={"Date": "date",
                            "ORA": "hour",
                            "A: Carbon dioxide(ppm)": "CO2",
                            "C: Ammonia(ppm)": "NH3",
                            "D: Methane(ppm)":"CH4"},
                   inplace=True)
        
        # Supress all the lines where we don't have the date or the hour
        dic = dic.dropna(subset=["date", "hour"]).copy()
        dic["datetime"] = pd.to_datetime(dic["date"].astype(str) + " " + dic["hour"].astype(str))
        # If we miss date or hour: we don't add the line
        
        # Ajouter CH4 si elle est absente
        if "CH4" not in dic.columns:
            dic["CH4"] = pd.NA
            
        # Selection of the items we're gonna use
        df_ = dic[["datetime", "date","hour", "CO2", "NH3","CH4", "id_channel"]]
        
        dfs.append(df_)
    
    
    if dfs:
        df_I_grouped = pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame(columns=["date","hour","CO2","NH3","id_channel"])
    
    df_I_grouped = df_I_grouped.sort_values(["date", "id_channel", "hour"]).reset_index(drop=True)
    
    return df_I_grouped





def write_csv(df,file_name):
    #Create file if it doesnt exist

    # Save
    df.to_csv(file_name, index=False)


def main_dataframe(debug):
    if debug:
        print("MAIN_DATAFRAME")
        
  
    df_innova = read_data(debug)
    df_innova = formatage_INNOVA(df_innova ,debug)
    write_csv(df_innova,"innova_formated.csv")
    
    #Timescale
    #ecrire new data
    
    return 











