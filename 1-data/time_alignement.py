# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 09:00:54 2025

@author: titou
"""
import numpy as np
import pandas as pd
import datetime
import os


#Warning : ne peut pas être sur plusiseurs périodes: 
#Faire groupe correspondance innova/rabbit par période
#Filtrer par mesure tous : INPUT([(df_rabbit["datetime,"])])
#Common timescale(df_i_rabbit,df_i_innova, autre)



def correspondance_rabbit_innova(date, mode, debug=False): 
    """
    (x,y): (node_rabbit, position sl inova)
    'date' peut être un objet datetime.datetime ou datetime.date, ou une chaîne (formats pris en charge).
    """
    if debug:
        print("correspondance_rabbit_innova")

    # --- Conversion automatique ---
    if isinstance(date, str):
        try:
            # format JJ/MM/AAAA HH:MM (ou JJ/MM/AAAA)
            try:
                date = datetime.datetime.strptime(date, "%d/%m/%Y %H:%M:%S")
            except ValueError:
                date = datetime.datetime.strptime(date, "%d/%m/%Y").replace(hour=0, minute=0)
        except ValueError:
            # format AAAA-MM-JJ HH:MM (ou AAAA-MM-JJ)
            try:
                date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                date = datetime.datetime.strptime(date, "%Y-%m-%d").replace(hour=0, minute=0)

    # Si c’est un datetime.date pur, on le convertit aussi
    if isinstance(date, datetime.date) and not isinstance(date, datetime.datetime):
        date = datetime.datetime.combine(date, datetime.time(0, 0))

    # --- Sélection des régimes ---
    if mode == "day":

        if datetime.datetime(2025, 3, 13, 0, 0) <= date < datetime.datetime(2025, 3, 31, 16, 0):
            # période du 13/03 à 8h au 31/03 à 18h
            return [(4,11),(2,5),(6,5),(5,0)]

        if datetime.datetime(2025, 3, 31, 18, 0) <= date <= datetime.datetime(2025, 4, 18, 6, 0):
            return [(4,11),(2,5),(6,5),(1,0)]

        if datetime.datetime(2025, 4, 30, 9, 0) <= date <= datetime.datetime(2025, 5, 12, 23, 0):
            return [(4,11),(2,5),(6,5),(5,0)]

        if datetime.datetime(2025, 6, 12, 7, 30) <= date <= datetime.datetime(2025, 6, 25, 22, 0):
            #return [(2,11),(4,5),(1,4),(6,3),(5,0)]
            return [(2,11),(4,5),(1,3),(6,4),(5,0)] #switch

        if datetime.datetime(2025, 9, 11, 0, 0) <= date <= datetime.datetime(2025, 9, 25, 23, 59):
            #return [(2,11),(4,5),(6,4),(3,3),(5,0)]
            return [(2,11),(4,5),(6,3),(3,4),(5,0)] #switch
        
        if datetime.datetime(2026, 1, 14, 0, 0) <= date <= datetime.datetime(2026, 1, 21, 23, 59):
            return [(1,11),(4,11),(5,11),(6,11)]

    if mode == "all":
        date_range = [#2024
            [datetime.datetime(2024, 5, 27, 0, 0), datetime.datetime(2024, 5, 30, 23, 59)],
            [datetime.datetime(2024, 7, 11, 0, 0), datetime.datetime(2024, 7, 29, 8, 0)], # a voir les dates
            [datetime.datetime(2024, 7, 29, 9, 30), datetime.datetime(2025, 1, 8, 23, 59)], 
            #2025
            [datetime.datetime(2025, 3, 13, 8, 0), datetime.datetime(2025, 3, 31, 18, 0)],
            [datetime.datetime(2025, 3, 31, 18, 0), datetime.datetime(2025, 4, 18, 6, 0)],
            [datetime.datetime(2025, 4, 30, 9, 0), datetime.datetime(2025, 5, 12, 23, 0)],# problems on min/max time
            [datetime.datetime(2025, 6, 12, 7, 30), datetime.datetime(2025, 6, 25, 22, 0)],
            [datetime.datetime(2025, 9, 11, 0, 0), datetime.datetime(2025, 9, 25, 23, 59)],
            #2026
            [datetime.datetime(2026, 1, 14, 0, 0), datetime.datetime(2026, 1, 21, 23, 59)]
        ]

        correspondance = [#2024
            [(6,10),(6,11),(4,11),(4,5),(2,5)],
            [(3,11),(3,10)],
            [(2,11),(2,10),(4,11),(4,5),(6,5)],
            #2025
            [(4,11),(2,5),(6,5),(5,0)],
            [(4,11),(2,5),(6,5),(1,0)],
            [(4,11),(2,5),(6,5),(5,0)],
            
            #[(2,11),(4,5),(1,4),(6,3),(5,0)],
            [(2,11),(4,5),(1,3),(6,4),(5,0)],#switch
            
            #[(2,11),(4,5),(6,4),(3,3),(5,0)],
            [(2,11),(4,5),(6,3),(3,4),(5,0)],#switch
            #2026
            [(1,11),(4,11),(5,11),(6,11)]
        ]
        return (date_range, correspondance)
    
    return None



def common_time_scale(dfs, debug, time_col="datetime"):
    """
    Calcule une échelle de temps commune pour une liste de DataFrames,
    basée sur la série temporelle la plus lente (plus grand pas médian).
    
    Paramètres
    ----------
    dfs : list[pd.DataFrame]
        Liste de DataFrames contenant une colonne temporelle `time_col`.
    time_col : str
        Nom de la colonne temporelle.
    debug : bool
        Si True, affiche des informations de diagnostic.
    
    Retour
    ------
    t_common : np.ndarray
        Tableau de timestamps (en secondes) définissant l'échelle commune.
    """
    
    dfs = [df for df in dfs if df is not None and not df.empty and time_col in df.columns]
    
    if debug:
        print("COMMON_TIME_SCALE")
    print((dfs[0])["datetime"])
    print((dfs[1])["datetime"])
    if len(dfs)>2:
        print((dfs[2])["datetime"])
    # Conversion des temps en secondes
    times = [df[time_col].values.astype("datetime64[s]").astype(float) for df in dfs]

    # Intervalle commun
    t_start = max(t.min() for t in times)
    t_end   = min(t.max() for t in times)
    print("t_start",t_start)
    print("t_end",t_end)
    if t_start >= t_end:
        print("Pas d'intervalle temporel commun entre les séries.")
        return None
        

    # Choisir la série la plus lente (pas médian le plus grand)
    dts = [np.median(np.diff(t)) for t in times]
    idx_slow = np.argmax(dts)
    t_slow = times[idx_slow]

    # Points internes de la série lente
    t_internal = t_slow[(t_slow > t_start) & (t_slow < t_end)]
    t_common = np.concatenate(([t_start], t_internal, [t_end]))

    #if debug:
        #print(f"Série la plus lente = index {idx_slow}, Δt médian = {dts[idx_slow]:.1f}s")
        #print(f"Échelle commune : {len(t_common)} points entre {t_start} et {t_end}")

    return t_common

def create_groups_to_synchronise(dates_range, df_innova, df_rabbit, df_envea, df_ms):
    import pandas as pd
    
    list_to_synchronise = []
    #Selecting of non None dataframe
    
    list_df = [df for df in [df_innova, df_rabbit, df_envea, df_ms] if df is not None]
    
    for date_range in dates_range:
        print("DATE RANGE: ")
        start_date = pd.to_datetime(date_range[0])
        end_date   = pd.to_datetime(date_range[1])
        mean_date = (start_date + (end_date - start_date) / 2).date()
        print(f"{start_date}-{end_date}")
       
        
        list_df_filtered = []
    
        # Selecting the dtafarames between start date and end date
        for df in list_df:
            df = df.copy()  # Important pour éviter SettingWithCopyWarning
            df["datetime"] = pd.to_datetime(df["datetime"])
            df_filtered = df[df["datetime"].between(start_date, end_date)].copy()
            df_filtered["date"] = df_filtered["datetime"].dt.date  # pour travailler par jour
            list_df_filtered.append(df_filtered)
            print(f"LENGHT DF between {start_date}-{end_date}:{len(df_filtered)}")
    
        # Find common dates of all dfs
        list_df_filtered = mask_common_date(list_df_filtered)
    
    
        # Si on a df_innova et df_rabbit, on applique la correspondance
        if df_innova is not None and df_rabbit is not None:
            correspondance = correspondance_rabbit_innova(mean_date,mode="day", debug=False)
    
            # Si df_envea est None, on supprime les couples avec b=0
            if df_envea is None:
                correspondance = [(a, b) for (a, b) in correspondance if b != 0]
    
            for i, x in enumerate(correspondance):
                print("X:", x, "i:", i)
    
                # Appliquer les masques sur les DataFrames filtrés par date
                df_innova_f = list_df_filtered[0]
                df_rabbit_f = list_df_filtered[1]
    
                mask_innova = df_innova_f["id_channel"] == x[1]
                mask_rabbit = df_rabbit_f["id_rabbit"] == x[0]
    
                # Ajouter les DataFrames filtrés dans la liste
                list_to_synchronise.append(
                    [df_innova_f[mask_innova], df_rabbit_f[mask_rabbit]] + list_df_filtered[2:]
                )
        else:
            list_to_synchronise.append(list_df_filtered)

    return list_to_synchronise  

def create_groups_to_synchronise_all(df_innova, df_rabbit, df_envea, df_ms, debug):
    
    if debug:
        print("CREATE_GROUPS_TO_SYNCHRONISE_ALL")
    
    list_to_synchronise = []
    #Selecting of non None dataframe
    
    list_df = [df for df in [df_innova, df_rabbit, df_envea, df_ms] if df is not None]
    
    if df_innova is not None and df_rabbit is not None:
        list_period_idcorr = correspondance_rabbit_innova(date="2000-01-01",mode = "all", debug = True)
        periods, id_corr = list_period_idcorr[0],list_period_idcorr[1]
        if len(periods) != len(id_corr):
            raise ValueError("The length of the periods and id_corr are not matching: please verify the function : 'correspondance_innova_rabbit' (mode = 'all')")
    
    if df_envea is None:
        #print("ID_CORR:",id_corr)
        new_idcorr = []
        for x in id_corr:
            #print("X:",x)
            x = [(a,b) for (a, b) in x if b != 0]
            #print(x)
            new_idcorr.append(x)
        id_corr = new_idcorr
            #list_period_idcorr = (periods,id_corr)
    
    for j,period in enumerate(periods):
        print("***************")
        #print("DATE RANGE: ")
        start_date = pd.to_datetime(period[0])
        end_date   = pd.to_datetime(period[1])
        print(f"{start_date}-{end_date}")
       
        
        list_df_filtered = []
    
        # Filter the dtafarames between start date and end date
        for df in list_df:
            df = df.copy()  # Important pour éviter SettingWithCopyWarning
            df["datetime"] = pd.to_datetime(df["datetime"])
            df_filtered = df[df["datetime"].between(start_date, end_date)].copy()
            df_filtered["date"] = df_filtered["datetime"].dt.date  # pour travailler par jour
            list_df_filtered.append(df_filtered)
            print(f"LENGHT DF:    {len(df_filtered)}")
        # Find common dates of all dfs
        #list_df_filtered = mask_common_date(list_df_filtered,debug)
    
    
    
        for i, x in enumerate(id_corr[j]):
            print("X:", x, "i:", i)

            # Appliquer les masques sur les DataFrames filtrés par date
            df_innova_f = list_df_filtered[0]
            df_rabbit_f = list_df_filtered[1]

            mask_innova = df_innova_f["id_channel"] == x[1]
            mask_rabbit = df_rabbit_f["id_rabbit"] == x[0]
            
            #list_df_not_none = list
            #candidate_group = [df_innova_f[mask_innova], df_rabbit_f[mask_rabbit]] + list_df_filtered[2:]
            
            # if any(df.empty for df in candidate_group):
            #     if debug:
            #         print("⚠️ Groupe ignoré (un ou plusieurs DataFrames vides)")
            #     continue
        
            if (df_innova_f[mask_innova].empty or df_rabbit_f[mask_rabbit].empty):
                if debug:
                    print("⚠️ Groupe ignoré (Innova ou Rabbit vide)")
                continue
            candidate_group = [df_innova_f[mask_innova], df_rabbit_f[mask_rabbit]] + list_df_filtered[2:]
            # Ajouter les DataFrames filtrés dans la liste
            list_to_synchronise.append(candidate_group)
            

    return list_to_synchronise  

def mask_common_date(list_df,debug):
    if debug:
        print("MASK_COMMON_DATE")
    # S'assurer que la colonne 'date' est bien de type datetime.date
    for df in list_df:
        df["date"] = pd.to_datetime(df["date"]).dt.date
    
    # Extraire les ensembles de dates
    list_dates = [set(df["date"].unique()) for df in list_df]
    
    # Intersection : dates communes à tous les DataFrames
    dates_communes = sorted(set.intersection(*list_dates))
    print(f"{len(dates_communes)} dates communes trouvées :", dates_communes[:5], "...")
    
    # Filtrer chaque DataFrame sur ces dates
    list_df_filtered = [
        df[df["date"].isin(dates_communes)] for df in list_df]
  
    return list_df_filtered



def time_alignement_merge(list_dfs, t_common, 
                          time_col="datetime", 
                          exclude_cols=("datetime", "date","hour", "id_channel", "id_rabbit"),
                          min_valid_points=2):
    """
    Aligne et fusionne plusieurs DataFrames sur une échelle de temps commune,
    avec préfixe automatique basé sur les colonnes caractéristiques.

    Paramètres
    ----------
    list_dfs : list[pd.DataFrame]
        Liste de DataFrames à interpoler.
    t_common : np.ndarray
        Tableau de timestamps communs (en secondes).
    time_col : str
        Nom de la colonne temporelle.
    exclude_cols : tuple
        Colonnes à exclure de l'interpolation.
    min_valid_points : int
        Nombre minimal de points valides requis pour tenter une interpolation.

    Retour
    ------
    df_merged : pd.DataFrame
        DataFrame combiné avec toutes les colonnes interpolées et alignées.
    """
    df_merged = pd.DataFrame({time_col: pd.to_datetime(t_common, unit="s")})
    df_merged["date"] = df_merged[time_col].dt.date              # date seule
    df_merged["hour"] = df_merged[time_col].dt.strftime("%H:%M:%S")  # heure au format classique
    
    for df in list_dfs:
        if df is None or df.empty:
            continue  # On saute ce DataFrame
        # Détection automatique du préfixe
        if "id_rabbit" in df.columns:
            prefix = "r"
        elif "id_channel" in df.columns:
            prefix = "i"
        elif any(col.startswith("temperature_in") for col in df.columns):
            prefix = "ms"
        else:
            prefix = "df"  # fallback

        # Conversion du temps en secondes
        t = df[time_col].values.astype("datetime64[s]").astype(float)

        for col in df.columns:
            if col in exclude_cols:
                continue

            col_name = f"{prefix}_{col}"

            series = df[col]
            if not np.issubdtype(series.dtype, np.number):
                df_merged[col_name] = np.nan
                continue

            valid_mask = series.notna()
            if valid_mask.sum() < min_valid_points:
                df_merged[col_name] = np.nan
                continue

            try:
                if col in ["wind_dir_in","wind_dir_out"]:
                    # Interpolation circulaire sur les angles
                    angles = np.deg2rad(series[valid_mask].values)
                    x = np.cos(angles)
                    y = np.sin(angles)
                
                    # Interpolation linéaire sur les composantes x et y
                    x_interp = np.interp(t_common, t[valid_mask], x, left=np.nan, right=np.nan)
                    y_interp = np.interp(t_common, t[valid_mask], y, left=np.nan, right=np.nan)
                
                    # Recalcule l’angle interpolé en degrés
                    df_merged[col_name] = (np.degrees(np.arctan2(y_interp, x_interp)) + 360) % 360
                    
                else:
                    df_merged[col_name] = np.interp(
                        t_common,
                        t[valid_mask],
                        series[valid_mask].values,
                        left=np.nan,
                        right=np.nan,
                    )
            except Exception:
                df_merged[col_name] = np.nan

    return df_merged



def time_alignement_main(dates_range, df_innova, df_rabbit, df_envea, df_ms,debug):
    # Création des groupes à synchroniser (liste de listes de DataFrames)
    #list_to_synchronise = create_groups_to_synchronise(dates_range, df_innova, df_rabbit, df_envea, df_ms)
    if debug:
        print("TIME_ALIGNEMENT_MAIN")
    
    
    list_to_synchronise = create_groups_to_synchronise_all(df_innova, df_rabbit, df_envea, df_ms,debug)
    print("LEN list to sync:", len(list_to_synchronise))
    
    all_aligned = []  # pour stocker tous les DataFrames alignés
    all_t_common = []  # pour stocker toutes les échelles de temps

    for groupe in list_to_synchronise:
        df_innova_local = groupe[0]
        df_rabbit_local = groupe[1]
        
        # Échelle de temps commune pour ce groupe
        t_common = common_time_scale(groupe, debug, time_col="datetime")
        if t_common is None or len(t_common) == 0:
            continue
        all_t_common.append(t_common)

        # Interpolation + alignement
        df_aligned = time_alignement_merge(
            groupe,
            t_common,
            time_col="datetime",
            exclude_cols=("datetime", "date", "hour", "id_channel", "id_rabbit"),
            min_valid_points=2
        )

        df_aligned["id_rabbit"] = df_rabbit_local["id_rabbit"].iloc[0]  # ou prendre df_aligned["id_rabbit"].iloc[0]
        df_aligned["id_channel"] = df_innova_local["id_channel"].iloc[0]
        
        print("--------")
        t_print = pd.DataFrame(t_common)
        t_print = pd.to_datetime(t_common, unit="s").round("S")
        print("T0",t_print[0])
        print("T-1",t_print[-1])
        print("ID RABBIT", df_rabbit_local["id_rabbit"].iloc[0])
        print("ID CHANNEL",df_innova_local["id_channel"].iloc[0])
        
        all_aligned.append(df_aligned)
    
    if all_aligned:
        aligned_df = pd.concat(all_aligned, ignore_index=True)
        
        #aligned_df = aligned_df.sort_values("datetime").reset_index(drop=True)
        
        #  Rearrangement of the columns
        cols = list(aligned_df.columns)
        
        # On enlève id_rabbit et id_channel s'ils existent
        for col in ["id_rabbit", "id_channel"]:
            if col in cols:
                cols.remove(col)
        
        # On place id_rabbit et id_channel juste après 'date'
        if "hour" in cols:
            idx = cols.index("hour") + 1
            cols = cols[:idx] + ["id_rabbit", "id_channel"] + cols[idx:]
            
        aligned_df = aligned_df[cols]
        
        #Grouping of 
        aligned_df = aligned_df.sort_values(["date", "id_rabbit", "datetime"]).reset_index(drop=True)
        aligned_df["datetime"] = pd.to_datetime(aligned_df["datetime"])
        aligned_df["datetime"] = aligned_df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
        aligned_df.to_csv("current_df_aligned_ALL_switched.csv", index=False,sep=";")
        print(f"✅ Fichier exporté : current_df_aligned_all.csv ({len(aligned_df)} lignes)")
    else:
        print("⚠️ Aucun DataFrame à concaténer !")


    return all_aligned, all_t_common

    
def switch_innova(df_innova):
    df_innova = df_innova.copy()
    df_innova["datetime"] = pd.to_datetime(df_innova["datetime"])
    mask_period = (df_innova["datetime"] >= pd.Timestamp("2025-06-10")) & (df_innova["datetime"] <= pd.Timestamp("2025-09-30"))
    df_innova.loc[mask_period,"id_channel_tmp"]=df_innova.loc[mask_period,"id_channel"]
    df_innova.loc[mask_period & (df_innova["id_channel_tmp"] == 3),"id_channel"] = 4
    df_innova.loc[mask_period & (df_innova["id_channel_tmp"] == 4),"id_channel"] = 3
    # suppression colonne temporaire
    df_innova.drop(columns="id_channel_tmp", inplace=True)

    return df_innova

            
def main(debug):          
    df_innova = pd.read_csv("data_common_dates/current_df_innova_CD.csv",sep=";")
    #df_innova = switch_innova(df_innova)
    
    # df_innova["datetime"] = pd.to_datetime(df_innova["datetime"], utc=True)
    # df_innova["datetime_paris"] = df_innova["datetime"].dt.tz_convert("Europe/Paris")
    # df_innova["datetime_paris"] = df_innova["datetime_paris"].dt.tz_localize(None)
    # df_innova["date_paris"] = df_innova["datetime_paris"].dt.date
    # df_innova["hour_paris"] = df_innova["datetime_paris"].dt.time
    # df_innova = df_innova.drop(columns=["datetime", "date", "hour"])
    # df_innova = df_innova.rename(columns={
    #     "datetime_paris": "datetime",
    #     "date_paris": "date",
    #     "hour_paris": "hour"
    # })
    df_rabbit = pd.read_csv("data_common_dates/current_df_rabbit_CD.csv",sep=";")
    df_meteostation = pd.read_csv("data_common_dates/current_df_meteo_station_CD.csv",sep=";")
    if os.path.exists("data_common_dates/current_df_envea_CD.csv"):
        df_envea = pd.read_csv("data_common_dates/current_df_envea_CD.csv",sep=";")
    else:
        df_envea = None
    
    time_alignement_main(["2020-01-01"], df_innova, df_rabbit, df_envea, df_meteostation,debug)
    














#%% DRAFT

def apply_threshold(df,instrument):
    dic_threshold = {
        "innova": {
            "NH3": {"min": 0, "max": 100},
            "CO2": {"min": 0, "max": 5000}
            },
        "rabbit": {
            "NH3": {"min": 0, "max": 100},
            "CO2": {"min": 0, "max": 5000},
            "temperature": {"min": -20, "max": 50},
            "humidity": {"min": 0, "max": 100}
        },
        "meteo_station": {
            "temperature": {"min": -20, "max": 50},
            "dew_point": {"min": -20, "max": 50},
            "wet_bulb": {"min": -20, "max": 50},
            "humidity": {"min": 0, "max": 100},
            "wind_dir": {"min" :0, "max": 360},
            "wind_gust": {"min" :0, "max": 40},
            "wind_speed": {"min" :0, "max": 40},
        }
    }
    if instrument in dic_threshold:
        dic_instr = dic_threshold[instrument]
        for measure in dic_instr:
            min_val = dic_instr[measure]["min"]
            max_val = dic_instr[measure]["max"]
            df.loc[(df[measure] < min_val) | (df[measure] > max_val), measure] = np.nan
        
    return df
