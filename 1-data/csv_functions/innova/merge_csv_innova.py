import camelot
import pandas as pd
import numpy as np
import os



def fuse_triplets(df, time_col, max_interval_min):
    """
    Fusionne les lignes par bloc de 3 mesures successives :
    - moyenne sur colonnes numériques
    - garde les colonnes non numériques depuis la 1ère ligne
    - si le bloc dépasse l'intervalle max (en minutes), on garde la première ligne
    - si moins de 3 lignes à la fin, elles sont conservées telles quelles
    """
    df = df.copy()
    
    # S'assurer que la colonne datetime est bien au format datetime
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]
    print("numeric cols", numeric_cols)
    print ("non numeric cols",non_numeric_cols)

    fused_rows = []
    i = 0
    df = df.sort_values(time_col).reset_index(drop=True)
    while i < len(df):
        block = df.iloc[i:i+3]
        
        # Cas: moins de 3 lignes restantes → garder telles quelles
        if len(block) < 3:
            for j in range(len(block)):
                fused_rows.append(block.iloc[j].copy())  # garantir Series
            break

        # Vérifier les intervalles de temps
        times = block[time_col]
        intervals = (times - times.iloc[0]).dt.total_seconds() / 60  # minutes
        if intervals.max() <= max_interval_min:
            # Fusionner
            fused_numeric = block[numeric_cols].iloc[1:].mean()  # average on only the 2 last points of the block of 3 by protocol

            fused_non_numeric = {}
            
            if "datetime" in block.columns:
                print("DATETIME")
                dt_mean = (block["datetime"].iloc[1:]).astype("int64").mean()  # moyenne en ns depuis 1970 # average on only the 2 last points of the block of 3 by protocol
                #print("dt_mean format ns 1970",dt_mean)
                print(dt_mean)
                dt_mean = pd.to_datetime(dt_mean, unit="ns").round("s")
                print(dt_mean)
                #print("dt_mean format normal",dt_mean)
                fused_non_numeric["datetime"] = dt_mean
                fused_non_numeric["date"] = dt_mean.date()
                fused_non_numeric["hour"] = dt_mean.time()
            
            fused_row = pd.concat([pd.Series(fused_non_numeric), fused_numeric])
            fused_rows.append(fused_row)
            i += 3
        else:
            # Bloc non valide → prendre la première ligne seulement
            fused_rows.append(block.iloc[0].copy())
            i += 1

    df_fused = pd.DataFrame(fused_rows).reset_index(drop=True)
    return df_fused


def read_pdf_camelot(SL_list, date = "15092025_24092025"):
    pdf_path_first = f"{date}_SL{SL_list[0]}.pdf"   #f"data/{date}/{date}_SL{SL_list[0]}.pdf"
    tables_first = camelot.read_pdf(pdf_path_first, pages="1", flavor="lattice")
    monitor_setup = tables_first[0].df
    monitor_output = "Monitor Setup.csv" #f"data/{date}/Monitor Setup.csv"
    monitor_setup.to_csv(monitor_output, index=False, encoding="utf-8-sig")
    print("Monitor Setup CSV généré !")
      
    all_SL_dfs = []
    
    # -------------------------------
    # Boucle sur les SL
    # -------------------------------
    for SL in SL_list:
        pdf_path = f"{date}_SL{SL}.pdf"  #f"data/{date}/{date}_SL{SL}.pdf"
        tables = camelot.read_pdf(pdf_path, pages="all", flavor="lattice")
        print(f"Camelot reading of SL{SL} completed")
        tables = tables[1:]  # Ignorer le premier tableau
    
        df_list = []
        header = tables[0].df.iloc[0].copy()
        #header = header.str.replace(r"\[(.*?)\]", r"(\1)", regex=True)
    
        for t in tables:
            df = t.df.copy()
            df = df[~(df == header).all(axis=1)]
            df_list.append(df)
    
        df_final = pd.concat(df_list, ignore_index=True)
        df_final.columns = header
        df_final.to_csv(f"Channel_{SL}_Measurement_Data.csv", sep =";", index=False, encoding="utf-8-sig")

def formatting_csv(SL_list) :   
    all_SL_dfs = []
    for SL in SL_list:    
    # Renommer colonne "Date Time" en "Date & Time"
        filename = f"Channel_{SL}_Measurement_Data.csv"
        df = pd.read_csv(filename,sep = ";")
        if "Date Time" in df.columns or "Date & Time" in df.columns:
            continue
        else:
            df = pd.read_csv(filename,sep = ";",header = 1)
            
        if "Date Time" in df.columns or "Date & Time" in df.columns:
            df.rename(columns={"Date Time": "datetime"}, inplace=True)
            df.rename(columns={"Date & Time": "datetime"}, inplace=True)
            
        # Ajouter colonnes Date et Heure
        if "datetime" in df.columns:
            df["datetime"] = pd.to_datetime(df["datetime"], errors='coerce', dayfirst = True)
            df["date"] = df["datetime"].dt.date
            df["hour"] = df["datetime"].dt.time
            df["datetime"] = df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
            print(df["datetime"])
            
        if "A: Carbon dioxide\n[ppm]" in df.columns or "A: Carbon dioxide(ppm)" in df.columns :
            df.rename(columns={"A: Carbon dioxide(ppm)": "CO2"}, inplace=True)
            df.rename(columns={"A: Carbon dioxide\n[ppm]": "CO2"}, inplace=True)
        if "C: Ammonia\n[ppm]" in df.columns or "C: Ammonia(ppm)":
            df.rename(columns={"C: Ammonia(ppm)": "NH3"}, inplace=True)
            df.rename(columns={"C: Ammonia\n[ppm]": "NH3"}, inplace=True)
        if "D: Methane\n[ppm]" in df.columns or "D: Methane(ppm)":
            df.rename(columns={"D: Methane(ppm)": "CH4"}, inplace=True)
            df.rename(columns={"D: Methane\n[ppm]": "CH4"}, inplace=True)
        
        df["id_channel"]= SL
        # Conversion explicite des colonnes pseudo-numériques
        
        columns_str = [c for c in df.columns if c not in ["datetime", "date", "hour"]]
        print("column str", columns_str)
        for c in columns_str:
            df[c] = pd.to_numeric(df[c].astype(str).str.replace(",", ".").str.strip(), errors="coerce")
        # -------------------------------
        # Fusion des triplets (médiane)
        # -------------------------------
        df = fuse_triplets(df, time_col="datetime", max_interval_min=3)
        df["id_channel"] = df['id_channel'].astype(int)
        print(f"Completion of fuse_triplets for SL{SL}")
        # Selection of the interesting features
        useful_cols = ["datetime", "date","hour","CO2","NH3","CH4","id_channel"]
        df = df[useful_cols]
        
        # -------------------------------
        # Sauvegarde CSV individuelle
        output_csv = f"Channel_{SL}_Measurement_Data_formatted.csv"
        df.to_csv(output_csv, index=False, encoding="utf-8-sig", sep =";")
        print(f"CSV SL {SL} généré avec fusion des triplets !")
        
        all_SL_dfs.append(df)
    # -------------------------------
    # Merge de toutes les SL
    # -------------------------------
    if all_SL_dfs:
        df_merged = pd.concat(all_SL_dfs, ignore_index=True)
        df_merged = df_merged.sort_values(["date", "id_channel", "hour"]).reset_index(drop=True)
        df_merged.to_csv("merged_innova.csv", index=False, encoding="utf-8-sig",sep=";")
        print("Merge final de toutes les SL généré : merged_innova.csv")
        return df_merged
    else:
        print("Aucun SL à merger")
        return pd.DataFrame(columns=useful_cols)
    



def main_merge_csv_innova_2(date,SL_list):
    read_pdf_camelot(SL_list,date)
    formatting_csv(SL_list)





    




date = "15092025_24092025"
SL_list = [5,10,11]