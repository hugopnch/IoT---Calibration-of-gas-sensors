# -*- coding: utf-8 -*-
"""
Created on Fri Jan  9 15:04:54 2026

@author: titou
"""
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta, date
import os
import json
#%%Importation and pre-processing of data


def assign_campaign(dt):
    if pd.Timestamp("2025-03-31") <= dt <= pd.Timestamp("2025-05-12"):
        return "2025_Apr"
    if pd.Timestamp("2025-06-12") <= dt <= pd.Timestamp("2025-06-25"):
        return "2025_Jun"
    elif pd.Timestamp("2025-09-11") <= dt <= pd.Timestamp("2025-09-25"):
        return "2025_Sep"
    elif pd.Timestamp("2026-01-14") <= dt <= pd.Timestamp("2026-01-22"):
        return "2026_Gen" #"2026_Gen"
    else:
        return "other"
    



def assign_campaign_iCO2(dt):
    if pd.Timestamp("2025-03-31") <= dt <= pd.Timestamp("2025-04-16"):
        return "2025_Apr_1"
    if pd.Timestamp("2025-04-16") <= dt <= pd.Timestamp("2025-05-12"):
        return "2025_Apr_2"
    if pd.Timestamp("2025-06-12") <= dt <= pd.Timestamp("2025-06-25"):
        return "2025_Jun"
    elif pd.Timestamp("2025-09-11") <= dt <= pd.Timestamp("2025-09-25"):
        return "2025_Sep"
    elif pd.Timestamp("2026-01-14") <= dt <= pd.Timestamp("2026-01-22"):
        return "2026_Gen"
    else:
        return "other"



def assign_humidity(row):
    hum = row["umidity"]
    if hum <=65:
        return 0
    elif hum <=75:
        return 1
    elif hum<=100:
        return 2
    else:
        return None




def assign_innova_point(row):
    camp = row["campaign"]
    rid = row["id_rabbit"]
    
    # if camp == "2025_Jun":
    #     mapping = {2: "sl11", 4: "sl5", 6: "sl4", 1: "sl3", 5: "no"}
    # elif camp == "2025_Sep":
    #     mapping = {2: "sl11", 4: "sl5", 3: "sl4", 6: "sl3", 5: "no"}
    
    if camp == "2025_Apr":
        #mapping = {1: "no", 2: "no", 4: "no", 6: "sl5"}
        mapping = {1: "no", 2: "sl5", 4: "no", 6: "sl5"}
        #mapping = {1: "no", 2: "no", 4: "no", 6: "no"}
    elif camp == "2025_Jun":
        #mapping = {2: "sl11", 4: "sl5", 1: "sl3", 6: "sl4", 5: "no"}
        mapping = {2: "sl11", 4: "no", 1: "sl4", 6: "sl3", 5: "no"}
    elif camp == "2025_Sep":
        #mapping = {2: "sl11", 4: "sl5", 6: "sl3", 3: "sl4", 5: "no"}
        mapping = {2: "sl11", 4: "no", 6: "sl3", 3: "sl4", 5: "no"}
    elif camp == "2026_Gen":
        #mapping = {1: "no", 4: "no", 5: "sl11", 6: "no"}
        mapping = {1: "sl11", 4: "no", 5: "sl11", 6: "sl11"}
        #mapping = {1: "no", 4: "no", 5: "no", 6: "no"}
    else:
        mapping = {}

    return mapping.get(rid, "no")

def assign_innova_point_iCO2(row):
    camp = row["campaign"]
    rid = row["id_rabbit"]
    
    if camp == "2025_Apr_1":
        #mapping = {1: "no", 2: "no", 4: "no", 6: "no"}
        mapping = {1: "no", 2: "sl5", 4: "sl11", 6: "sl5"}
    elif camp == "2025_Apr_2":
        mapping = {1: "no", 2: "no", 4: "no", 6: "no"}
    elif camp == "2025_Jun":
        mapping = {2: "sl11", 4: "sl5", 1: "no", 6: "sl3", 5: "no"}
    elif camp == "2025_Sep":
        mapping = {2: "sl11", 4: "sl5", 6: "sl4", 3: "sl3", 5: "no"}
    elif camp == "2026_Gen":
        #mapping = {1: "no", 4: "no", 5: "sl11", 6: "no"}
        mapping = {1: "no", 4: "no", 5: "sl11", 6: "sl11"}
    else:
        mapping = {}

    return mapping.get(rid, "no")




def e_time_period(dt):
    if pd.Timestamp("2025-03-13") <= dt <= pd.Timestamp("2025-04-19"):
        return "ALL_per"#"2025_MarApr"
    elif pd.Timestamp("2025-04-30") <= dt <= pd.Timestamp("2025-05-12"):
        return "ALL_per" #"2025_May"
    else:
        return "other"

def import_data_IR():
    if target_col[0] == "i_NH3":
        file_path = "csv_decomposed/innova/df_signal_decomposition_NH3_ALL.csv"
        #file_path = "csv/innova/switched/df_signal_decomposition_10_50_200.csv"
    elif target_col[0] == "i_CO2":
        file_path = "csv_decomposed/innova/df_signal_decomposition_CO2_current.csv"
    else:
        raise ValueError("Target is not supported")
       
    df = pd.read_csv(file_path, sep=";")
    df["datetime"] = pd.to_datetime(df["datetime"])
    df.sort_values("datetime").reset_index(drop=True)
    
    if target_col[0] == "i_NH3":
        df["campaign"] = df["datetime"].apply(assign_campaign)
        df = df[df["campaign"] != "other"].copy()
        df["innova_point"] = df.apply(assign_innova_point, axis=1)
        df = df[df["innova_point"] != "no"].copy()
        with open("csv_decomposed/innova/features_decomposition_list_NH3_ALL.json", "r") as f:
        #with open("csv/innova/switched/features_decomposition_list_10_50_200.json", "r")as f:
            dict_features = json.load(f)
    elif target_col[0] == "i_CO2":
        df["campaign"] = df["datetime"].apply(assign_campaign_iCO2)
        df = df[df["campaign"] != "other"].copy()
        df["innova_point"] = df.apply(assign_innova_point_iCO2, axis=1)
        df = df[df["innova_point"] != "no"].copy()
        with open("csv/innova/features_decomposition_CO2_list.json", "r") as f:
            dict_features = json.load(f)
    else:
        raise ValueError("The target col do not match any existing function")
        
 
        
    return df,dict_features

def import_data_ER():
    file_path = "csv_decomposed/envea/df_signal_decomposition_PM2.5_ALL.csv"
    #file_path = "csv/envea/df_signal_decomposition_current.csv"
    df = pd.read_csv(file_path, sep=";")
    
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["campaign"] = df["datetime"].apply(e_time_period)
    df.sort_values("datetime").reset_index(drop=True)
    
    with open("csv_decomposed/envea/features_decomposition_list_PM2.5_ALL.json", "r") as f:
    #with open("csv/envea/features_decomposition_list.json", "r") as f:
        dict_features = json.load(f)
    
    return df, dict_features



def apply_models_by_colonne(df,model_col1,model_col2,features,gas="NH3",colonne_col="colonne"):
    """
    Applique model_col1 si colonne == 1
    Applique model_col2 si colonne == 2
    Stocke le résultat dans r_{gas}_corrected_colonne
    """

    df = df.copy()
    output_col = f"{gas}_corrected_colonne"

    df[output_col] = np.nan

    # ------------------------
    # Colonne 1
    # ------------------------
    mask1 = df[colonne_col] == 1
    if mask1.any():
        X1 = df.loc[mask1, features]
        df.loc[mask1, output_col] = model_col1.predict(X1)

    # ------------------------
    # Colonne 2
    # ------------------------
    mask2 = df[colonne_col] == 2
    if mask2.any():
        X2 = df.loc[mask2, features]
        df.loc[mask2, output_col] = model_col2.predict(X2)

    return df



#%% Plot data each model (same file)


def plot_models(
    df,
    gas="NH3",
    engineered_cols = [],
    model_path="learning_JuneSeptember_campaign/hyperparameters_search",
    models=None,
    use_grouping=False,
    name_grouping="colonne",
    min_samples=80,
    export_csv=True,
):
    target_col = f"i_{gas}"
    r_col = f"r_{gas}"
    rabbit_cols = ["r_NH3", "r_temperature", "r_umidity", "r_THI", "r_CO2"]
    id_cols = ["id_rabbit", "id_channel"]
    base_model_path = "learning_JuneSeptember_campaign/hyperparameters_search_base"
    # Filtrage identique à ton code
    df_use = df[df["innova_point"] != "no"].copy()

    if use_grouping:
        iterable = df_use.groupby(name_grouping)
    else:
        iterable = [("ALL", df_use)]

    if models is None:
        raise ValueError("Tu dois fournir la liste des modèles à tester")

    for model in models:
        for group, df_sub in iterable:
            if not all(c in df_sub.columns for c in id_cols):
                print(f"id_rabbit ou id_channel absent pour le groupe {group}")
                continue
            
            for (id_rabbit, id_channel), df_rc in df_sub.groupby(id_cols):
                if len(df_rc) < min_samples:
                    continue
    
                if target_col not in df_rc.columns or r_col not in df_rc.columns:
                    continue
    
                # Chargement du modèle
                skeleton = f"best_model_{gas}_{model}_{group}.joblib"
                model_file = os.path.join(model_path, skeleton)
                base_file = os.path.join(base_model_path, skeleton)
                if not os.path.exists(model_file):
                    print(f"Modèle absent : {model_file}")
                    continue
    
                reg = joblib.load(model_file)
                reg_base = joblib.load(base_file)
                
                # Sélection des features
                features = [c for c in rabbit_cols+engineered_cols  if c in df_rc.columns]
                
                
                if not features:
                    continue
    
                X = df_rc[features].values
                X_base = df_rc[rabbit_cols].values
                y_true = df_rc[target_col].values
                r_raw = df_rc[r_col].values
    
                mask = np.isfinite(X).all(axis=1) & np.isfinite(y_true)
                X = X[mask]
                X_base = X_base[mask]
                y_true = y_true[mask]
                r_raw = r_raw[mask]
                datetime = df_rc[mask]["datetime"]
                idx = df_rc.index[mask]
    
                if len(X) < min_samples:
                    continue
    
                # Prédiction
                y_pred = reg.predict(X)
                y_pred_base = reg_base.predict(X_base)
                # ---------- EXPORT CSV ----------
                if export_csv:
                    df_out = pd.DataFrame(
                        {
                            "i_gas": y_true,
                            "r_gas": r_raw,
                            "r_corrected": y_pred,
                            "datetime": datetime
                        },
                        index=idx,
                    )
    
                    csv_name = f"corrected_{gas}_{model}_{group}_rabbit{id_rabbit}_channel{id_channel}.csv"
                    df_out.to_csv(os.path.join(model_path, csv_name),sep=";")
    
                # ---------- PLOT ----------
                plt.figure(figsize=(10, 5))
                plt.plot(datetime, y_true, label=target_col, lw=2)
                plt.plot(datetime, r_raw, label=r_col, alpha=0.6)
                plt.plot(datetime, y_pred, label="r_corrected signal decomposition", alpha=0.8)
                plt.plot(datetime, y_pred_base, label="r_corrected base ", alpha=0.8)
    
                #plt.title(f"{gas} | Model: {model} | Group {name_grouping}: {group} \n  Rabbit {id_rabbit} – Channel {id_channel}")
                plt.title(f"{gas} | Model: {model} | Group: ALL   \n  Rabbit {id_rabbit} – Channel {id_channel}")
                plt.xlabel("Time")
                plt.ylabel("{gas} Concentration")
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(os.path.join(model_path, f"corrected_{gas}_{model}_{group}_rabbit{id_rabbit}_channel{id_channel}.png"))
                plt.show()
            



#%%Plot data base + models of different files
def plot_model_predictions(time_col,target_col,base_col, dic, df):
    """
    Boucle sur des modèles sauvegardés et trace leurs valeurs prédites.

    Parameters
    ----------
    model_paths : list[str]
        Liste des chemins vers les modèles (.joblib)
    features_list : list[list[str]]
        Liste des listes de features (une par modèle)
    df : pandas.DataFrame
        DataFrame contenant toutes les features
    x : array-like or None
        Axe x pour le plot (index par défaut)
    """

    id_cols = ["id_rabbit", "id_channel"]
    
    

    for (id_rabbit, id_channel), df_rc in df.groupby(id_cols):
        if len(df_rc) < 80:
            continue
        
        x = df_rc[time_col]
        start = pd.to_datetime(x.iloc[0])
        end   = pd.to_datetime(x.iloc[-1])
        
        plt.figure(figsize=(12, 5))
        plt.plot(x,df_rc[target_col],label = "NH3 innova")
        plt.plot(x,df_rc[base_col],label="NH3 rabbit")
        
        
        
        for key, dic_key in dic.items():
            path = dic_key["model_path"]
            features = dic_key["features_list"]
            label = dic_key["label"]
            
            df_key = df_rc.dropna(subset=features)
            x_key = df_rc.loc[df_key.index, time_col]
            # --- chargement du modèle ---
            model = joblib.load(path)
    
            # --- sélection des features ---
            X = df_key[features].copy()
    
            # --- prédiction ---
            y_pred = model.predict(X)
    
            # --- plot ---
            plt.plot(x_key, y_pred, label=label)

        plt.xlabel("Time")
        plt.ylabel("NH3 concentration (ppm)")
        plt.title(f"NH3 Concentration | Rabbit {id_rabbit} – Channel {id_channel} \n"
                  f"{start} to {end} ")
        # plt.title(f"NH3 | Model: XGB | Window size 52/72/144 | Rabbit {id_rabbit} – Channel {id_channel} \n"
        #           f"{start} to {end} ")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()



if False:
    gas = "NH3"
    target_col = f"i_{gas}"
    rabbit_cols = ["r_NH3", "r_temperature", "r_umidity","r_CO2","r_THI"]
    st_8 =  ["r_NH3", "r_temperature", "r_umidity", "r_CO2", "r_THI", "r_NH3_st_8h_rms", "r_NH3_st_8h_std", "r_NH3_st_8h_diff_last", "r_NH3_st_8h_slope", "r_umidity_st_8h_mean", "r_umidity_st_8h_std", "r_temperature_st_8h_diff_last", "r_temperature_st_8h_slope", "r_umidity_st_8h_diff_last"]
    st_2_8 = ["r_NH3", "r_temperature", "r_umidity", "r_CO2", "r_THI", "r_NH3_st_2h_min", "r_NH3_st_2h_std", "r_NH3_st_2h_diff_last", "r_NH3_st_2h_slope", "r_temperature_st_2h_min", "r_temperature_st_2h_std", "r_temperature_st_2h_diff_last", "r_temperature_st_2h_slope", "r_umidity_st_2h_std", "r_umidity_st_2h_diff_last", "r_NH3_st_8h_min", "r_NH3_st_8h_std", "r_NH3_st_8h_diff_last", "r_NH3_st_8h_slope", "r_umidity_st_8h_min", "r_temperature_st_8h_std", "r_temperature_st_8h_diff_last", "r_umidity_st_8h_slope", "r_umidity_st_8h_diff_last"]
    wl_2_8 = ["r_NH3", "r_temperature", "r_umidity", "r_CO2", "r_THI", "r_NH3_wl_2h_D1_energy", "r_NH3_wl_2h_A_energy", "r_NH3_wl_2h_A_rms", "r_NH3_wl_2h_D1_energy_rel", "r_temperature_wl_2h_D1_energy_rel", "r_temperature_wl_2h_A_energy", "r_temperature_wl_2h_A_rms", "r_umidity_wl_2h_D1_energy_rel", "r_umidity_wl_2h_A_energy", "r_umidity_wl_2h_A_rms", "r_NH3_wl_8h_D1_energy", "r_NH3_wl_8h_D2_energy", "r_NH3_wl_8h_D3_energy", "r_NH3_wl_8h_A_energy", "r_NH3_wl_8h_A_rms", "r_NH3_wl_8h_D2_energy_rel", "r_NH3_wl_8h_D3_energy_rel", "r_temperature_wl_8h_D1_energy", "r_temperature_wl_8h_D3_energy", "r_temperature_wl_8h_A_energy", "r_temperature_wl_8h_A_rms", "r_umidity_wl_8h_D1_energy_rel", "r_umidity_wl_8h_D2_energy", "r_umidity_wl_8h_D3_energy", "r_umidity_wl_8h_A_rms"]
    tsg_wl_2_8 = ["r_NH3", "r_temperature", "r_umidity", "r_CO2", "r_THI", "r_NH3_wl_2h_D1_energy", "r_NH3_wl_2h_A_energy", "r_NH3_wl_2h_A_rms", "r_NH3_wl_2h_A_energy_rel", "r_temperature_wl_2h_D1_energy_rel", "r_temperature_wl_2h_A_energy", "r_temperature_wl_2h_A_rms", "r_umidity_wl_2h_A_energy_rel", "r_umidity_wl_2h_A_energy", "r_umidity_wl_2h_A_rms", "r_NH3_wl_8h_D1_energy", "r_NH3_wl_8h_D2_energy", "r_NH3_wl_8h_D3_energy", "r_NH3_wl_8h_A_energy", "r_NH3_wl_8h_A_rms", "r_NH3_wl_8h_D2_energy_rel", "r_NH3_wl_8h_D3_energy_rel", "r_temperature_wl_8h_A_energy_rel", "r_temperature_wl_8h_D3_energy", "r_temperature_wl_8h_A_energy", "r_temperature_wl_8h_A_rms", "r_umidity_wl_8h_A_energy_rel", "r_umidity_wl_8h_D2_energy_rel", "r_umidity_wl_8h_D3_energy_rel", "r_umidity_wl_8h_A_rms"]
    dic = {
            # "REF_Lin":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\1-Reference\\best_Linear_ALL.joblib',
            #        "features_list": rabbit_cols,
            #        "label": 'Baseline NH3 Lin'},
           # "REF_LGBM":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\1-Reference\\best_LGBM_ALL.joblib',
           #                "features_list": rabbit_cols,
           #                "label": 'Baseline NH3 LGBM'},
           # "REF_Cat":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\1-Reference\\best_CatBoost_ALL.joblib',
           #                "features_list": rabbit_cols,
           #                "label": 'Baseline NH3 CatBoost'},
          
           # "Col_Lin":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\2-Grouping_column\\best_Linear_2.joblib',
           #                "features_list": rabbit_cols,
           #                "label": 'NH3 Lin Column 2'},
           # "Col_LGBM":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\2-Grouping_column\\best_LGBM_2.joblib',
           #                "features_list": rabbit_cols,
           #                "label": 'NH3 LGBM Column 2'},
           # "Col_Cat":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\2-Grouping_column\\best_CatBoost_2.joblib',
           #                "features_list": rabbit_cols,
           #                "label": 'NH3 CatBoost Column 2'},
           
           # "st8_Lin":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\st_8\\best_Linear_ALL.joblib',
           #                "features_list": st_8,
           #                "label": 'NH3 Lin st 8h'},
           # "st8_LGBM":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\st_8\\best_LGBM_ALL.joblib',
           #                "features_list": st_8,
           #                "label": 'NH3 LGBM st 8h'},
           # "st8_Cat":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\st_8\\best_CatBoost_ALL.joblib',
           #                "features_list": st_8,
           #                "label": 'NH3 CatBoost st 8h'},
           
           # "st_2_8_Lin":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\st_2_8\\best_Linear_ALL.joblib',
           #                "features_list": st_2_8,
           #                "label": 'NH3 Lin st 2h/8h'},
           # "st_2_8_LGBM":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\st_2_8\\best_LGBM_ALL.joblib',
           #                "features_list": st_2_8,
           #                "label": 'NH3 LGBM st 2h/8h'},
           # "st_2_8_Cat":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\st_2_8\\best_CatBoost_ALL.joblib',
           #                "features_list": st_2_8,
           #                "label": 'NH3 CatBoost st 2h/8h'},
           
           # "wl_2_8_Lin":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\wl_2_8\\best_Linear_ALL.joblib',
           #                "features_list": wl_2_8,
           #                "label": 'NH3 Lin wl 2h/8h'},
           # "wl_2_8_LGBM":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\wl_2_8\\best_LGBM_ALL.joblib',
           #                "features_list": wl_2_8,
           #                "label": 'NH3 LGBM wl 2h/8h'},
           # "wl_2_8_Cat":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\3-Historic\\wl_2_8\\best_CatBoost_ALL.joblib',
           #                "features_list": wl_2_8,
           #                "label": 'NH3 CatBoost wl 2h/8h'},
           
           "tsg_Lin":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\4-Additional results\\timeseriesplit_nodecomp\\best_Linear_ALL.joblib',
                          "features_list": rabbit_cols,
                          "label": 'NH3 Linear'},
           # "tsg_LGBM":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\4-Additional results\\timeseriesplit_nodecomp\\best_LGBM_ALL.joblib',
           #                "features_list": rabbit_cols,
           #                "label": 'NH3 LGBM '},
           # "tsg_Cat":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\4-Additional results\\timeseriesplit_nodecomp\\best_CatBoost_ALL.joblib',
           #                "features_list":rabbit_cols,
           #                "label": 'NH3 CatBoost'},
           
           "tsg_wl_2_8_Lin":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\4-Additional results\\timeseriesplit_decomp\\best_Linear_ALL.joblib',
                          "features_list": tsg_wl_2_8,
                          "label": 'NH3 Linear wl 2h/8h'},
           # "tsg_wl_2_8_LGBM":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\4-Additional results\\timeseriesplit_decomp\\best_LGBM_ALL.joblib',
           #                "features_list": tsg_wl_2_8,
           #                "label": 'NH3 LGBM wl 2h/8h'},
           # "tsg_wl_2_8_Cat":{"model_path": '..\\machine_learning_analysis\\6-Sensibility analysis\\5-Models\\4-Additional results\\timeseriesplit_decomp\\best_CatBoost_ALL.joblib',
           #                "features_list": tsg_wl_2_8,
           #                "label": 'NH3 CatBoost wl 2h/8h'},
          
           }
    
    file_path = "csv_decomposed/innova/df_signal_decomposition_NH3_ALL.csv"
    df_signal = pd.read_csv(file_path, sep=";")
    df_signal["datetime"] = pd.to_datetime(df_signal["datetime"])
    mask_period = (df_signal["datetime"] >= pd.Timestamp("2025-09-22")) & (df_signal["datetime"] <= pd.Timestamp("2025-09-25"))
    #mask_period = (df_signal["datetime"] >= pd.Timestamp("2025-06-17 12:00:00")) & (df_signal["datetime"] <= pd.Timestamp("2025-06-25"))
    #mask_period = (df_signal["datetime"] >= pd.Timestamp("2025-09-11")) & (df_signal["datetime"] <= pd.Timestamp("2025-09-15"))
    #mask_period = (df_signal["datetime"] >= pd.Timestamp("2026-01-14")) & (df_signal["datetime"] <= pd.Timestamp("2026-01-18"))
    df_period = (df_signal.copy())[mask_period]
    

    plot_model_predictions(time_col= "datetime",target_col="i_NH3",base_col="r_NH3", dic=dic, df=df_period)



