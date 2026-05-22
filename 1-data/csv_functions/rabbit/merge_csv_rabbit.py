import camelot
import pandas as pd
import numpy as np
import os
import csv



def main_csv_rabbit(type_extract, debug):
    # type_extract : "app" or "computer
    # debug: "True" or "False"
    
    if type_extract == "app" or "computer":
        csv_rabbit(type_extract,debug)
        print(f"Data extracted from the {type_extract} was formated into CSV")
    else:
        print("No correct type extraction was given")


def read_data(file, debug=False) -> pd.DataFrame:
    print("*******************")
    if debug:
        print(f"Reading file: {file}")

    ext = os.path.splitext(file)[1].lower()
    print("extension:",ext)
    if ext != ".csv":
        raise ValueError(f"Please convert the file {file} to '.csv'")

    # Lire toutes les lignes
    with open(file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Détecter le séparateur sur la première ligne
    first_line = lines[0].strip()
    sep = ";" if ";" in first_line else ","

    # Vérifier si le dernier séparateur est présent
    if not first_line.endswith(sep):
        lines[0] = first_line + sep 
        if debug:
            print("Header corrected (missing separator added).")

    # Écrire temporairement et lire avec pandas
    temp_file = file.replace(".csv", "_fixed.csv")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.writelines(lines)

    df = pd.read_csv(temp_file, sep=sep, thousands = " ")
    return df


def test_file_name(file_name,debug):
    if debug:
        print("test_file_name")
    
    if file_name.lower() == "umidità":
        legend = "umidity"
    elif file_name.lower() == "temperatura":
        legend = "temperature"
    elif file_name.lower() == "ammoniaca":
        legend = "NH3"
    elif file_name.lower() == "anidride carbonica":
        legend = "CO2"
    elif file_name.lower() == "acido solfidrico":
        legend = "H2S"
    elif file_name.lower() == "pm 1.0":
        legend = "PM_1_0"
    elif file_name.lower() == "pm 2.5":
        legend = "PM_2_5"
    elif file_name.lower() == "pm 4.0":
        legend = "PM_4_0"
    elif file_name.lower() == "pm 10":
        legend = "PM_10"
    else:
        print(f"⚠️ Name unknown: {file_name.lower()}, file ignored")
        return None
    
    return legend
        


def extract_df_rabbit_computer(df, legend, debug=False):
    """
    df : DataFrame lu depuis CSV computer
    legend : nom de la variable (CO2, NH3, etc.)
    """
    if debug:
        print(f"extract_df_rabbit_computer for {legend}")
    

    # Transformation en format long : id_rabbit et value
    df_long = df.melt(
        id_vars=["Timestamp", "Entity Name"], 
        value_vars=[c for c in df.columns if str(c) in ["1", "2", "3", "4", "5","6"]],
        var_name="id_rabbit",
        value_name=legend
    )
    

    # Convertir Timestamp en datetime

    
    df_long["datetime"] = pd.to_datetime(df_long["Timestamp"], errors="coerce",dayfirst=True)
    df_long["date"] = df_long["datetime"].dt.date
    df_long["hour"] = df_long["datetime"].dt.time
    df_long["datetime"] = df_long["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
    
    # id_rabbit à partir de colonne melt
    df_long["id_rabbit"] = df_long["id_rabbit"].astype(str)

    # Supprimer lignes sans datetime
    #df_long = df_long.dropna(subset=["datetime"])

    
    # Garder uniquement les colonnes importantes
    return df_long[["datetime", "date", "hour", "id_rabbit", legend]]


def extract_df_rabbit_app(df, debug=False):
    """
    Prépare un fichier CSV exporté depuis l'app pour fusion.
    Ne gère que :
    - renommage des colonnes pour correspondre à NH3/CO2/etc.
    - conversion datetime + création des colonnes date et hour
    - id_rabbit en str
    Tout le reste (NaN, fusion, conversion numérique, groupby) est fait dans csv_rabbit.
    """
    if debug:
        print("Processing app CSV")

    # Colonnes intéressantes de l'app et leur mapping vers le standard
    col_map = {
        "node_id": "id_rabbit",
        "timestamp": "datetime",
        "h2s_ppm": "H2S",
        "nh3_ppm": "NH3",
        "co2_ppm": "CO2",
        "pm_1_0_ppm": "PM_1_0",
        "pm_2_5_ppm": "PM_2_5",
        "pm_4_0_ppm": "PM_4_0",
        "pm_10_ppm": "PM_10",
        "indoor_humidity": "umidity",
        "indoor_db_temperature": "temperature"
    }

    # Ne garder que les colonnes présentes
    df = df[[c for c in col_map.keys() if c in df.columns]].copy()

    # Renommer pour correspondre aux noms standard
    df.rename(columns={k: v for k, v in col_map.items() if k in df.columns}, inplace=True)

    # Conversion datetime et création date/hour
    if "datetime" in df.columns:
        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce",unit='s')
        df["date"] = df["datetime"].dt.date
        df["hour"] = df["datetime"].dt.time

    # id_rabbit en str
    if "id_rabbit" in df.columns:
        df["id_rabbit"] = df["id_rabbit"].astype(str)

    # Colonnes utiles
    useful_cols = ["datetime", "date", "hour", "id_rabbit"]
    for col in ["NH3", "CO2", "H2S", "PM_1_0", "PM_2_5", "PM_4_0", "PM_10", "temperature", "umidity"]:
        if col in df.columns:
            useful_cols.append(col)

    return df[useful_cols]

        
        
        
        
        
        
def csv_rabbit(type_extract, debug=False):
    if debug:
        print("csv_rabbit")
    
    rabbit_files = [f for f in os.listdir() if f.lower().endswith(".csv")] 
    dfs = []
    
    gas_measure = ["NH3","CO2","H2S","PM_1_0","PM_2_5","PM_4_0","PM_10"]
    
    for file in rabbit_files:
        file_name, ext = os.path.splitext(file)
        df_file = read_data(file, debug)
        if type_extract == "computer":
            legend = test_file_name(file_name, debug)
            if legend is None:
                continue
            df_file = extract_df_rabbit_computer(df_file, legend, debug)
        elif type_extract == "app":
            df_file = extract_df_rabbit_app(df_file, debug)
        dfs.append(df_file)
        
    if not dfs:
          raise ValueError("No list of dataframe was found")
          return None

    # Merge all the dataframes
   
    df_all = pd.concat(dfs, ignore_index=True)
    
    expected_cols = ["NH3", "CO2", "H2S", "PM_1_0", "PM_2_5", "PM_4_0", "PM_10", "temperature", "umidity"]
    measures_in_df = [c for c in expected_cols if c in df_all.columns]
    df_all = df_all.dropna(subset=measures_in_df, how="all")
    
    for col in gas_measure:
        if col not in df_all.columns:
            df_all[col] = pd.NA
    
    # Group by date/id/hour
    df_grouped = df_all.groupby(["date", "id_rabbit", "hour"], as_index=False).agg({
        "datetime": "first",
        "date": "first",
        "hour": "first",
        "NH3": "first",
        "CO2": "first",
        "H2S": "first",
        "PM_1_0": "first",
        "PM_2_5": "first",
        "PM_4_0": "first",
        "PM_10": "first",
        "temperature": "first",
        "umidity": "first"
    })
    
    numeric_cols = ["NH3", "CO2", "H2S", "PM_1_0", "PM_2_5", "PM_4_0", "PM_10", "temperature", "umidity"]
    for col in numeric_cols:
        if col in df_grouped.columns:
            df_grouped[col] = df_grouped[col].astype(str).str.replace(",", ".", regex=False)
            df_grouped[col] = pd.to_numeric(df_grouped[col], errors="coerce")
    # Conversion en float (tout ce qui n’est pas convertible devient NaN)
    #df_grouped[numeric_cols] = df_grouped[numeric_cols].apply(pd.to_numeric, errors="coerce")
    
    df_grouped.to_csv("merged_rabbit.csv", index=False, encoding="utf-8", sep =";")
    return df_grouped
    # # Ne garder que si gaz (ou gaz+climat)
    # mask_has_gas = df_grouped[["NH3", "CO2"]].notna().any(axis=1)
    # df_grouped = df_grouped[mask_has_gas]
    # #Force to go to float all the value
    # df_grouped[["NH3", "CO2", "temperature", "umidity"]] = df_grouped[["NH3", "CO2", "temperature", "umidity"]].apply(pd.to_numeric, errors="coerce")
    
    # return df_grouped























