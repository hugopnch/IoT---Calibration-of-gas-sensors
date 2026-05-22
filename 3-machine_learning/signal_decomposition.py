# -*- coding: utf-8 -*-
"""
Created on Fri Jan 16 15:54:36 2026

@author: titou
"""
#%% Packages
import os
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

import json
import pywt
from scipy.signal import find_peaks

#%% Utilitaires pre-processing
def assign_campaign(dt):
    if pd.Timestamp("2025-03-31") <= dt <= pd.Timestamp("2025-05-12"):
        return "other"#"2025_Apr"
    elif pd.Timestamp("2025-06-12") <= dt <= pd.Timestamp("2025-06-25"):
        return "2025_Jun"
    elif pd.Timestamp("2025-09-11") <= dt <= pd.Timestamp("2025-09-25"):
        return "2025_Sep"
    elif pd.Timestamp("2026-01-14") <= dt <= pd.Timestamp("2026-01-22"):
        return "other"#"2026_Gen"
    else:
        return "other"

def assign_campaign_iCO2(dt):
    if pd.Timestamp("2025-03-31") <= dt <= pd.Timestamp("2025-04-16"):
        return "2025_Apr_1"
    elif pd.Timestamp("2025-04-16") <= dt <= pd.Timestamp("2025-05-12"):
        return "2025_Apr_2"
    elif pd.Timestamp("2025-06-12") <= dt <= pd.Timestamp("2025-06-25"):
        return "2025_Jun"
    elif pd.Timestamp("2025-09-11") <= dt <= pd.Timestamp("2025-09-25"):
        return "2025_Sep"
    elif pd.Timestamp("2026-01-14") <= dt <= pd.Timestamp("2026-01-22"):
        return "2026_Gen"
    else:
        return "other"
    


def assign_innova_point_iCO2(row):
    camp = row["campaign"]
    rid = row["id_rabbit"]
    
    if camp == "2025_Apr_1":
        mapping = {1: "no", 2: "sl5", 4: "sl11", 6: "sl5"}
    elif camp == "2025_Apr_2":
        mapping = {1: "no", 2: "no", 4: "no", 6: "no"}
    elif camp == "2025_Jun":
        mapping = {2: "sl11", 4: "sl5", 1: "sl3", 6: "sl4", 5: "no"}
    elif camp == "2025_Sep":
        mapping = {2: "sl11", 4: "sl5", 6: "sl3", 3: "sl4", 5: "no"}
    elif camp == "2026_Gen":
        #mapping = {1: "no", 4: "no", 5: "sl11", 6: "no"}
        mapping = {1: "no", 4: "no", 5: "sl11", 6: "sl11"}
    else:
        mapping = {}

    return mapping.get(rid, "no")

def assign_innova_point(row):
    camp = row["campaign"]
    rid = row["id_rabbit"]
    

    if camp == "2025_Apr":
        mapping = {1: "no", 2: "sl5", 4: "sl11", 6: "sl5"}
    elif camp == "2025_Jun":
        mapping = {2: "sl11", 4: "sl5", 1: "sl3", 6: "sl4", 5: "no"}
    elif camp == "2025_Sep":
        mapping = {2: "sl11", 4: "sl5", 6: "sl3", 3: "sl4", 5: "no"}
    elif camp == "2026_Gen":
        mapping = {1: "sl11", 4: "no", 5: "sl11", 6: "sl11"}
    else:
        mapping = {}

    return mapping.get(rid, "no")

def assign_altezza(row):
    sl = row["innova_point"]
    if sl in ["sl11","sl3"]:
        return 155
    elif sl in ["sl5","sl4"]:
        return 270
    
    return None 

def assign_colonna(row):
    sl = row["innova_point"]
    if sl in ["sl11","sl5"]:
        return 1
    elif sl in ["sl3","sl4"]:
        return 2
    
    return None 

def assign_hot_season(row):
    cmp = row["campaign"]
    if cmp in ["2026_Gen","2025_Apr"]:
        return 0
    elif cmp in ["2025_Jun","2025_Sep"]:
        return 1
    return None

def assign_cold_season(row):
    cmp = row["campaign"]
    if cmp in ["2026_Gen","2025_Apr"]:
        return 1
    elif cmp in ["2025_Jun","2025_Sep"]:
        return 0
    return None


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


def e_time_period(dt):
    if pd.Timestamp("2025-03-13") <= dt <= pd.Timestamp("2025-04-19"):
        return "2025_MarApr"
    elif pd.Timestamp("2025-04-30") <= dt <= pd.Timestamp("2025-05-12"):
        return "2025_May"
    else:
        return "other"

def clean_NR(s):
    return int(s[1:])


#%% Utilitaires Features decomposition
def wavelet_features(signal, wavelet="db4", level=3):
    """
    Calculation of the wavelet decomposition features for a window
    Args:
        signal : 1D array of the signal (the window)
        wavelet : name of the wavelet filter
        level : max level of decomposition
    Returns:
        dict : features {D1_energy, D1_energy_rel, ..., A_rms, A_energy_rel} or None if impossible
    """
    signal = np.asarray(signal)
    if len(signal) == 0:
        return None

    # Calcul of the level max of decomposition possible given the length of the signal
    max_level = pywt.dwt_max_level(len(signal), pywt.Wavelet(wavelet).dec_len)
    level_used = min(level, max_level)
    if level_used == 0:
        return None
    else:
        # Wavelet decomposition
        coeffs = pywt.wavedec(signal, wavelet, level=level_used)
        A = coeffs[0]       # approximation
        Ds = coeffs[1:]     # details
    
        feats = {}
        
        # Engineered features on the wavelet decomposition
        energies = [] # energy of the details
        for j, D in enumerate(Ds, start=1):
            E = np.mean(D**2)
            feats[f"D{j}_energy"] = E
            energies.append(E)
    
       
        E_A = np.mean(A**2)  # energy of the approximation
        feats["A_energy"] = E_A
        feats["A_rms"] = np.sqrt(np.mean((A - A.mean())**2)) # RMS of the approximation
    
       
        total_energy = sum(energies) + E_A #total energy
        if total_energy == 0 or np.isnan(total_energy):
            return None  
    
       
        for j in range(1, len(Ds) + 1):
            feats[f"D{j}_energy_rel"] = feats[f"D{j}_energy"] / total_energy # Relative energy
        feats["A_energy_rel"] = E_A / total_energy 

    return feats

def stats_features(signal):
    """
    Calculation of the wavelet decomposition features for a window
    Args:
        signal : 1D array of the signal (the window)
    Returns:
        dict : features {mean, std, ... , slope} or None if impossible
    """
    
    
    x = np.asarray(signal, dtype=float)
    feats = {}

    
    x = x[np.isfinite(x)] # Cleaning NaN / inf
    
    if len(x) < 2:
        return None

    feats["mean"] = np.mean(x)
    feats["std"] = np.std(x)
    feats["rms"] = np.sqrt(np.mean(x**2))
    feats["median"] = np.median(x)
    feats["min"] = np.min(x)
    feats["max"] = np.max(x)

    
    feats["diff_last"] = x[-1] - x[-2] if len(x) > 1 else 0.0 # Simple dynamic
    
    if len(x) >= 3 and np.std(x) > 1e-6: # Robust slope
        t = np.arange(len(x))
        try:
            feats["slope"] = np.polyfit(t, x, 1)[0]
        except np.linalg.LinAlgError:
            feats["slope"] = 0.0
    else:
        feats["slope"] = 0.0

    return feats

def fft_features(signal,datetime_index,k_peaks=3,min_freq=1/48):
    """
    Calculation of the features decomposition  for a window
    Args:
        signal : 1D array of the signal (the window)
        datetime_index: 1D array of the datetime of the window
        k_peaks: number of first peaks
        min_freq: the minimum frequency acceptable
    Returns:
        dict : features {fft_f1_cph,fft_period1_h, fft_power1, ....} or None if impossible
    """
    

    
    
    signal = np.asarray(signal)
    if len(signal) < 4:
        return None

    # Mean dt between 2 measures (in h)
    dt_hours = np.mean(np.diff(datetime_index).astype("timedelta64[s]").astype(float)) / 3600.0
    start = pd.to_datetime(datetime_index[0])
    end   = pd.to_datetime(datetime_index[-1])
    
    # FFT
    signal_detrended = signal - np.mean(signal)
    fft_vals = np.fft.rfft(signal_detrended)
    power = np.abs(fft_vals)**2
    freqs = np.fft.rfftfreq(len(signal), d=dt_hours)

    # Removal of f=0 (mean component)
    freqs = freqs[1:]
    power = power[1:]
    
    
    duration_hours = (pd.to_datetime(datetime_index[-1]) - pd.to_datetime(datetime_index[0])).total_seconds() / 3600
    # Min frequency observable
    min_freq_signal = 1.0 / duration_hours


    if min_freq is not None:
        min_freq_effective = max(min_freq, min_freq_signal)
        mask = freqs >= min_freq_effective
        freqs = freqs[mask]
        power = power[mask]

    if len(power) == 0:
        return None

    
    # Identification of the peaks
    peaks, _ = find_peaks(power, distance=2) # To add a threshold (per example valid peaks should have at least 10% of the principal peak), add in find peaks height = 0.1*power.max()
    if len(peaks) == 0:
        return None
    else:
        peak_powers = power[peaks]
        idx_sorted = peaks[np.argsort(peak_powers)[::-1]]  # sorted by power
    
    idx_sorted = idx_sorted[:k_peaks]

    # Construction of the results dic
    feats = {}
    for i, idx in enumerate(idx_sorted, start=1):
        f = freqs[idx]
        feats[f"fft_f{i}_cph"] = f # frequency (per h)
        feats[f"fft_period{i}_h"] = 1.0 / f if f > 0 else np.nan # period (in h)
        feats[f"fft_power{i}"] = power[idx] # power


    return feats



def build_features_test(df, target_col ="r_NH3",window_sizes={'1h':1,'6h':6,'24h':24},
                        min_points_ratio = 0.8, split_mn=60,groups=[], method=None):
    """
    The main function for the decomposition that coordinates the different decomposition.
    Args:
        df : pd.dataframe
        target_col: str of the colummn to decompose
        window_sizes: dic with format {'Xh':X, .. , 'Yh': Y } with the windows sizes wanted for the decomposition
        min_points_ratio: float between [0,1] it is a rejection criteria for the window ; 
                          1 strict: the window should have exactly the number of points required (calculated with the mean dt of the group)
                          0: as if there is no control on the length of the window
        split_mn: float that cut a group in 2 if the distance between 2 measure is superior to this float
        groups: list of str or []
        method: 'fft','wavelet' or 'stats'
    """
    
    window_lengths = {h: [] for h in window_sizes}
    features_all = []
    features_start = [c for c in df.columns]
    
    
    if groups == []:
        iterable = [("ALL", df)]
    else:
        iterable = df.groupby(groups)
     
     
    groups = groups
    for args, df_sub in iterable :
        df_sub = df_sub.sort_values("datetime").reset_index(drop=True)
        dt = df_sub["datetime"].diff()
        df_sub["segment"] = (dt > pd.Timedelta(minutes=split_mn)).cumsum() # Creating the portions (split when delta > split_min
        
        for  seg , df_pair in df_sub.groupby("segment"):
            df_pair = df_pair.sort_values("datetime").reset_index(drop=True)
            times = df_pair["datetime"].values
            values = df_pair[target_col].values
            
            # Calcul of the mean dt of the segment
            dt_mean = np.nanmean(np.diff(times).astype("timedelta64[s]").astype(float)) / 60 #in minutes
            if np.isnan(dt_mean) or dt_mean == 0:
                continue
            
            # Calcul of the mean number of points that should be inside each window
            window_sizes_mean = {}
            for h,w in window_sizes.items():
                n_hour = int(h.replace("h", ""))
                w_size_mean = int((n_hour * 60) / dt_mean)
                window_sizes_mean[h] = max(w_size_mean, 1)
    
            if len(df_pair) <= min_points_ratio*min(window_sizes_mean.values()):
                continue
            
            # Decomposition feature calcul for each row
            for idx in range(len(df_pair)):
                row_feats = {}
                row_feats["datetime"] = times[idx]
                
                if groups != []:
                    for x,y in zip(args,groups):
                        row_feats[f'{y}'] = x # ID of the grouping
                
                t_now=times[idx]
                
                # Decomposition feature calcul for each window
                for h,w in window_sizes.items():
                    # Creation of the window
                    if True:
                        n_hour = int(h.replace("h",""))
                        t_start = t_now - np.timedelta64(n_hour, "h")
                        start_idx = np.searchsorted(times, t_start)
                        window = values[start_idx:idx]
                        w_size_mean = window_sizes_mean[h]
                        window = df_pair[
                            (df_pair["datetime"] < t_now) &
                            (df_pair["datetime"] >= t_start) ][target_col].values
                
                        if len(window) < min_points_ratio*w_size_mean:
                            continue
                    
            
                    if False: #Old version
                        w_size = window_sizes[h]
                        window = df_pair.loc[idx-w_size:idx-1, target_col].values
                        if len(window)<w_size:
                            continue
                    window_lengths[h].append(len(window))
                    
                    # Calcul of the decomposition dipending of the choosen method
                    feats_w = None
                    if method == "fft":
                        datetime_index = times[start_idx:idx]
                        feats_w = fft_features(window,datetime_index,k_peaks=3,min_freq=1/48)
                        method_abr = "fft"
                    elif method == "wavelet":
                        feats_w = wavelet_features(window,wavelet="db2")
                        method_abr = "wl"
                    elif method =="stats":
                        feats_w = stats_features(window)
                        method_abr = "st"
                    else:
                        raise ValueError("No feature method selected between 'stats','fft','wavelet'")
                    
                    if feats_w is None:
                        continue  # Calculus impossible on this window
        
                    # Storage of the row results
                    for k, v in feats_w.items():
                        row_feats[f"{target_col}_{method_abr}_{h}_{k}"] = v
                        
                
                if len(row_feats) > 2:  # Should be composed of at least the datetime and the ID
                    features_all.append(row_feats)
    
    # Results to dataframe
    df_features = pd.DataFrame(features_all)
    df_merged = df.merge(df_features,on=["datetime"]+groups,how="left")
    features_add = [c for c in df_merged.columns if c not in features_start+["segment"]]
    
    
    
    # Statistics of the windows length for feedback
    stats_windows = []
    for h, lengths in window_lengths.items():
        if len(lengths) == 0:
            continue
            
        lengths = np.array(lengths)
        
        stats_windows.append({
            "window": h,
            "mean": lengths.mean(),
            "min": lengths.min(),
            "max": lengths.max(),
            "median": np.median(lengths),
            "iqr": np.percentile(lengths,75) - np.percentile(lengths,25)
        })
    
    df_window_stats = pd.DataFrame(stats_windows)
    
    return df_merged,features_add, df_window_stats


#%% Models and grids

models = {
        "Linear": LinearRegression(),
        "XGB": XGBRegressor(objective="reg:squarederror", random_state=42),
        "RFC": RandomForestRegressor(random_state=42),
    }

param_grids = {
    "RFC" : {
        "reg__n_estimators": [200, 500],
        "reg__max_depth": [None, 10, 20],
        "reg__min_samples_split": [2, 5],
        "reg__min_samples_leaf": [1, 2],
    },
    
    "XGB" : {
        "reg__n_estimators": [100, 300],
        "reg__max_depth": [3, 5, 7],
        "reg__learning_rate": [0.01, 0.05, 0.1],
        "reg__subsample": [0.8, 1.0],
        "reg__colsample_bytree": [0.8, 1.0],
    }
}


#%% Main importation and pre-processing


def import_data_IR():
    file_path = "csv_decomposed/innova/current_df_aligned_ALL_switched.csv"
    df = pd.read_csv(file_path, sep=";")
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["campaign"] = df["datetime"].apply(assign_campaign)
    
    df = df[df["campaign"] != "other"].copy()
    
    df["hot"] = df.apply(assign_hot_season,axis=1)
    df_debug = df
    df["innova_point"] = df.apply(assign_innova_point, axis = 1)#_iCO2, axis=1)
    df = df[df["innova_point"] != "no"].copy()
    
    # mask_threshold = df["r_CO2"]>400
    # df = df[mask_threshold].copy()

    return df, df_debug
    


def import_data_ER():
    file_path = "csv_decomposed/envea/envea_rabbit.csv"
    df = pd.read_csv(file_path, sep=";")
    
    df["datetime"] = pd.to_datetime(df["Data Legale"]+" "+df["ORA LEGALE"])
    df = df[['datetime','Rabbit','Per. conc.','Valori PM2.5','Umidità','temperatura']]
    df["Rabbit"] = df["Rabbit"].apply(clean_NR)
    df = df.rename(columns={'Rabbit': "id_rabbit",
                            'Per. conc.': "e_PM_2.5",
                            'Valori PM2.5': "r_PM_2.5",
                            'Umidità': "r_umidity",
                            'temperatura': "r_temperature"})  
    
    df.sort_values("datetime").reset_index(drop=True)
    df["campaign"] = df["datetime"].apply(e_time_period)
    return df


    
   
#%% MAIN Command

# Data import and masks
flag_IR = False # Innova
flag_ER = True # Envea

# Functions flag
main_study = True
flag_decomposition = True
flag_export_decomposition_feats = True


if __name__ == "__main__": 
    #target_col = ["r_CO2"]
    if flag_IR:
        path_export = "csv_decomposed/innova"
        df, df_debug = import_data_IR()
           
    if flag_ER:
        path_export = "csv_decomposed/envea"
        df = import_data_ER()
    
    
    if main_study:
        methods = ["stats","wavelet","fft"] 
        features_decomposition_all = {}
        if flag_IR:
            window_sizes={'8h':52,'12h':72,'24h':144}
            window_sizes_test={'1h':1,'2h':2,'3h':3,'4h':4,'6h':6,'8h':8,'12h':12,'24h':24}
            target_col = "i_NH3"
            decomp_targets = ['r_NH3','r_temperature','r_umidity']
            features_rabbit = ["r_NH3", "r_temperature","r_umidity","r_CO2","r_THI"]
            encoding_col = [] #["hot"]
            grouping_col = []
        if flag_ER:
            window_sizes={'8h':8,'12h':12,'24h':24}
            window_sizes_test={'1h':1,'2h':2,'3h':3,'4h':4,'6h':6,'8h':8,'12h':12,'24h':24}
            target_col = "e_PM_2.5"
            decomp_targets = ["r_PM_2.5", "r_temperature","r_umidity"]
            features_rabbit = ["r_PM_2.5", "r_temperature","r_umidity"] 
            encoding_col = []
            grouping_col = []
           
        print(f"Methods: {methods} | window_sizes: {window_sizes_test} ")
        
        df_features = df.copy()
        if flag_decomposition:
            for target in decomp_targets:     
                for method in methods:
                    label = f'{target}_{method}'
                    print("Label:", label)
                    
                    if flag_IR:
                        df_features,features_decomposition,df_window_stats = build_features_test(df_features, target_col = target,
                                                                                window_sizes=window_sizes_test,min_points_ratio = 0.9,
                                                                                split_mn=60,groups=["id_rabbit","id_channel"], method=method)
                        features_decomposition_all[label]=features_decomposition
                    if flag_ER:
                        df_features,features_decomposition,df_window_stats = build_features_test(df_features, target_col = target,
                                                                                 window_sizes=window_sizes_test,min_points_ratio = 0.9,
                                                                                 split_mn=4*60,groups=["campaign","id_rabbit"], method=method)
                        features_decomposition_all[label]=features_decomposition
            
            features_engineered = [x for lst in features_decomposition_all.values() for x in lst]
            
            if flag_export_decomposition_feats:
                df_features.to_csv(f"{path_export}/df_signal_decomposition_PM2.5_ALL.csv",sep=";",index=False)
                with open(f"{path_export}/features_decomposition_list_PM2.5_ALL.json", "w") as f:
                    json.dump(features_decomposition_all, f)
     
            
            
      

   
        

                                   
                                   
    








  


        
