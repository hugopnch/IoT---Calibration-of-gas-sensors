# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 11:41:15 2025

@author: titou
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Dec  9 16:05:36 2025

@author: titou
"""

#%% Packages importation
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import make_scorer

from sklearn.model_selection import train_test_split, GridSearchCV, KFold,ShuffleSplit, GroupKFold,StratifiedShuffleSplit
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.svm import SVR
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import joblib
from scipy.stats import pearsonr
from scipy.signal import find_peaks
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import BayesianRidge

#%% Functions pre-processing

def assign_campaign(dt):
    if pd.Timestamp("2025-06-12") <= dt <= pd.Timestamp("2025-06-25"):
        return "2025_Jun"
    elif pd.Timestamp("2025-09-11") <= dt <= pd.Timestamp("2025-09-25"):
        return "2025_Sep"
    else:
        return "other"


def assign_innova_point(row):
    camp = row["campaign"]
    rid = row["id_rabbit"]

    if camp == "2025_Jun":
        mapping = {2: "sl11", 4: "sl5", 1: "sl4", 6: "sl3", 5: "no"}
    elif camp == "2025_Sep":
        mapping = {2: "sl11", 4: "sl5", 6: "sl4", 3: "sl3", 5: "no"}
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

def assign_humidity(row):
    hum = row["r_umidity"]
    if hum <=65:
        return 0
    elif hum <=75:
        return 1
    elif hum<=100:
        return 2
    else:
        return None






#%% Bins error analysis

def get_ytest_ypred(df, target_col, features, model, param_grid=None,pred_col  =None, test_size=0.2, random_state=42):
    """
    Sub-function of analyze_model_bins
    Args:
        df: pd.dataframe
        target_col: str , column to predict
        features: list of str for model training to include even if model = None (usefull for bining after)
        model: estimator sklearn (or None)
        param_grid: dic of hyper-parameters (optionnal)
        pred_col: str or None (to include if model = None --> return this column as prediction)
        test_size: float between [0,1]
        
    Return y_test, y_pred and X_test_df (features associated)
    """
    df = df.copy()
    X = df[features]
    y = df[target_col]

    mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
    X, y = X[mask], y[mask]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    pipe = Pipeline([("scaler", StandardScaler()), ("reg", model)])
    
    if model == None:
        y_pred = df.loc[X_test.index,pred_col].values
    elif param_grid:
        gs = GridSearchCV(pipe, param_grid=param_grid, scoring="r2", cv=3, n_jobs=-1)
        gs.fit(X_train, y_train)
        best_model = gs.best_estimator_
        y_pred = best_model.predict(X_test)
    else:
        best_model = pipe
        best_model.fit(X_train, y_train)
        y_pred = best_model.predict(X_test)

    
    X_test_df = pd.DataFrame(X_test, columns=features)  

    return y_test.values, y_pred, X_test_df


def bin_error_1d(y_test, y_pred, feature, bins=5, plot=True, feature_name=None,metric="",model_name=""):
    """
    Sub-function of analyze_model_bins
    Args:
        y_test, y_pred (from get_ytest_ypred)
        feature: array of the feature we want to analyze
        bins: int of n° of bins wanted
        plot: Bool to activate or no the plot
        feature_name: str
        metric: "mae","rmse", or "r2"
        model_name: str for title of the plot, if None just put the column used for y_pred
    Purpose and returns:
        Plot the errors between y_test and y_pred function of the feature. 
        Return the edges, the value of the score as well as the count (effectif) of each bin
    """
    
    feature = np.array(feature)
    y_test = np.array(y_test)
    y_pred = np.array(y_pred)

    bin_edges = np.linspace(feature.min(), feature.max(), bins+1)
    bin_metric = []
    counts = []

    for i in range(bins):
        mask = (feature >= bin_edges[i]) & (feature < bin_edges[i+1])
        counts.append(mask.sum())
        if np.sum(mask) > 0:
            if metric.lower() == "mae":
                metric_score = np.mean(np.abs(y_test[mask] - y_pred[mask]))
            elif metric.lower() == "rmse":
                metric_score = np.sqrt(np.mean((y_test[mask] - y_pred[mask])**2))
            elif metric.lower() == "r2":
                from sklearn.metrics import r2_score
                metric_score = r2_score(y_test[mask], y_pred[mask])
            else:
                raise ValueError(f"Metric {metric} not recognized. Choose 'MAE', 'RMSE', or 'R2'.")
        else:
            metric_score = np.nan
        bin_metric.append(metric_score)

    if plot:
        plt.figure(figsize=(6,4))
        plt.bar(range(bins), bin_metric, width=0.8, tick_label=[f"{bin_edges[i]:.2f}-{bin_edges[i+1]:.2f}" for i in range(bins)])
        plt.ylabel(f"{metric}")
        plt.xlabel(feature_name or "Feature")
        plt.title(f"{metric} per bin (1D) {model_name} model")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()
        
        plt.figure(figsize=(6,4))
        plt.bar(range(bins), counts, tick_label=[f"{bin_edges[i]:.1f}-{bin_edges[i+1]:.1f}" for i in range(bins)], color='orange')
        plt.ylabel("Count")
        plt.xlabel(f"Feature bin {feature_name}")
        plt.title(f"Effectif par bin ({model_name})")
        plt.show()

    return bin_edges, bin_metric,counts


def bin_error_2d(y_test, y_pred, feature_x, feature_y, bins_x=5, bins_y=5, plot=True, names=("X","Y"),metric="",model_name=""):
    """
    Sub-function of analyze_model_bins
    Args:
        y_test, y_pred (from get_ytest_ypred)
        feature_x, feature_y: array of the feature we want to analyze
        bins_x, bins_y : int of n° of bins wanted for each of the feature
        plot: Bool to activate or no the plot
        names: (str,str) name of each feature
        metric: "mae","rmse", or "r2"
        model_name: str for title of the plot, if None just put the column used for y_pred
    Purpose and returns:
        Plot the error heatmap between y_test and y_pred function of the features. 
        Return the edges, the grid value of the score as well as the grid count (effectif)
    """
    
    
    x = np.array(feature_x)
    y = np.array(feature_y)
    y_test = np.array(y_test)
    y_pred = np.array(y_pred)

    x_edges = np.linspace(x.min(), x.max(), bins_x+1)
    y_edges = np.linspace(y.min(), y.max(), bins_y+1)

    error_grid = np.full((bins_x, bins_y), np.nan)
    count_grid = np.zeros((bins_x, bins_y))

    for i in range(bins_x):
        for j in range(bins_y):
            mask = (x >= x_edges[i]) & (x < x_edges[i+1]) & (y >= y_edges[j]) & (y < y_edges[j+1])
            count_grid[i, j] = mask.sum()
            if np.sum(mask) > 0:
                if metric.lower() == "mae":
                   error_grid[i, j] = np.mean(np.abs(y_test[mask] - y_pred[mask]))
                elif metric.lower() == "rmse":
                    error_grid[i, j] = np.sqrt(np.mean((y_test[mask] - y_pred[mask])**2))
                elif metric.lower() == "r2":
                    from sklearn.metrics import r2_score
                    error_grid[i, j] = r2_score(y_test[mask], y_pred[mask])
                else:
                    raise ValueError(f"Metric {metric} not recognized. Choose 'MAE', 'RMSE', or 'R2'.")
              

    if plot:
        plt.figure(figsize=(6,5))
        plt.imshow(error_grid.T, origin="lower",
                   extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
                   aspect='auto', cmap='viridis')
        plt.colorbar(label=metric)
        plt.xlabel(names[0])
        plt.ylabel(names[1])
        plt.title(f"{metric} per bin (2D) for {model_name} model")
        plt.show()
        
        masked_counts = np.ma.masked_where(count_grid.T == 0, count_grid.T)
        cmap = plt.cm.plasma
        cmap.set_bad(color='white')
        
        plt.figure(figsize=(6,5))
        plt.imshow(masked_counts, origin="lower",
                   extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
                   aspect='auto', cmap=cmap)
        cbar = plt.colorbar()
        cbar.set_label("Effectif")
        plt.xlabel(f"Feature {names[0]}")
        plt.ylabel(f"Feature {names[1]}")
        plt.title("Effectif 2D bins ")
        #.figure(figsize=(6,5))
        # plt.imshow(count_grid.T, origin="lower", extent=[x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]],
        #            aspect='auto', cmap='plasma')
        # plt.colorbar(label="Effectif")
        # plt.xlabel("Feature X")
        # plt.ylabel("Feature Y")
        # plt.title("Effectif 2D bins")
        plt.show()

    return x_edges, y_edges, error_grid,count_grid


def analyze_model_bins(df, target_col, features, model, pred_col =None, param_grid=None,model_name = "XGB",
                       feature_bins_1d=None, feature_bins_2d=None, metric = "MAE"):
    """
    MAIN Function
    Args
        df : dataframe
        target_col : str : column to predict
        features : list of str for model training (should include all features_bins_1d and features_bins_2d)
        model : estimator sklearn
        param_grid : dictionnaire paramètres GridSearch
        feature_bins_1d : list of str for the 1d bins
        feature_bins_2d : liste of tuples (col1, col2) for the heatmap
        metric: 'mae','rmse','r2'
    Purpose and returns
        The purpose of the function is  to analyze the errors of calibration regarding the paramaeters of the problem.
        It plots the errors and/or heatmap of errros and effectif and return a dic result
    """
    results = {}
    y_test, y_pred, X_test_df = get_ytest_ypred(df, target_col, features, model, param_grid, pred_col = pred_col)
    results["y_test"] = y_test
    results["y_pred"] = y_pred

    # Bins 1D
    if feature_bins_1d is not None:
        for fx in feature_bins_1d:
            _, mae_bins,count_1d = bin_error_1d(y_test, y_pred, X_test_df[fx].values, bins=5, plot=True, feature_name=fx,metric=metric,model_name=model_name)
            results[f"bin_error_{fx}"] = mae_bins

    # Bins 2D
    if feature_bins_2d is not None:
        for fx, fy in feature_bins_2d:
            _, _, error_grid,count_2d = bin_error_2d(y_test, y_pred, X_test_df[fx].values, X_test_df[fy].values,
                                            bins_x=5, bins_y=5, plot=True, names=(fx, fy),metric=metric,model_name=model_name)
            results[f"bin_error_{fx}_{fy}"] = error_grid

    return results

#%% FFT

def fft_analysis(
    df,
    measure,
    groupby_feat = [],
    window_sizes={"ALL": None},
    k_peaks=3,
    min_freq= None,
    max_freq = None,
    plot=True
):
    """
    MAIN - The function plots the FFT of the measure on all the groups present and return as well a dict of results.
    Args:
        df : pd.dataframe
        measure: str of the column to analyse
        groupby_feat: list of str or []
        window_sizes: {"ALL":None}
        k_peaks : int number of distinct peaks
        min_freq, max_freq : float the minimum and maximum frequency to consider
        plot: bool, to plot the figures
    Returns
        pd.dataframe of FFT features + ID
    """
    
    def fft_features_plot(signal, datetime_index, k=3, min_freq=None, max_freq=None, measure=None, group_dict={}, plot=True):

        """
        Subfunction - Calculation of the FFT and plot
        Args:
            signal : 1D array of the signal 
            datetime_index: 1D array of the datetime of the signal
            k : int number of distinct peaks
            min_freq, max_freq : float the minimum and maximum frequency to consider
            measure : str name of the measure
            group_dict: dict with the values of a group (ID)
            plot: bool, to plot the figures
        Returns:
            dict : features FFT {fft_f1_cph,fft_period1_h, fft_power1, ....} or None if impossible
        """
        
        
        signal = np.asarray(signal)
        if len(signal) < 4:
            return None

        # Mean dt between 2 measures (in h)
        dt_s = np.mean(np.diff(datetime_index).astype("timedelta64[s]").astype(float))
        start = pd.to_datetime(datetime_index[0])
        end   = pd.to_datetime(datetime_index[-1])
    
        
        # FFT
        signal_detrended = signal - np.mean(signal)
        fft_vals = np.fft.rfft(signal_detrended)
        power = np.abs(fft_vals)**2
        freqs = np.fft.rfftfreq(len(signal), d=dt_s)

        # Removal of f=0 (mean component)
        freqs = freqs[1:]
        power = power[1:]
        
        if min_freq is not None:
            mask = freqs >= min_freq
            freqs = freqs[mask]
            power = power[mask]
            
        if max_freq is None:
            max_freq = 1/(2*dt_s)  # Nyquist frequence
            
        mask = freqs <= max_freq
        freqs = freqs[mask]
        power = power[mask]

        if len(power) == 0:
            return None

       # Identification of the peaks
        peaks, _ = find_peaks(power, distance=2) # To add a threshold (per example valid peaks should have at least 10% of the principal peak), add in find peaks height = 0.1*power.max()
        if len(peaks) == 0:
            return None

        peak_powers = power[peaks]
        idx_sorted = peaks[np.argsort(peak_powers)[::-1]]  # sorted by power
        idx_sorted = idx_sorted[:k]

        # Construction of the results dic
        feats = {}
        for i, idx in enumerate(idx_sorted, start=1):
            f = freqs[idx]
            feats[f"fft_f{i}_cph"] = f
            feats[f"fft_period{i}_h"] = 1.0 / f if f > 0 else np.nan
            feats[f"fft_power{i}"] = power[idx]
        
        # Plot of the FFT
        if plot:
            plt.figure(figsize=(10, 4))
            plt.plot(freqs, power, label='FFT power', linewidth=1.5)
            plt.scatter(freqs[idx_sorted], power[idx_sorted], color='red', s=100, zorder=10, label='Top peaks')
            
            # Annotation des pics avec période en heures
            for i, idx in enumerate(idx_sorted, start=1):
                period_h = feats[f'fft_period{i}_h'] / 3600  # Conversion en heures
                plt.text(freqs[idx], power[idx], f"{period_h:.1f}h", 
                         color='red', ha='center', va='bottom', fontweight='bold')
            
            # Construction du titre avec les groupes
            if group_dict:
                group_str = " | ".join([f"{k}={v}" for k, v in group_dict.items()])
            else:
                group_str = "ALL"
            
            plt.xlabel("Frequency (Hz)", fontsize=11)
            plt.ylabel("Power", fontsize=11)
            plt.title(f"FFT Spectrum — {len(signal)} points | {measure}\n" 
                      f"{group_str}\n"
                      f"{start.strftime('%Y-%m-%d %H:%M')} to {end.strftime('%Y-%m-%d %H:%M')}", 
                      fontsize=12)
            plt.legend(loc='best')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.show()

        return feats
    
    # MAIN
    features_all = []
    
    if groupby_feat == []:
        iterable = [("ALL", df)]
    else:
        iterable = df.groupby(groupby_feat)
    
    #Loop on all the groups
    for group, df_grp in iterable: 
        # Construction of a dict for the groups ID
        if groupby_feat == []:
            group_dict = {}
        elif isinstance(groupby_feat, list) and len(groupby_feat) > 1:
            group_dict = dict(zip(groupby_feat, group))
        else:
            group_dict = {groupby_feat[0]: group}
        
        # Extraction of the data
        df_pair = df_grp.sort_values("datetime").reset_index(drop=True)
        signal = df_pair[measure].values
        signal = signal[np.isfinite(signal)]
        
        if len(signal) < 4:
            continue

        times = df_pair["datetime"].values
        
        # Plot 
        feats = fft_features_plot(
            signal, times, 
            k=k_peaks, 
            min_freq=min_freq, 
            max_freq=max_freq, 
            measure=measure, 
            group_dict=group_dict,  
            plot=plot
        )
        
        # Results construction
        if feats is not None:
            feats["window"] = "ALL"
            for key, val in group_dict.items():
                feats[key] = val
            features_all.append(feats)
    
    if len(features_all) == 0:
        print("No FFT features was calculated")
        return None

    return pd.DataFrame(features_all)

#%% Log Linear regression

def log_lin_reg(df_features, target_col, features_rabbit,ordre):
    """ 
    Args:
        df_features : pd.dataframe
        target_col : str 
        features_rabbit : list of str
        ordre = int n° of iterations
    Purpose and returns
        The function aims at finding the coefficients alp of a relation of type target_col = A*(feature[0]**alp0)*(...)*(feature[n]**alpn)
        Returns a list of dic associated (one for each order), with the coefficients and diverses statistics
    """
    
    df_features["target_loop"] = df_features[target_col].values
    coeffs = []

    for i in range(ordre):
        print("Ordre n°",i)
        if i > 0:
            # Construction of the last relation found
            Pr = np.ones(len(df_features))
            for f, c in zip(features_rabbit, coeffs[i-1]["coefs"]):
                Pr *= (df_features[f] ** c)
            Pr *= coeffs[i-1]["biais"]
        else:
            Pr = np.zeros(len(df_features))
        
        # Substraction of P_r to target_loop
        df_features["target_loop"] = df_features["target_loop"] - Pr
        print(df_features["target_loop"])
        
        # Mask for values > 0 after substraction (to avoid powers <1 with negatives)
        mask_0 = (df_features[features_rabbit + ["target_loop"]] > 0).all(axis=1)
        df_loop = df_features[mask_0].copy()
        print(df_loop)
        print("Len df_loops",np.sum(mask_0))
        
        # Adimensionalisation of new data
        mean_feat_loop = df_loop[features_rabbit].mean(axis=0)
        mean_target_loop = df_loop["target_loop"].mean(axis=0)
        df_loop[features_rabbit] = df_loop[features_rabbit] / mean_feat_loop
        df_loop["target_loop"] = df_loop["target_loop"] / mean_target_loop

        # Log-transform of the features 
        df_loop[features_rabbit] = np.log(df_loop[features_rabbit])
        df_loop["target_loop"] = np.log(df_loop["target_loop"])

        # Data preprocessing for regression
        X = df_loop[features_rabbit].values
        y = df_loop["target_loop"].values
        
        mask = np.isfinite(X).all(axis=1) & np.isfinite(y)
        X, y = X[mask], y[mask]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        # LinearRegression
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        

        # Results construction
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        pearson_r, _ = pearsonr(y_test.flatten(), y_pred.flatten())
        biais = model.intercept_
        coefs = model.coef_

        # Stockage des résultats
        coeffs.append({
            "len_group": len(df_loop),
            "features": features_rabbit,
            "R2_test": r2,
            "RMSE_test": rmse,
            "MAE_test": mae,
            "r": pearson_r,
            "biais": biais,
            "coefs": coefs,  # Liste des coefficients
            **{f"c_{f}": c for f, c in zip(features_rabbit, coefs)}
        })
        
        print(coeffs)
        
        return coeffs

#%% Models grid 

models = {
        "Linear": LinearRegression(),
        "XGB": XGBRegressor(objective="reg:squarederror", random_state=42),
        "RFC": RandomForestRegressor(random_state=42),
   }

param_grids = {
    "Linear": {},
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
    },
}



def choose_model_PG(list_model,all_models,all_PG):
    models_C = {}
    PG_C = {}
    for model in list_model:
        if model in all_models and model in all_PG:
            models_C[model] = all_models[model]
            PG_C[model] = all_PG[model]
        else:
            raise ValueError(f"The model {model} is not listed in the dics of all models and/or all_params")
    return models_C, PG_C


#%% Main command
f_bin_error = False #Showing the error (metric to be choosen) function of the parameter (whether on raw data than ML corrected data)
f_tests = False # Some simple statistical tests
f_fft = True # Show the Fourrier transform
f_simple_dt = False # Show a simple DecisionTreeRegressor plot to see parameters that impact the most
f_loglin = False # To do a recursive Linear Regression on log parameters to try to find a power relation between the parameters

list_models = ["Linear","XGB"]
models_choosen, param_grid_choosen = choose_model_PG(list_models,models,param_grids)

file_path = "../1-data/current_df_aligned_ALL.csv"
df = pd.read_csv(file_path, sep=";")

df["datetime"] = pd.to_datetime(df["datetime"])
df["campaign"] = df["datetime"].apply(assign_campaign)
df["innova_point"] = df.apply(assign_innova_point, axis=1)
df["Alezze (cm)"] = df.apply(assign_altezza, axis = 1)
df["colonne"] = df.apply(assign_colonna, axis = 1)
df["hum_range"]=df.apply(assign_humidity,axis=1)
df = df[df["innova_point"] != "no"].copy()


if f_fft:
    
    #mask_period = (df["datetime"] >= pd.Timestamp("2026-01-01")) & (df["datetime"] <= pd.Timestamp("2026-02-01"))
    df_period = (df.copy())#[mask_period]
    df_period = df_period.dropna(subset=["r_NH3"])
    plt.plot([1,2],[1,2])
    plt.show()
    df_fft = fft_analysis(
        df_period,
        measure = "r_NH3",
        groupby_feat = ["campaign",'id_channel'], #,'id_rabbit'],
        window_sizes={"ALL":None},
        k_peaks=5,
        min_freq= 1/(35*3600), # Frequence limited at a maximum of 30h (to limit data loss after)
        max_freq= 0.0001, #for Nyquist frequency use None
        plot=True
    )

    print(df_fft)

if f_simple_dt:
    from sklearn.tree import DecisionTreeRegressor, plot_tree
    
    
    features_X = ["r_NH3", "r_temperature","r_umidity"]
    target_col = ['i_NH3']
    df_signal = df  
    
    # mask_period = (df_signal["datetime"] >= pd.Timestamp("2025-09-18")) & (df_signal["datetime"] <= pd.Timestamp("2025-09-19"))
    
    
    X_tree = df_signal[features_X]
    y_tree = df_signal[target_col[0]]
    
    mask = X_tree.notna().all(axis=1) & y_tree.notna()
    X_tree = X_tree[mask]
    y_tree = y_tree[mask]
    
    
    
    reg = DecisionTreeRegressor(
        max_depth=3,
        min_samples_leaf=5,
        random_state=42
    )
    reg.fit(X_tree, y_tree)
    
    # Visualisation
    plt.figure(figsize=(20,10))
    plot_tree(
        reg,
        feature_names=X_tree.columns,
        filled=True,
        rounded=True
    )
    plt.show()

if f_bin_error:
    features = ["r_NH3","r_CO2","r_temperature","r_umidity","ms_wet_bulb_in", "ms_dew_point_out","ms_wind_speed_in", "ms_wind_dir_in"]
    target_col = "i_NH3"
    
    # 1D bins sur la température
    feature_bins_1d = ["r_temperature","r_umidity"]
    
    # 2D bins sur température et humidité
    feature_bins_2d = [("r_temperature", "r_umidity")]
    
    results = analyze_model_bins(df, target_col, features, model=None, #models["XGB"],
                                 pred_col='r_NH3', param_grid=param_grids["XGB"],model_name="r_NH3",
                                 feature_bins_1d=feature_bins_1d,
                                 feature_bins_2d=feature_bins_2d,metric="MAE")
    
    # y_test et y_pred disponibles
    y_test = results["y_test"]
    y_pred = results["y_pred"]
       


if f_loglin:
    ordre = 20  # Nombre d'itérations
    target_col = ["i_NH3"]
    features_rabbit = ["r_NH3", "r_temperature", "r_umidity","r_THI", "r_CO2"]
    df_features = df[features_rabbit + target_col].copy()
    coeffs = log_lin_reg(df_features, target_col, features_rabbit,ordre)
  
if f_tests:
    X = df["r_NH3"].values
    y = df["i_NH3"].values
    
    mask = np.isfinite(X) & np.isfinite(y)
    X, y = X[mask], y[mask]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42
    )
    
    r2   = r2_score(y_test, X_test)
    rmse = np.sqrt(mean_squared_error(y_test, X_test))
    mae  = mean_absolute_error(y_test, X_test)
   

    

#%% Other (required decomposed file)
plot_wavelet = False
if plot_wavelet:
    df_wavelet =  pd.read_csv("df_signal_decomposition_current.csv", sep=";")
    df_wavelet["datetime"] = pd.to_datetime(df_wavelet["datetime"])
    mask_period = (df_wavelet["datetime"] >= pd.Timestamp("2026-01-01")) & (df_wavelet["datetime"] <= pd.Timestamp("2026-02-01"))
    for (rid,iid), df_r in df_wavelet.groupby(["id_rabbit","id_channel"]):
        mask = mask_period & (df_wavelet["id_rabbit"] == rid) & (df_wavelet["id_channel"] == iid)
        df_mask = df_wavelet[mask]
        plt.figure(figsize=(12,4))
        t= df_mask['datetime']
        
        plt.plot(t,df_mask['r_NH3'], label='r_NH3')
        #plt.plot(t,df_mask['i_NH3'], label='i_NH3')
        plt.plot(t,df_mask['8h_A_energy'], label='8h_A_energy (approx rabbit)')
        plt.plot(t,df_mask['12h_A_energy'], label='12h_A_energy (approx rabbit)')
        plt.plot(t,df_mask['24h_A_energy'], label='24h_A_energy (approx rabbit)')
        plt.title(f"Wavelet analysis | SL {iid} Rabbit {rid}")
        plt.legend()
        plt.show()
        
#%% Other 2 (Complexity)

def compute_distances_sample(X, n_samples=200000):
    n = len(X)

    i = np.random.randint(0, n, n_samples)
    j = np.random.randint(0, n, n_samples)

    mask = i != j
    i, j = i[mask], j[mask]

    dists = np.linalg.norm(X[i] - X[j], axis=1)

    return dists

def entropy_from_distances(dists, bins=50):
    hist, _ = np.histogram(dists, bins=bins, density=True)

    # convertir densité → probas
    p = hist / np.sum(hist)

    # éviter log(0)
    p = p[p > 0]

    entropy = -np.sum(p * np.log(p))

    return entropy

def complexity_entropy(df, features=['NH3i','NH3r','T','H'], n_samples=200000):
    df_clean = df[features].dropna()
    X = StandardScaler().fit_transform(df_clean)
    

    dists = compute_distances_sample(X, n_samples)

    H = entropy_from_distances(dists)
    
    print("Len X",len(X))
    print("Distance entropy:", H)

    return H



def complexity_index_fast(df, features=['NH3i','NH3r','T','H'], n_samples=200000):
    df_clean = df[features].dropna()
    X = StandardScaler().fit_transform(df_clean)
    n = len(X)
    print("N:",n)

    i = np.random.randint(0, n, n_samples)
    j = np.random.randint(0, n, n_samples)

    mask = i != j
    i, j = i[mask], j[mask]

    dists = np.linalg.norm(X[i] - X[j], axis=1)

    # mean_dist = np.mean(dists)
    # complexity = 1 / (1 + mean_dist)

    # return 1-complexity
    return np.std(dists)

def complexity_dot_vectorized(df, features=['NH3i', 'NH3r', 'T', 'H']):
    scaler = StandardScaler()
    df_clean = df[features].dropna()
    X = scaler.fit_transform(df_clean)

    n, d = X.shape

    total = 0.0
    total_abs = 0.0
    count = 0

    for i in range(n):
        print(f"{i}/{n}")

        # Produit scalaire avec TOUTES les lignes restantes d’un coup
        dots = X[i+1:] @ X[i]   # shape (n-i-1,)

        corr = dots / d

        total += corr.sum()
        total_abs += np.abs(corr).sum()
        count += len(corr)

    mean_corr = total / count
    mean_abs_corr = total_abs / count

    print("Complexity Pearson:", mean_corr)
    print("Complexity Pearson Abs:", mean_abs_corr)

    return mean_corr

def complexity_optimized(df, features=['NH3i', 'NH3r', 'T', 'H']):
    """
    Ne calcule chaque corrélation qu'une seule fois
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(df[features])
    
    n_rows = len(X)
    
    # Stocker les corrélations par ligne
    #corr_per_row = [[] for _ in range(n_rows)]
    # Stockage global
    corr_all = []   
    corr_abs_all = []
    # Calculer chaque paire une seule fois
    for i in range(n_rows):
        print(f"{i}/{n_rows}")
        for j in range(i + 1, n_rows):  # i+1 pour éviter doublons et soi-même
            corr, _ = pearsonr(X[i], X[j])
            abs_corr = abs(corr)
            #
            corr_abs_all.append(abs_corr)
            corr_all.append(corr)
            # # Stocker pour les DEUX lignes
            # corr_per_row[i].append(abs_corr)
            # corr_per_row[j].append(abs_corr)
    
    # Calculer la moyenne pour chaque ligne
    #complexity = [np.mean(corrs) for corrs in corr_per_row]
    
    print("Complexity Pearson:", np.mean(corr_all))
    print("Complexity Pearson Abs:", np.mean(corr_abs_all))
    
    return np.mean(corr_all)

#%% Old

def custom_interval_scorer(y_true, y_pred, N=10, liste_coeff=None):
    """
    Scorer basé uniquement sur une liste de coefficients alpha_i fournie par l'utilisateur.
    
    Paramètres :
    - y_true, y_pred : vecteurs numpy de même longueur
    - N : nombre d'intervalles
    - liste_coeff : liste de coefficients alpha_i (longueur N)
    """

    if liste_coeff is None:
        raise ValueError("liste_coeff doit être fourni (longueur = N).")

    liste_coeff = np.asarray(liste_coeff)

    # Vérification stricte
    if len(liste_coeff) != N:
        raise ValueError(
            f"liste_coeff doit contenir {N} coefficients mais en contient {len(liste_coeff)}."
        )

    y_true = np.array(y_true)
    y_pred = np.array(y_pred)

    # Bornes des intervalles basées sur y_true
    y_min, y_max = np.min(y_true), np.max(y_true)
    bins = np.linspace(y_min, y_max, N+1)

    alpha = liste_coeff
    s = 0.0

    for i in range(N):
        mask_true = (y_true >= bins[i]) & (y_true < bins[i+1])
        mask_pred = (y_pred >= bins[i]) & (y_pred < bins[i+1])

        n_true = np.sum(mask_true)
        n_pred = np.sum(mask_pred)

        if n_true > 0:
            s += alpha[i] * abs(n_true - n_pred) / n_true

    return 1 - s


# Scorer sklearn
custom_scorer = make_scorer(custom_interval_scorer, greater_is_better=True)


        