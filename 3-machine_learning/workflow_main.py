# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 09:49:12 2026

@author: titou
"""

#%% Packages Importation
import os
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from typing import List, Tuple, Union

import optuna
import optuna.visualization as vis
import seaborn as sns

from sklearn.metrics import make_scorer
from sklearn.model_selection import  GridSearchCV, KFold, GroupKFold,StratifiedShuffleSplit,ShuffleSplit,TimeSeriesSplit
from sklearn.model_selection import train_test_split,cross_val_score,learning_curve, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.base import clone
import warnings


from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from catboost import CatBoostRegressor
import joblib
import json
import networkx as nx

from scipy.stats import pearsonr



#%% Utilitaires pre-processing

# ------------- For NH3 ----------------
def assign_campaign(dt):
    if pd.Timestamp("2025-03-31") <= dt <= pd.Timestamp("2025-05-12"):
        return 'other'#"2025_Apr"
    if pd.Timestamp("2025-06-12") <= dt <= pd.Timestamp("2025-06-25"):
        return "2025_Jun"
    elif pd.Timestamp("2025-09-11") <= dt <= pd.Timestamp("2025-09-25"):
        return "2025_Sep"
    elif pd.Timestamp("2026-01-14") <= dt <= pd.Timestamp("2026-01-22"):
        return 'other'#"2026_Gen"
    else:
        return "other"
    
def assign_innova_point(row):
    camp = row["campaign"]
    rid = row["id_rabbit"]

    if camp == "2025_Apr":
        mapping = {1: "no", 2: "no", 4: "no", 6: "no"}
    elif camp == "2025_Jun":
        mapping = {2: "sl11", 4: "sl5", 1: "sl3", 6: "sl4", 5: "no"}
    elif camp == "2025_Sep":
        mapping = {2: "sl11", 4: "sl5", 6: "sl3", 3: "sl4", 5: "no"}
    elif camp == "2026_Gen":
        mapping = {1: "no", 4: "no", 5: "no", 6: "no"}
    else:
        mapping = {}

    return mapping.get(rid, "no")
    


# ------------- For CO2 ----------------
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

# ------------- For PM2.5 ----------------

def e_time_period(dt):
    if pd.Timestamp("2025-03-13") <= dt <= pd.Timestamp("2025-04-19"):
        return "2025_MarApr"
    elif pd.Timestamp("2025-04-30") <= dt <= pd.Timestamp("2025-05-12"):
        return "2025_May"
    else:
        return "other"


# ------------- General ----------------

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
        return "hum_inf_65"
    elif hum <=75:
        return "hum_between_65_75"
    elif hum<=100:
        return "hum_sup_75"
    else:
        return None






#%% Utilitaires data importation
def import_data_IR():
    if target_col[0] == "i_NH3":
        file_path = "csv_decomposed/innova/df_signal_decomposition_NH3_junesept.csv"
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
        with open("csv_decomposed/innova/features_decomposition_NH3_list_junesept.json", "r") as f:
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
        
    
    
    df["humidity_range"] = df.apply(assign_humidity, axis = 1)
    df["column"] = df.apply(assign_colonna, axis = 1)
    df['height'] = df.apply(assign_altezza, axis = 1)
    
   
        
    return df,dict_features
    


def import_data_ER():
    file_path = "csv_decomposed/envea/df_signal_decomposition_PM2.5_ALL.csv"
    df = pd.read_csv(file_path, sep=";")
    
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["campaign"] = df["datetime"].apply(e_time_period)
    df.sort_values("datetime").reset_index(drop=True)
    
    with open("csv_decomposed/envea/features_decomposition_list_PM2.5_ALL.json", "r") as f:
        dict_features = json.load(f)
    
    return df, dict_features

#%% Personalized external splits,CV Maker and associated sub-functions

def timeseriesplitgroup(X,y,df =None, test_size = 0.3, group_cols = ['campaign','id_rabbit'], 
                        datetime_col = "datetime", n_splits = 1, max_window_hours = 24):
    
    ''' A classical time serie split with the addition of the possibility to use a timeserie split
    on each group (instead of all the data) and the possibility to exclude points between the training and test
    Returns Xtrain and Xtest'''
    
    idxs = group_timeseries_split(
        df=df,
        group_cols = group_cols,
        datetime_col = datetime_col,
        n_splits = n_splits,
        test_size = test_size,
        max_window_hours = max_window_hours
    )
    
    train_idx, test_idx = idxs[0], idxs[1]
    # Split selon le type
    if hasattr(X, 'loc'):  # pandas DataFrame
        X_train, X_test = X.loc[train_idx], X.loc[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
    else:  # numpy array
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
    
    return X_train, X_test, y_train, y_test


def group_timeseries_split(df: pd.DataFrame,group_cols: Union[str, List[str]],datetime_col: str,
                           n_splits: int = 1,test_size: float = 0.2, max_window_hours: float = 5.0
                           ) -> Tuple[pd.Index, pd.Index]:
    """
    Sub-function : Temporal spslit per group with an exclusion window between test and split
    Returns train index and test index
    """
    
    if isinstance(group_cols, str):
        group_cols = [group_cols]
    
    
    window_delta = pd.Timedelta(hours=max_window_hours)
    all_train_idx = []
    all_test_idx = []
    
    # Loop on the groups to define  the splits
    for group_name, group_df in df.groupby(group_cols):
        group_df = group_df.sort_values(datetime_col).copy()
        n_samples = len(group_df)
        test_samples = int(n_samples * test_size)
        train_samples = n_samples - test_samples
        
        # Vérifications
        if n_splits <= 2:
            if train_samples < 1:
                print(f"⚠️  Group {group_name}: not enough train data (skip)")
                continue
        else:
            if train_samples < 1:
                print(f"⚠️  Group {group_name}: not enough train data (skip)")
                continue
        
        # Location of the test
        if n_splits == 1:
            # Test location at the end
            test_start_idx = train_samples
            test_end_idx = n_samples
            test_idx_local = group_df.index[test_start_idx:test_end_idx]
            
            # Test datetime range
            test_start_time = group_df[datetime_col].iloc[test_start_idx]
            
            # Train = beginning until (test_start - window)
            train_mask = group_df[datetime_col] < (test_start_time - window_delta)
            train_idx_local = group_df[train_mask].index
            
        elif n_splits == 2:
            # Test location at the beginning
            test_start_idx = 0
            test_end_idx = test_samples
            test_idx_local = group_df.index[test_start_idx:test_end_idx]
            
            # Test datetime range
            test_end_time = group_df[datetime_col].iloc[test_end_idx - 1]
            
            # Train = from (test_end + window) until the end
            train_mask = group_df[datetime_col] > (test_end_time + window_delta)
            train_idx_local = group_df[train_mask].index
            
        else:
            # Test location center  (n_splits >= 3) with position of centre : linear between end and beginning début et fin |  n=3 center=0.5, n=4  center=0.33, n=5  center=0.66, etc.
            centers_test = [0.5,0.33,0.66]
            if n_splits > 5:
                raise ValueError("n_split > 5 is not supported")
            position = centers_test[n_splits-3]  
            
            center_idx = int(n_samples * position)
            test_start_idx = max(0, center_idx - test_samples // 2)
            test_end_idx = min(n_samples, test_start_idx + test_samples)
            
           
                
            if test_end_idx == n_samples:
                raise ValueError(f"test_end_idx for split n°{n_splits} is out of bound")
            if test_start_idx == 0:
                raise ValueError(f"test_start_idx for split n°{n_splits} is out of bound")
                
    
            
            test_idx_local = group_df.index[test_start_idx:test_end_idx]
            
            # Test datetime range
            test_start_time = group_df[datetime_col].iloc[test_start_idx]
            test_end_time = group_df[datetime_col].iloc[test_end_idx - 1]
            
            # Train = before (test_start - window) or after (test_end + window)
            train_mask = (
                (group_df[datetime_col] < (test_start_time - window_delta)) |
                (group_df[datetime_col] > (test_end_time + window_delta))
            )
            train_idx_local = group_df[train_mask].index
        
        
        if len(train_idx_local) == 0: #Final check
            print(f" Group {group_name}: window is too large, no training index (skip)")
            continue
        
        all_train_idx.extend(train_idx_local.tolist())
        all_test_idx.extend(test_idx_local.tolist())
    
    
    train_idx = pd.Index(all_train_idx) # Conversion in Index pandas
    test_idx = pd.Index(all_test_idx)
    
   
    
    return train_idx, test_idx



class GroupTimeSeriesSplitter:
    """Splitter compatible sklearn for CV"""
    
    def __init__(self, df_full, group_cols, datetime_col, n_splits_list, 
                 test_size=0.2, max_window_hours=5.0):
        
        self.df_full = df_full
        self.group_cols = group_cols
        self.datetime_col = datetime_col
        self.n_splits_list = n_splits_list  # ex: [1, 3, 5]
        self.test_size = test_size
        self.max_window_hours = max_window_hours
        #self.i = 0
    def split(self, X, y=None, groups=None):
        """Split generator"""
        
        
        for n_split in self.n_splits_list:
            train_idx, test_idx = group_timeseries_split(
                self.df_full, 
                self.group_cols,
                self.datetime_col,
                n_splits=n_split,
                test_size=self.test_size,
                max_window_hours=self.max_window_hours
            )
              
            # Convertir en indices numériques
            train_pos = X.index.get_indexer(train_idx)
            test_pos = X.index.get_indexer(test_idx)
            
            if (train_pos < 0).any() or (test_pos < 0).any():
                raise ValueError("Mismatch indexes between df and X_train")
            
            yield train_pos, test_pos
    
    def get_n_splits(self, X=None, y=None, groups=None):
        return len(self.n_splits_list)

def visualize_split(df, train_idx, test_idx, datetime_col, group_col):
    """Subfunction to visualize the repartition of Xtrain and Xtest"""
    import matplotlib.pyplot as plt
    
    s_fixed = 200  # Length of the bars
    fig_width_inches = 15 # width of the figure 
    
    fig, axes = plt.subplots(
        len(df[group_col].drop_duplicates()), 1, 
        figsize=(fig_width_inches, 3 * len(df[group_col].drop_duplicates()))
    )
    
    if len(df[group_col].drop_duplicates()) == 1:
        axes = [axes]
    
    excluded_idx = df.index.difference(train_idx.union(test_idx))
    
    for ax, (group_name, group_df) in zip(axes, df.groupby(group_col)):
       
        width_per_point_inches = fig_width_inches/ len(group_df[datetime_col])
        width_per_point_points = width_per_point_inches * 72 # Convertir in points (1 inch = 72 points)

        
        linewidth = width_per_point_points*0.5   # To avoid superposition *0.5
        
        # Excluded points
        excluded_group = group_df.loc[group_df.index.intersection(excluded_idx)]
        if len(excluded_group)>0:
            ax.scatter(excluded_group[datetime_col], [0] * len(excluded_group), 
                       marker = '|', c='lightgray', s=s_fixed, linewidth=linewidth, label='Excluded')
        
        # Train points
        train_group = group_df.loc[group_df.index.intersection(train_idx)]
        ax.scatter(train_group[datetime_col], [0] * len(train_group), 
                   marker = '|', c='blue', s=s_fixed,linewidth=linewidth, label='Train', alpha=0.8)
        
        # Test points
        test_group = group_df.loc[group_df.index.intersection(test_idx)]
        ax.scatter(test_group[datetime_col], [0] * len(test_group), 
                   marker = '|', c='red', s=s_fixed, linewidth=linewidth, label='Test', alpha=0.8)
        
        # Plot
        ax.set_title(f'Group: {group_name}')
        ax.set_xlabel('Time')
        ax.legend()
        ax.set_yticks([])
    
            
    plt.tight_layout()
    print("\n")
    plt.show()
    return





#%% Utilitaires report function (including gridsearch, learning curve, visualisation of Xtrain/test, clustering, scatter plots, normal plots )

def gridsearch_analysis(data, config_main, config_gridsearch):
    '''This function allow to optimize the hyper parameters of the models 
    as well as creating tables and/or displays to sum-up the most influents 
    parameters of the training'''
     
    def create_results_table(results_top):
        '''Create the results table of the gridsearch part'''
        # Figure creation
        fig, ax = plt.subplots(figsize=(14, 6))
        ax.axis('off')
    
        # Table creation
        df_display = results_top.copy()
        col_rename = {
            "rank_test_score":      "rank",
            "mean_train_score_cv":  "mean_train_cv",
            "mean_test_score_cv":   "mean_test_cv",
            "score_test":           "test",
            "diff_cv_test":         "diff",
            "ratio_test_testcv":    "r_test",
            "ratio_train_testcv":   "r_train",
        }
        df_display = results_top.rename(columns=col_rename)
        numeric_cols = df_display.select_dtypes(include=['float']).columns
        df_display[numeric_cols] = df_display[numeric_cols].round(4) # Rounding the resultsfor more lisibility
        
      
        table = ax.table(
            cellText=df_display.values,
            colLabels=df_display.columns,
            cellLoc='center',
            bbox=[0.03, 0, 1, 1] 
        )
    
        # Style of the table
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5) # Enlarging of the cells
    
        # Application of colors on the ratios that should be controlled
        cols = list(df_display.columns)
        idx_test = cols.index('r_test')
        idx_train = cols.index('r_train')
    
        for i in range(len(df_display)):
            row_idx = i + 1 # +1 because index 0 is the header
            
            val_test = df_display.iloc[i,idx_test]
            val_train = df_display.iloc[i,idx_train]
            
            if not isinstance(val_test, float) or not isinstance(val_train, float):
                continue
            
            if val_test < 0.95:
                table[(row_idx, idx_test)].set_facecolor("#ffcc80") # Orange
            elif val_test > 1.05:
                table[(row_idx, idx_test)].set_facecolor("#c8e6c9") # Light green
    
            # Logique pour ratio_train_testcv
            
            if val_train < 0.95 or val_train > 1.05:
                table[(row_idx, idx_train)].set_facecolor("#ffcdd2") # Light red
    
       
        plt.show()
        plt.close()
        
        return results_top
    

    # Data extract
    df = data["df"]
    id_cols = data["id_cols"]
    df = df.sort_values( id_cols+['datetime']).reset_index(drop=True)
    
    X  = df[data["features_to_use"]]
    y = df[data["target_col"]].values.ravel()
    group_label = data.get("current_group", "ALL")
    
    scorer = config_main["scorer"]
    split_func = config_main["split_func"]
    split_args = config_main.get("split_args", {})
    use_balance = config_main["use_balance"]
    
    
    
    param_grid = config_main["param_grid"]
    model = config_main["model"] 
    scaler = config_main["scaler"]
    
    if scaler != None:
        pipe = Pipeline([
            ("scaler", scaler),
            ("reg",model)
            ])
    else:
        pipe = Pipeline([
            ("reg",model)
            ])
        
    

    # To balance the group weight in test/split if necessary
    if use_balance:
        encode_vals = df[data["feats_to_balance"]].values 
        split = StratifiedShuffleSplit(n_splits=1, test_size=config_main["len_test"], random_state=config_main["random_state"])
        for train_idx, test_idx in split.split(X, encode_vals):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
    else:
        if "df" in split_args:   
            split_args["df"] = df
        X_train, X_test, y_train, y_test = split_func(X, y, **split_args)
        
        # Initialisation of the cross validation with the train_df (necessary for personalized CV, useless but no issues caused for other CV)
        train_mask = df.index.isin(X_train.index)
        df_train_only = df[train_mask].copy()
        cv = config_gridsearch["cv_func"]
        cv.df_full = df_train_only  
        
    print("\n🔍 Distribution y_train vs y_test:")
    print(f"y_train: mean={y_train.mean():.3f}, std={y_train.std():.3f}, min={y_train.min():.3f}, max={y_train.max():.3f}")
    print(f"y_test: mean={y_test.mean():.3f}, std={y_test.std():.3f}, min={y_test.min():.3f}, max={y_test.max():.3f}")
    print("\n")
    
    # Case 1 : model without gridsearch (Lineaar,...)
    if param_grid is None or (not callable(param_grid) and len(param_grid) == 0):
        model_clone = clone(pipe)
        
        for i, (train_idx, test_idx) in enumerate(cv.split(X_train, y_train)):
            y_fold_test = y_train[test_idx]
            y_fold_train = y_train[train_idx]
            print(f"Fold {i} — y_test: mean={y_fold_test.mean():.2f}, std={y_fold_test.std():.2f}, \n"
                  f"y_train: mean={y_fold_train.mean():.2f}, std={y_fold_train.std():.2f} \n")
                
        cv_results = cross_validate(
            model_clone,
            X_train,
            y_train,
            cv=cv,
            scoring=scorer,
            return_train_score=True,
            return_estimator = True,
            n_jobs=1
        )
        
        
        # Post process
        print(f"train scores CV: {cv_results['train_score']} \n")
        print(f"test scores CV: {cv_results['test_score']} \n")
        
        
        mean_train = cv_results["train_score"].mean()
        mean_test = cv_results["test_score"].mean()
        std_test_cv = cv_results["test_score"].std()
        test_preds = []
        for estimator in cv_results['estimator']:
            y_pred = estimator.predict(X_test)
            test_preds.append(r2_score(y_test,y_pred))
        
        val_cv = np.mean(test_preds)
    
        model_clone.fit(X_train, y_train)
        
        if config_gridsearch["save_models"]:
            os.makedirs("quarto/models", exist_ok=True)
            joblib.dump(model_clone,
                        f"quarto/models/best_{config_main['model_name']}_{group_label}.joblib")
        
        model_fit = model_clone
        score_test = model_clone.score(X_test, y_test)
        results_top = pd.DataFrame({
            "rank_test_score":[1],
            "mean_train_score_cv":[mean_train],
            "mean_test_score_cv":[mean_test],
            "std_test_cv": [std_test_cv],
            "test_score_cv": [val_cv],
            "score_test":[score_test],
            
        })
    
        results_top["diff_cv_test"] = results_top["score_test"] - results_top["mean_test_score_cv"]
        results_top["ratio_test_testcv"] = results_top["score_test"] / results_top["mean_test_score_cv"]
        results_top["ratio_train_testcv"] = results_top["mean_train_score_cv"] / results_top["mean_test_score_cv"]
        results_top = results_top.round(4)
        results = results_top
        
        reg = model_clone.named_steps["reg"]
        if hasattr(reg, "coef_"):
            intercept = reg.intercept_
            coefs = reg.coef_
            params_dict = {
                            "intercept": float(np.array(intercept).flatten()[0]),
                            **{f"coef_{f}": float(c) for f, c in zip(X.columns, np.array(coefs).flatten())}
                        }
         
        else:
            params_dict = {}
        
        best_params = {}
        
    else:
        # Classical Gridsearch 
        if config_gridsearch["search_type"] == "sklearn":
            grid_search = GridSearchCV(pipe, param_grid, cv=cv, scoring=scorer, n_jobs=-1, return_train_score=True)
            grid_search.fit(X_train, y_train)
            
            model_fit = grid_search.best_estimator_
            model_fit.fit(X_train,y_train)
            
            # Postprocess
            best_params = grid_search.best_params_
            results = pd.DataFrame(grid_search.cv_results_)
            
            if config_gridsearch["save_models"]:
                os.makedirs("quarto/models", exist_ok=True)
                joblib.dump(model_fit,
                            f"quarto/models/best_{config_main['model_name']}_{group_label}.joblib")
            
            
            results = results.sort_values(by='mean_test_score', ascending=False)
            results = results.rename(columns={
                'mean_train_score': 'mean_train_score_cv',
                'mean_test_score': 'mean_test_score_cv',
                'std_test_score': 'std_test_cv'
            })
            
            results_top = results.head(10).copy()
            results_top = results_top[['params','rank_test_score', 'mean_train_score_cv', 'mean_test_score_cv','std_test_cv']]
            
            # Loop to re-evaluate all the top10 models results on the CV
            val_cv = []
            for param in results_top['params']:
                model_clone = clone(pipe)
                model_clone.set_params(**param)
                cv_results = cross_validate(
                    model_clone, X_train, y_train,
                    cv=cv,
                    scoring=scorer,
                    return_train_score=True,
                    return_estimator=True,
                    n_jobs=1
                )
                test_preds = []
                for estimator in cv_results['estimator']:
                    y_pred = estimator.predict(X_test)
                    test_preds.append(r2_score(y_test,y_pred))
                
                val_cv.append(np.mean(test_preds))
                
            
            results_top['test_score_cv'] = val_cv
            # Loop to re-evaluate all the top10 models results on the test (re trained on all the train)
            test_scores = []
            for param in results_top['params']:
                model_clone = clone(pipe)
                model_clone.set_params(**param)
                model_clone.fit(X_train, y_train)
                test_scores.append(model_clone.score(X_test, y_test))
               
                
            results_top['score_test'] = test_scores
            
            results_top['diff_cv_test'] = results_top['score_test'] - results_top['mean_test_score_cv']
            results_top['ratio_test_testcv'] = results_top['score_test'] / results_top['mean_test_score_cv']
            results_top['ratio_train_testcv'] = results_top['mean_train_score_cv'] / results_top['mean_test_score_cv']
            
            params_dict = dict(zip(results_top['rank_test_score'], results_top['params']))
            results_top = results_top.drop(columns=['params'])
            
            if hasattr(model_fit.named_steps['reg'], 'feature_importances_'):
                feature_importance = pd.DataFrame({
                    'feature': data['features_to_use'],
                    'importance': model_fit.named_steps['reg'].feature_importances_
                }).sort_values('importance', ascending=False)
                
                print(f"\n{'='*20}")
                print(f"TOP Importance FEATURES")
                print(f"{'='*20}")
                print(feature_importance.to_string(index=False))
                print("\n")
            else:
                print("NO Feature importances\n")
            
            
            results_top = results_top.round(4)
            top1_row = results_top.iloc[[0]].copy()
        
        elif config_gridsearch["search_type"] == "optuna":
            # Parametrisation of the Optuna searcher
            objective_func = param_grid
            optuna.logging.set_verbosity(optuna.logging.ERROR)
            
            study = optuna.create_study(
                direction="maximize",  # maximiser le R²
                sampler=optuna.samplers.TPESampler(seed=42)  # algorithme bayésien
            )
            
            # Optimisation
            study.optimize(
                lambda trial: objective_func(trial, X_train, y_train,X_test,y_test, cv, pipe),
                n_trials=75,        
                n_jobs=-1,          
                show_progress_bar=False)
            
            
            trials_df = study.trials_dataframe()

            # Post process of the optimisation
            user_attrs_list = []
            
            for t in study.trials:
                user_attrs_list.append({
                    'mean_train_score_cv': t.user_attrs.get('mean_train_score_cv', np.nan),
                    'mean_test_score_cv': t.user_attrs.get('mean_test_score_cv', np.nan),
                    'std_test_cv': t.user_attrs.get('std_test_cv', np.nan),
                    'test_score_cv': t.user_attrs.get('test_score_cv', np.nan),
                    'penalized_score': t.user_attrs.get('penalized_score', np.nan),
                })
            
            results = pd.concat([trials_df, pd.DataFrame(user_attrs_list)], axis=1)
            
            
            results['rank_test_score'] = results['penalized_score'].rank( 
                ascending=False, method='min'
            ).astype(int) # Ranking on the penalized_score to avoid overfitting
            results = results.sort_values('penalized_score',ascending=False)
            
            
        
            def is_control_param(param_name):
                """Detect whether a  parameter is a control parameter of Optuna (not the model itself)"""
                OPTUNA_CONTROL_PARAMS = ["use_max_depth",  
                                         "n_layers",  
                                         "bootstrap"  
                                        ]
                if param_name in OPTUNA_CONTROL_PARAMS:
                    return True
                if param_name.startswith("n_neurons_layer_"): 
                    return True
                return False
            
            params_list = []
            for idx, row in results.iterrows():
                trial_number = int(row['number'])
                trial = study.trials[trial_number]
                params_with_prefix = {f"reg__{k}": v for k, v in trial.params.items() 
                                      if not is_control_param(k)}  #  Adding of the prefix "reg__" for each hyperparam
                params_list.append(params_with_prefix)
            
            results['params'] = params_list
            
           
            results_top = results.head(10)[[
                'number', 'rank_test_score', 'mean_train_score_cv', 'mean_test_score_cv','test_score_cv','std_test_cv','penalized_score','params'
            ]].copy()  # Selection of the Top 10 results
            
        
            test_scores = []
           
            for param in results_top['params']:
                model_clone = clone(pipe)
                model_clone.set_params(**param)
                model_clone.fit(X_train, y_train)
                test_scores.append(model_clone.score(X_test, y_test))
                
                
                
            
            results_top['score_test'] = test_scores
            results_top['diff_cv_test'] = results_top['score_test'] - results_top['mean_test_score_cv']
            results_top['ratio_test_testcv'] = results_top['score_test'] / results_top['mean_test_score_cv']
            results_top['ratio_train_testcv'] = results_top['mean_train_score_cv'] / results_top['mean_test_score_cv']
            
            
            results_top = results_top.drop(columns=['number'])
            results_top = results_top.round(4)
            
            params_dict = dict(zip(results_top['rank_test_score'], results_top['params'])) # Reconstruction of PARAMS_DICT (as for method == "sklearn")
            results_top = results_top.drop(columns=['params'])
            
            
            best_params = params_dict[1]  
            model_fit = clone(pipe)
            model_fit.set_params(**best_params)
            model_fit.fit(X_train,y_train)
            
            
            if config_gridsearch["save_models"]:
                os.makedirs("quarto/models", exist_ok=True)
                joblib.dump(model_fit,
                            f"quarto/models/best_{config_main['model_name']}_{group_label}.joblib")
            
            if hasattr(model_fit.named_steps['reg'], 'feature_importances_'):
                feature_importance = pd.DataFrame({
                    'feature': data['features_to_use'],
                    'importance': model_fit.named_steps['reg'].feature_importances_
                }).sort_values('importance', ascending=False)
                
                print(f"\n{'='*20}")
                print(f"🎯 TOP Importance FEATURES")
                print(f"{'='*20}")
                print(feature_importance.to_string(index=False))
                print("\n")
            else:
                print("NO Feature importances\n")
            
            # Figures plotting of Optuna search
            fig, ax = plt.subplots(figsize=(10, 5))
            trial_numbers = [t.number for t in study.trials]
            values = [t.value for t in study.trials]
            best_so_far = [max(values[:i+1]) for i in range(len(values))]
            
            # 1. Historic of the optimisation
            ax.plot(trial_numbers, values, 'o-', alpha=0.6, label='Score per trial')
            ax.plot(trial_numbers, best_so_far, 'r-', linewidth=2, label='Best score')
            ax.set_xlabel('Trial')
            ax.set_ylabel('R² Score')
            ax.set_title('Historical of the optimisation')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig('quarto/img_tmp/optuna_history.png', dpi=150, bbox_inches='tight')
            plt.show()
            plt.close()
            
            # 2. Importance of hyperparameters
            from optuna.importance import get_param_importances
            importances = get_param_importances(study)
            important_params = [param for param, imp in importances.items() if imp > 0.05] 
            
            fig, ax = plt.subplots(figsize=(10, 6))
            params = list(importances.keys())
            values = list(importances.values())
            ax.barh(params, values, color='steelblue')
            ax.set_xlabel('Importance')
            ax.set_title('Importance of the hyperparameters')
            ax.grid(True, axis='x', alpha=0.3)
            plt.tight_layout()
            plt.savefig('quarto/img_tmp/optuna_importance.png', dpi=150, bbox_inches='tight')
            plt.show()
            plt.close()
            
            print("Parameters with  >5% of importance :", important_params)
            print("\n")
            
            # 3. Score distribution per hyperparam (equivalent slice)
            for param_name in important_params:
                fig, ax = plt.subplots(figsize=(10, 5))
                param_values = [t.params[param_name] for t in study.trials if param_name in t.params]
                scores = [t.value for t in study.trials if param_name in t.params]
                
                ax.scatter(param_values, scores, alpha=0.6, s=50)
                ax.set_xlabel(param_name)
                ax.set_ylabel('R² Score')
                ax.set_title(f'Impact of {param_name}')
                ax.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig('quarto/img_tmp/optuna_slice_lr.png', dpi=150, bbox_inches='tight')
                plt.show()
                plt.close()
            
            # 4. Creation of a heatmap of the two most important hyper-parameters
            heatmap_data = []
            for trial in study.trials:
                row = {}
                for param in important_params:
                    row[param] = trial.params.get(param, np.nan)  # Récupère la valeur du paramètre
                row["score"] = trial.value  # 
                heatmap_data.append(row)
            
            heatmap_df = pd.DataFrame(heatmap_data)
            
           
            
            for param in important_params:  # Discretisation in 5 bins of the hyper-parameters values (if float)
                if pd.api.types.is_float_dtype(heatmap_df[param]):
                    quantiles = heatmap_df[param].quantile([0, 0.2, 0.4, 0.6, 0.8, 1.0]).values
                    heatmap_df[f"{param}_bin"] = pd.cut(
                        heatmap_df[param],
                        bins=quantiles,
                        labels=[f"[{quantiles[i]:.4f}, {quantiles[i+1]:.4f}]" for i in range(len(quantiles)-1)],
                        include_lowest = True
                        
                    )
                else:  
                    heatmap_df[f"{param}_bin"] = heatmap_df[param].astype(str)
            
           
            
            if len(important_params) >= 2:  # Creation of a pivot table for the heatmap
                x_param = important_params[0]  # Selection of the 2 parameters the most important (>5%)
                y_param = important_params[1] 
            
                
                pivot_table = heatmap_df.pivot_table(
                    index=f"{y_param}_bin",
                    columns=f"{x_param}_bin",
                    values="score",
                    aggfunc="mean"  
                )
            
               
                plt.figure(figsize=(10, 6))
                sns.heatmap(
                    pivot_table,
                    annot=True,
                    fmt=".3f",  # 3 décimales
                    cmap="YlGnBu",  # Palette de couleurs
                    cbar_kws={"label": f"Regularized {scorer} Score"}
                )
                plt.title(f"Score Heatmap with combinaison of {x_param} and {y_param}")
                plt.xlabel(x_param)
                plt.ylabel(y_param)
                plt.tight_layout()
                plt.savefig('quarto/img_tmp/optuna_heatmap.png', dpi=150, bbox_inches='tight')
                plt.show()
                plt.close()
            else:
                print("Not enough parameters >5% of importance to plot a heatmap")


    
    if len(results)>10: # Addition of the worst results in the table results of the gridsearch
        
        results_worst = results.tail(1).copy() # Selection of the worst line
        cols_to_keep = [x for x in results_worst.columns if x in ['params', 'rank_test_score', 'mean_train_score_cv', 'mean_test_score_cv','std_test_cv','test_score_cv','penalized_score']]
        results_worst = results_worst[cols_to_keep]
        
        # Evaluation of the worst model
        model_eval = clone(pipe)
        param = results_worst["params"].iloc[0]
       
        model_eval.set_params(**param)
        model_eval.fit(X_train,y_train) 
        score_test = model_eval.score(X_test,y_test)
        
        
        # Post processing of the worst model
        results_worst['score_test'] = score_test
        results_worst['diff_cv_test'] = results_worst['score_test'] - results_worst['mean_test_score_cv']
        results_worst['ratio_test_testcv'] = results_worst['score_test'] / results_worst['mean_test_score_cv']
        results_worst['ratio_train_testcv'] = results_worst['mean_train_score_cv'] / results_worst['mean_test_score_cv']
        
        
        results_worst = results_worst.drop(columns=['params'])
        results_worst = results_worst.apply(pd.to_numeric, errors='coerce')
        results_worst = results_worst.round(4)
        
        empty_row = pd.DataFrame([['---'] * len(results_top.columns)], 
                                 columns=results_top.columns) # Création of an empty line (for better visualisation)
        
        final_results = pd.concat([results_top, empty_row, results_worst], ignore_index=True)
    
    else:
        final_results = results_top
    
    
    print('\n')
    create_results_table(final_results)        
    top1_row = results_top.iloc[[0]].copy()
    
   
    
    return params_dict, best_params, top1_row, model_fit

def create_learning_curve(data,config_main,config_lc):
    'This function aims at displaying the learning curve of a given model'
    # Data extraction and pipeline initialisation
    df = data["df"]
    id_cols = data["id_cols"]
    df = df.sort_values( id_cols+['datetime']).reset_index(drop=True)
    
    X = df[data["features_to_use"]]
    y = df[data["target_col"]].values.ravel()
    
    
    id_cols = data["id_cols"]
    scorer = config_main["scorer"]
    scorer_name = f"{config_main['scorer']}"
    model = type(config_main["model"])
    scaler = config_main["scaler"]
    split_func = config_main["split_func"]
    split_args = config_main.get("split_args", {})
    best_param = config_main["best_param"]
    
    if best_param:
        best_param_model = {k.replace("reg__", ""): v for k, v in best_param.items()}
    else:
        best_param_model = {} 
    

    if scaler != None:
        best_model = Pipeline([
            ("scaler", scaler),
            ("reg",model(**best_param_model))
            ])
    else:
        best_model = Pipeline([
            ("reg",model(**best_param_model))
            ])
        
    
    test_size = config_main["len_test"]
    
    nb_linspace = config_lc["nb_linspace"]
    #cv_n = config_lc["cv"]
    ref_process = config_lc["ref_process"]
    ref_args = config_lc.get("ref_args", {})
    flag_ref = config_lc["flag_ref"]
    
    if "df" in split_args:
        split_args["df"] = df
    X_train, X_test, y_train, y_test = split_func(X, y, **split_args)
    
    train_mask = df.index.isin(X_train.index)
    df_train_only = df[train_mask].copy()
    cv = config_lc["cv_func"]
    cv.df_full = df_train_only  # Initialisation of the cross validation with the train_df (necessary for personalized CV, useless but no issues caused for other CV)
    
    
    
    
    # Learning curve
    train_sizes, train_scores, val_scores = learning_curve(
        best_model, X_train, y_train,
        cv=cv,
        scoring=scorer,
        train_sizes=np.linspace(0.1, 1.0, nb_linspace),
        n_jobs=-1
    )

    train_mean = train_scores.mean(axis=1)
    val_mean = val_scores.mean(axis=1)

    train_std = train_scores.std(axis=1)
    val_std = val_scores.std(axis=1)
    
    
   
    plt.figure()
    plt.plot(train_sizes, train_mean, label="Training score")
    plt.plot(train_sizes, val_mean, label="Validation score")
    
    plt.fill_between(
        train_sizes,
        train_mean - train_std,
        train_mean + train_std,
        alpha=0.2
    )

    plt.fill_between(
        train_sizes,
        val_mean - val_std,
        val_mean + val_std,
        alpha=0.2
    )

    
    # Baseline to add to the plot if flag activated
    if flag_ref:
        X_ref = df[data["feats_ref"]]
        if config_lc["flag_ref_ml"]:
            ref_model = ref_process(**ref_args)
            baseline_scores = cross_val_score(ref_model,X,y,cv=cv,scoring=scorer)
            baseline_score = baseline_scores.mean()

        else:
            ref_func = ref_process
            baseline_score = ref_func(X_ref, y, **ref_args)

        plt.axhline(
            baseline_score,
            linestyle="--",
            label="Baseline score"
        )

    plt.xlabel("Training size")
    plt.ylabel(f"Score ({scorer_name})")
    plt.title("Learning Curve")
    plt.legend()
    plt.grid()
    plt.show()
   
    return

def stats_model(data, config_main):
    ''' Used for the Data analysis part: basic statistics on the Dataframe '''
    df = data["df"]
    target_col = data["target_col"]
    features_X = data["features_X"]
    feats_to_balance = data["feats_to_balance"]
    feats_grouping = data["feats_grouping"]
    feats_postproc = data["feats_postproc"]
    id_cols = data["id_cols"]
    
    mask = np.isfinite(df[target_col+features_X]).all(axis=1)
    df_clean = df[mask]

    len_test = config_main["len_test"]
    scorer = config_main["scorer"]
    

    metadata = {
        "Nombre de lignes df ": len(df),
        "Nombre de lignes df clean ": len(df_clean),
        "Nombre de features": len(features_X),
        "% de NaN": df.isna().sum().sum() / (len(df) * len(df.columns)) * 100,
        "Taille dataset entraînement": int(len(df_clean) * (1 - len_test)),
        "Taille dataset test": int(len(df_clean) * len_test),
        "Métrique utilisée": scorer,
    }

    table = pd.DataFrame(
        list(metadata.items()),
        columns=["Parameter", "Value"]
    )
    
    list_features = {"Column target": target_col,
                     "Features_X": features_X,
                     "feats_to_balance": feats_to_balance,
                     "feats_grouping": feats_grouping,
                     "feats_postproc": feats_postproc,
                     "feats_ref": feats_reference,
                     "id_cols": id_cols}
    
    if config_main["use_balance"]:
        list_features["Balance group"] = feats_to_balance
    if config_main["use_grouping"]:
        list_features["Grouping"] = feats_grouping
    

    return table, list_features

def create_comparison_table(comparison_rows, use_grouping):
    '''Utilitaire to create the sum-up table at the end of all the gridsearch Analysi (to compare the best results of different models) '''
    # Pre-processing
    df_compare = pd.concat(comparison_rows, ignore_index=True)
    df_compare = df_compare.drop(columns=[c for c in df_compare.columns 
                                          if "rank" in c.lower()], errors='ignore')
    
    
    if use_grouping: # If use_grouping: add a row weighted mean of all the grouping to compare (reconstruction of the dataframe results)
        numeric_cols = df_compare.select_dtypes(include='float').columns
        rows_with_mean = []
        
        for model_name, df_model in df_compare.groupby("model", sort=False):
            rows_with_mean.append(df_model)
            
            mean_row = df_model[numeric_cols].mean().round(3)
            total_len = df_compare["Len total"].sum()
        
          
            weighted_mean_row = pd.Series(index=numeric_cols, dtype=float)   # Initialisation of the weighted mean row
        
           
            for num_col in numeric_cols:  # Calcul of the weighted mean for each numerical column
                weighted_mean_row[num_col] = (df_model[num_col] * df_model["Len total"]).sum() / total_len
            
            mean_row["model"]        = model_name
            mean_row["group"]        = "MEAN weighted"
            mean_row["Len training"] = df_model["Len training"].sum()
            mean_row["Len test"]     = df_model["Len test"].sum()
            mean_row["Len total"]    = df_model["Len total"].sum()
            
            rows_with_mean.append(mean_row.to_frame().T)
        
        df_compare = pd.concat(rows_with_mean, ignore_index=True)
    
    col_rename = {
        "mean_train_score_cv": "mean_train_cv",
        "mean_test_score_cv":  "mean_test_cv",
        "test_score_cv": "test_cv",
        "score_test":          "test",
        "diff_cv_test":        "diff",
        "ratio_test_testcv":   "r_test",
        "ratio_train_testcv":  "r_train",
        'penalized_score': "pen_score"
    }
    df_compare = df_compare.rename(columns=col_rename)
    
    
    float_cols = ["mean_train_cv", "mean_test_cv","std_test_cv",'test_cv', "test", "diff", "r_test", "r_train","penalized_score"]
    for col in float_cols: # Rounding of the values of the table
        if col in df_compare.columns:
            df_compare[col] = pd.to_numeric(df_compare[col], errors='coerce').round(3)

    
    best_mean_idx = None # Localisation of the best MEAN uniquement if grouping
    if use_grouping:
        mask_mean     = df_compare['group'] == "MEAN"
        test_numeric  = pd.to_numeric(df_compare['test'], errors='coerce')
        best_mean_idx = test_numeric[mask_mean].idxmax() if mask_mean.any() else None
        
    
    best_idx = None  #Localisation of the best global results else if no grouping
    if not use_grouping:
        test_numeric = pd.to_numeric(df_compare['test'], errors='coerce')
        best_idx = test_numeric.idxmax()
        
        
    # Creation of the table
    fig, ax = plt.subplots(figsize=(16, max(3, len(df_compare) * 0.5 + 1)))
    ax.axis('off')

    table = ax.table(
        cellText=df_compare.values,
        colLabels=df_compare.columns,
        cellLoc='center',
        bbox=[0.03, 0, 1, 1]
    )
    
    # Style of the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)

    cols      = list(df_compare.columns)
    idx_test  = cols.index('r_test')
    idx_train = cols.index('r_train')

    for i in range(len(df_compare)):
        row_idx = i + 1
        is_mean = use_grouping and str(df_compare.iloc[i].get("group", "")) == "MEAN"

        if is_mean:
            # Gris de base pour toutes les MEAN
            for j in range(len(cols)):
                table[(row_idx, j)].set_facecolor("#e0e0e0")
            # Meilleure MEAN en vert — appliqué en premier, écrasé par orange/rouge si besoin
            if i == best_mean_idx:
                for j in range(len(cols)):
                    table[(row_idx, j)].set_facecolor("#a5d6a7")
        
        if not is_mean and i == best_idx:
            for j in range(len(cols)):
                table[(row_idx, j)].set_facecolor("#a5d6a7")
        # Couleurs r_test / r_train — s'appliquent sur tout (lignes normales ET MEAN)
        try:
            val_test = float(df_compare.iloc[i, idx_test])
            if val_test < 0.95:
                table[(row_idx, idx_test)].set_facecolor("#ffcc80")
            elif val_test > 1.05:
                table[(row_idx, idx_test)].set_facecolor("#c8e6c9")

            val_train = float(df_compare.iloc[i, idx_train])
            if val_train < 0.95 or val_train > 1.05:
                table[(row_idx, idx_train)].set_facecolor("#ffcdd2")
        except (ValueError, TypeError):
            pass

    plt.show()
    plt.close()

def X_train_repartiton(data, config_main, config_gridsearch):
    """ Visualise the repartion of train/test on the  external split and the folds of the internal CV 
    """
    # Data preparation
    df = data["df"]
    id_cols = data["id_cols"]
    df = df.sort_values(id_cols + ['datetime']).reset_index(drop=True)
    
    X = df[data["features_to_use"]]
    y = df[data["target_col"]].values.ravel()
    
    split_func = config_main["split_func"]
    split_args = config_main.get("split_args", {})
    
    # External split
    if "df" in split_args:
        split_args["df"] = df
    X_train, X_test, y_train, y_test = split_func(X, y, **split_args)
    
    
    
    md_title("External Split: X_train vs X_test", level=3)
    print(f"  External Split:")
    print(f"  Train: {len(X_train)} samples")
    print(f"  Test: {len(X_test)} samples")
    
    visualize_split(df, X_train.index, X_test.index, 'datetime', id_cols)
    
    # Internal split (CV folds)
    train_mask = df.index.isin(X_train.index)
    df_train_only = df[train_mask].copy()
    
    cv = config_gridsearch["cv_func"]
    cv.df_full = df_train_only
    if hasattr(cv,"max_window_hours"):
        max_window_hours = cv.max_window_hours
    else:
        max_window_hours = 0
    # ============================================
    # 5. ✅ BOUCLER DIRECTEMENT SUR cv.split()
    # ============================================
    md_title("Internal CV Folds", level=3)
    
    
    for fold_idx, (train_pos, test_pos) in enumerate(cv.split(X_train, y_train)):
        
        print(f"\n Fold {fold_idx + 1}/{cv.get_n_splits()}")

       
        
        # Convertir les positions numériques en Index pandas
        train_idx = X_train.index[train_pos]
        test_idx = X_train.index[test_pos]
        
        # Stats
        print("\n")
        print(f"  Train: {len(train_idx)} samples")
        print(f"  Test: {len(test_idx)} samples")
        print(f"  Excluded: {len(df_train_only) - len(train_idx) - len(test_idx)} samples")
        print(f"  Window exclusion: {max_window_hours}h")
        print("\n")
        # Visualiser
        visualize_split(
            df_train_only, 
            train_idx, 
            test_idx, 
            'datetime', 
            id_cols
        )
    
    return X_train, X_test, y_train, y_test

def scatter_plot(data,config_main,model_fitted):
    'This function aims at displaying the scatter plot results of a given model'
    
    df = data["df"]
    X = df[data["features_to_use"]]
    y_true = df[data["target_col"]].values.ravel()
    
    y_pred = model_fitted.predict(X)

    plt.figure(figsize=(7, 5))
    plt.scatter(y_true, y_pred, alpha=0.3)
    plt.plot([y_true.min(), y_true.max()],
             [y_true.min(), y_true.max()], 'r--', label="perfect prediction")
    plt.xlabel("y_true")
    plt.ylabel("y_pred")
    plt.title("Predicted vs True")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
def scatter_res(data,config_main, model_fitted):
    'This function aims at displaying the residuals scatter plot results of a given model'
    
    df = data["df"]
    X = df[data["features_to_use"]]
    y_true = df[data["target_col"]].values.ravel()
    
    y_pred = model_fitted.predict(X)
    residus = y_true - y_pred
    
    plt.figure(figsize=(7, 5))
    plt.scatter(y_pred, residus, alpha=0.3)
    plt.axhline(0, color='r', linestyle='--')
    plt.xlabel("y_pred")
    plt.ylabel("Residuals")
    plt.title("Residuals vs Predicted")
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    
def corr_clusters(data,config_cluster):
    ''' This function returns a list of  uncorrelated features as well as the list of all clusters
    depending on the mode the data is clustered to check the correlation. 
    It also plot  correlation heatmap of the features'''
    
    def in_corr_clust(df_clust,threshold):
        '''This function take into input a dataframe with a thrshold and 
        returns a list of  uncorrelated features as well as the list of all clusters
        It also plot  correlation heatmap of the features'''
        
        corr = df_clust.corr()
        sns.clustermap(
            corr,
            cmap="coolwarm",
            center=0
        )
        
        
        G = nx.Graph()

        # nodes
        for f in corr.columns:
            G.add_node(f)

        # edges
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                val = corr.iloc[i, j]
                if abs(val) > threshold:
                    G.add_edge(corr.columns[i], corr.columns[j], weight=val)

        clusters = list(nx.connected_components(G))
        uncorrelated_list =  [list(c)[0] for c in clusters]
        
        return clusters, uncorrelated_list
    
    # Data extraction
    df = data["df"]
    features_X = data["features_X"]
    features_base = data["feats_base"]
    features_added = data["feats_added"]
    df_clust = df[features_X]
    threshold = config_cluster["corr_threshold"]
    windows = config_cluster["windows"]
    mode = config_cluster["mode"]
    
    clust_all, uncorr_all =  [x for x in features_base], [x for x in features_base]
    
    # Clustering by mode choosing
    if mode == "all":
        df_clust = [df[features_X]]
        clust_all, uncorr_all = [], []
    elif mode == "by_window":
        df_clust = []
        for i in range(len(windows)):
            feat_window = [x for x in features_added if f'_{windows[i]}_' in x]
            df_window = df[feat_window]
            if len(df_window)>0:
                df_clust.append(df_window)
    elif mode == "feats_add":
        df_clust = [df[features_added]]
    else:
        raise ValueError("The clustering mode is not well defined")
    
  
    for df in df_clust:
        clusters, uncorrelated_list = in_corr_clust(df,threshold)
        clust_all.extend(clusters)
        uncorr_all.extend(uncorrelated_list)

    
    return clust_all, uncorr_all
   
def plot_model(data, config_main, config_plot):
    '''MAIN Function: plot all the figures of the corrected data on different time windows (grouped by id_cols) 
    with possibility to add references plot'''
    
    def add_study_dic(list_models, dic_plot, data, config_main):
        ''' Sub-function : add all the parameters of the studied models inside a dic   '''
        
        if config_main["use_grouping"]:  # ← typo "use_grouping:" corrigée
            # Récupère les valeurs uniques du/des grouping cols
            groups = data["df"][data["feats_grouping"]].drop_duplicates().values
            
            for m in list_models:
                for group in groups:
                    # Convertit proprement le groupe en string
                    group_str = group if isinstance(group, str) else "_".join(map(str, group))
                    
                    key  = f"{m}_{group_str}"
                    path = f"quarto/models/best_{m}_{group_str}.joblib"
                    
                    if os.path.exists(path):
                        dic_plot[key] = {
                            "model_path":   path,
                            "features_list": data["features_to_use"],
                            "label":        f"{m} — {group_str}"
                        }
                    else:
                        print(f"[WARN] modèle introuvable : {path}")
        
        else:
            for m in list_models:
                key  = f"{m}_ALL"
                path = f"quarto/models/best_{m}_ALL.joblib"
                
                if os.path.exists(path):
                    dic_plot[key] = {
                        "model_path":    path,
                        "features_list": data["features_to_use"],
                        "label":         f"{m} " # — ALL"
                    }
                else:
                    print(f"[WARN] modèle introuvable : {path}")
        
        return dic_plot
        
    def _filter_dic(dic_plot, model_name):
        '''Sub-function : filter the global dic according to the model choosen ''' 
        return {k: v for k, v in dic_plot.items() if k.startswith(model_name)}

    def _plot_agg(df, time_col, target_col, label, agg_freq="1h"):   
        '''Sub-function : if the flag agg is True, plot the mean of the agg_freq instead of each point''' 
        # 🔥 sécurisation complète
        if isinstance(target_col, (list, tuple)):
            target_col = target_col[0]
    
        df = df.copy()
        df[time_col] = pd.to_datetime(df[time_col])
        df = df.sort_values(time_col)
        df = df.set_index(time_col)
    
        # 🔥 IMPORTANT : double [] → simple []
        df_mean = df[target_col].resample(agg_freq).mean()
        df_std  = df[target_col].resample(agg_freq).std()
    
        df_agg = pd.concat([df_mean, df_std], axis=1)
        df_agg.columns = ["mean", "std"]
    
        df_agg = df_agg.dropna()   # supprime lignes incohérentes
    
        t = df_agg.index
        y_mean = df_agg["mean"].values
        y_std  = df_agg["std"].values

    
        # Plot
        plt.plot(t, y_mean, label=f"{label} (mean)", linewidth=1.5)
    
        plt.fill_between(
            t,
            y_mean - y_std,
            y_mean + y_std,
            alpha=0.2
        )

    def _plot_one_figure(config_plot, df_rc, dic_filtered, tw_label, idcol_dict, name_model=""):
        '''Sub-function : plot the figure given by the already filtered dataframe ''' 
        
        # Data extraction
        time_col   = "datetime"
        measure, unit  =  config_plot["measurement"],config_plot["unit"]
        target_col = data["target_col"]
        t     = df_rc[time_col]
        X_ref = df_rc[data["feats_ref"]]
        y     = df_rc[target_col]
        start = pd.to_datetime(t.iloc[0])
        end   = pd.to_datetime(t.iloc[-1])
        flag_agg = config_plot["flag_agg"]
        
        if flag_agg:
            agg_freq = config_plot["agg_freq"]
        
        df_rc[time_col] = pd.to_datetime(df_rc[time_col])
        df_rc = df_rc.sort_values(time_col).reset_index(drop=True)
        
        # Plot of the figure
        plt.figure(figsize=(12, 5))
        if flag_agg:
            _plot_agg(df_rc, time_col, target_col, label=f"{measure}", agg_freq=agg_freq)
        else:
            plt.plot(t, df_rc[target_col], label=f"{measure} ", linewidth=1.5)

        if config_plot["ref_column"]:
            if flag_agg:
                _plot_agg(df_rc, time_col, target_col= config_plot["ref_column"], label=config_plot["ref_column"], agg_freq=agg_freq)
            else:
                plt.plot(t, df_rc[config_plot["ref_column"]], label=config_plot["ref_column"])
        if config_plot["ref_func"]:
            y_func = config_plot["ref_func"](X_ref, y, **config_plot["ref_args"])
            if flag_agg:
                df_rc["ref_func"] = y_func
                _plot_agg(df_rc, time_col, target_col= "ref_func", label="ref_func", agg_freq=agg_freq)
            else:
                plt.plot(t, y_func, label="ref func")
        if config_plot["ref_ml"]:
            y_pred = config_plot["ref_ml"].predict(X_ref)
            if flag_agg:
                df_rc["ref_ml"] = y_pred
                _plot_agg(df_rc, time_col, target_col= "ref_ml", label="ref_ml", agg_freq=agg_freq)
            else:
                plt.plot(t, y_pred, label="ref ML")

        for key, dic_key in dic_filtered.items():
            model  = joblib.load(dic_key["model_path"])
            X      = df_rc[dic_key["features_list"]].copy()
            y_pred = model.predict(X)
            
            col_pred = f"pred_{key}"
            df_rc[col_pred] = y_pred
        
            if flag_agg:
                _plot_agg(df_rc, time_col, col_pred, measure + " " + dic_key["label"], agg_freq)
            else:
                plt.plot(t, y_pred, label=measure + " " + dic_key["label"])
            
            
           
            
        plt.xlabel("Time", fontsize = 16)
        plt.ylabel(f"{measure} ({unit})", fontsize = 16)
       
        
        title_str = " | ".join(f"{k}: {v}" for k, v in idcol_dict.items())
        plt.title(f"{measure} | Model : {name_model} | Time window : {tw_label} | {title_str} "
                  f"| {start:%Y-%m-%d} → {end:%Y-%m-%d}",
                  fontsize=16)
                  
        
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()
    
    # MAIN Function
    # Construction of the global dic
    dic_plot = config_plot["dic_plot"]
    dic_plot = add_study_dic(config_plot["list_models"], dic_plot, data, config_main)

    if config_plot["flag_alone"]: # flag_alone : one dic per model
        dics_to_plot = {
            model_name: _filter_dic(dic_plot, model_name)
            for model_name in config_plot["list_models"]
        }
    elif config_plot["flag_compare"]: # flag_compare : one dic with all the models
        dics_to_plot = {"ALL": dic_plot}
    else:
        dics_to_plot = {}

    
    df       = data["df"]
    id_cols  = config_plot["id_cols"]
    time_col = "datetime"

    # Main loop on the groups given by id_cols (one plot per group)
    for keys, df_rc in df.groupby(id_cols):
        
        df_rc = df_rc.sort_values(time_col).reset_index(drop=True)
        keys_dict = dict(zip(id_cols, keys if isinstance(keys, tuple) else (keys,))) # keys is a tuple of the length of id_cols
        title_str = ",".join(f"{k}: {v}" for k, v in keys_dict.items())
        md_title(f"Group: {title_str}", level=3)
        
        if len(df_rc) < 80:
            continue
        
        # Loop on the different time windows to plot for each group
        for tw in config_plot["time_windows"]:
            md_title(f"Time window : {tw}", level=4)
           
            if tw == "ALL":  # Temporal filter
                df_tw    = df_rc.copy()
                tw_label = "ALL"
            else: # End of window taken by default at the end of period
                end_time   = df_rc[time_col].max() # Could change to median    
                start_time = end_time - pd.Timedelta(hours=tw)
                mask_tw = (df_rc[time_col] >= start_time) & (df_rc[time_col] <= end_time)
                df_tw      = df_rc[mask_tw].copy()
                tw_label   = f"{tw}h"
            
            # Loop on all the dics of the plot_dic
            for label, dic_filtered in dics_to_plot.items():    
                if config_main["use_grouping"]: # Last security for the mode use_grouping :plot only if the model group match the group of df_rc
                    group_val = df_rc[data["feats_grouping"]].iloc[0]
                    group_str = group_val if isinstance(group_val, str) else "_".join(map(str, group_val))
                    dic_filtered = {
                        k: v for k, v in dic_filtered.items()
                        if f"_{group_str}" in k
                    }
                    
                    if not dic_filtered:  # ← aucun modèle pour ce groupe, on skip
                        continue
                
                _plot_one_figure(config_plot,df_tw, dic_filtered, tw_label, keys_dict, label)
#%% Utilitaires Markdown Quarto

def md(text):
    print(f"\n{text}\n")

def md_title(text, level=2):
    print(f"\n{'#' * level} {text}\n")

def md_bold(text):
    print(f"**{text}**")


#%%Utilitaires features and model selection

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

def choose_features_eng(features_eng,list_method,list_measure, window_size):
    choosen_feat = []
    if list_method == []:
        raise ValueError("The method list is empty")
    if list_measure == []:
        raise ValueError("The measure list is empty")
    if window_size == []:
        raise ValueError("The window size is empty")
    
    for meas in list_measure:
        for method in list_method:
            label = f'{meas}_{method}'
            feats_label = features_eng[label]
            for hsize in window_size:
                for feat in feats_label:
                    if f"_{hsize}_" in feat:
                        choosen_feat.append(feat)
    return choosen_feat



#%% Models and hyperparameters grids (normal and optuna)

all_models = {
        "Linear": LinearRegression(),
        "Ridge": Ridge(random_state=42),
        "XGB": XGBRegressor(objective="reg:squarederror", random_state=42),
        "RFR": RandomForestRegressor(random_state=42),
        "MLP": MLPRegressor(random_state=42),
        "LGBM": LGBMRegressor(random_state=42, n_jobs=-1, verbose=-1),
        "CatBoost": CatBoostRegressor(random_state=42, verbose=0, thread_count=-1),
    }

all_param_grids = {
    "Linear": {},
        
    "RFR": {
    "reg__n_estimators": [500],
    "reg__max_depth": [3, 4],                
    "reg__min_samples_split": [100, 150],    
    "reg__min_samples_leaf": [30, 50, 70],   
    "reg__max_features": [0.2, 0.3],         
    "reg__max_samples": [0.4, 0.6],          
    },
    
    "XGB": {
    "reg__n_estimators": [500, 700],         
    "reg__max_depth": [1, 2],                
    "reg__learning_rate": [0.005, 0.01],     
    "reg__subsample": [0.4, 0.6],            
    "reg__colsample_bytree": [0.4, 0.6],     
    "reg__colsample_bylevel": [0.5, 0.7],    
    "reg__min_child_weight": [20, 30, 50],   
    "reg__gamma": [5.0, 10.0, 20.0],         
    "reg__reg_lambda": [20.0, 50.0, 100.0],  
    "reg__reg_alpha": [0.5, 1.0, 5.0],       
    }
    
}



def objective_rfr(trial, X_train, y_train, X_test, y_test, cv_func, pipe_base):
    from sklearn.base import clone
    from sklearn.model_selection import cross_validate
    
    
    
    
    use_max_depth = trial.suggest_categorical("use_max_depth", [True, False])
    if use_max_depth:
        
        max_depth = trial.suggest_int("max_depth", 3, 15)
    else:
        max_depth = None

    
    params = {
        "reg__n_estimators": trial.suggest_int("n_estimators", 200, 500, step=50),  
        "reg__max_depth": max_depth,
        "reg__min_samples_split": trial.suggest_int("min_samples_split", 10, 50, step=5),  
        "reg__min_samples_leaf": trial.suggest_int("min_samples_leaf", 4, 20, step=2),  
        "reg__max_features": trial.suggest_float("max_features", 0.2, 0.5),  
        "reg__max_samples": trial.suggest_float("max_samples", 0.5, 0.8),  
        "reg__min_impurity_decrease": trial.suggest_float("min_impurity_decrease", 0.002, 0.02, log=True),  
        "reg__bootstrap": True,  
        "reg__ccp_alpha": trial.suggest_float("ccp_alpha", 0.001, 0.05, log=True), 
        "reg__min_weight_fraction_leaf": trial.suggest_float("min_weight_fraction_leaf", 0.0, 0.1), 
    }
    
    pipe = clone(pipe_base)
    pipe.set_params(**params)
    
    cv_results = cross_validate(
        pipe, X_train, y_train,
        cv=cv_func,
        scoring='r2',
        return_train_score=True,
        return_estimator=True,
        n_jobs=1
    )
    
    
    test_preds = []
    for estimator in cv_results['estimator']:
        y_pred = estimator.predict(X_test)
        test_preds.append(r2_score(y_test,y_pred))
        
    
    mean_train_cv = cv_results['train_score'].mean()
    mean_val_cv = cv_results['test_score'].mean()
    std_cv = cv_results['test_score'].std()
    val_cv = np.mean(test_preds)
    
    trial.set_user_attr("mean_train_score_cv", mean_train_cv)
    trial.set_user_attr("mean_test_score_cv", mean_val_cv)
    trial.set_user_attr("std_test_cv", std_cv)
    trial.set_user_attr("test_score_cv", val_cv)
    
    
    
    overfit_gap = mean_train_cv - mean_val_cv
    lambda_penalty = 5  
    
    if mean_train_cv/mean_val_cv > 1.05 and mean_val_cv >0.05 :
        penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)
    else:
        penalized_score = mean_val_cv
        
    trial.set_user_attr("penalized_score", penalized_score)
    
    return penalized_score 


def objective_xgb(trial, X_train, y_train,X_test,y_test, cv_func, pipe_base):
    from sklearn.base import clone
    from sklearn.model_selection import cross_validate
    
    
    
    params = {
      "reg__n_estimators": trial.suggest_int("n_estimators", 300, 800, step=100), 
      "reg__max_depth": trial.suggest_int("max_depth", 2, 4),  
      "reg__learning_rate": trial.suggest_float("learning_rate", 0.005, 0.03, log=True),  
      "reg__subsample": trial.suggest_float("subsample", 0.4, 0.7),  
      "reg__colsample_bytree": trial.suggest_float("colsample_bytree", 0.4, 0.7),  
      "reg__colsample_bylevel": trial.suggest_float("colsample_bylevel", 0.4, 0.7), 
      "reg__colsample_bynode": trial.suggest_float("colsample_bynode", 0.4, 0.7), 
      "reg__min_child_weight": trial.suggest_int("min_child_weight", 30, 100, step=10),  
      "reg__gamma": trial.suggest_float("gamma", 5, 20),  
      "reg__reg_lambda": trial.suggest_float("reg_lambda", 10, 100),  
      "reg__reg_alpha": trial.suggest_float("reg_alpha", 2, 20), 
      "reg__max_delta_step": trial.suggest_int("max_delta_step", 0, 5),  
  }
       
    pipe = clone(pipe_base)
    pipe.set_params(**params)
    
    cv_results = cross_validate(
        pipe, X_train, y_train,
        cv=cv_func,
        scoring='r2',
        return_train_score=True,
        return_estimator=True,
        n_jobs=1
    )
    
    test_preds = []
    for estimator in cv_results['estimator']:
        y_pred = estimator.predict(X_test)
        test_preds.append(r2_score(y_test,y_pred))
    

    mean_train_cv = cv_results['train_score'].mean()
    mean_val_cv = cv_results['test_score'].mean()
    std_cv = cv_results['test_score'].std()
    val_cv = np.mean(test_preds)
    
    trial.set_user_attr("mean_train_score_cv", mean_train_cv)
    trial.set_user_attr("mean_test_score_cv", mean_val_cv)
    trial.set_user_attr("std_test_cv", std_cv)
    trial.set_user_attr("test_score_cv", val_cv)
    
    overfit_gap = mean_train_cv - mean_val_cv
    lambda_penalty = 5  
    penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)
    
    if mean_train_cv/mean_val_cv > 1.05 and mean_val_cv >0.05 :
        penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)
    else:
        penalized_score = mean_val_cv
    
    trial.set_user_attr("penalized_score", penalized_score)
    
    return penalized_score 


def objective_mlp(trial, X_train, y_train,X_test,y_test, cv_func, pipe_base):
    from sklearn.base import clone
    from sklearn.model_selection import cross_validate
    
    n_layers = trial.suggest_int("n_layers", 1, 3)      
    hidden_layer_sizes = []
    for i in range(n_layers):
        n_neurons = trial.suggest_int(f"n_neurons_layer_{i}", 8, 64, step=8)
        hidden_layer_sizes.append(n_neurons)
    
    params = {
        "reg__hidden_layer_sizes": tuple(hidden_layer_sizes),
        "reg__activation": trial.suggest_categorical("activation", ["relu", "tanh"]),
        "reg__alpha": trial.suggest_float("alpha", 0.0001, 10, log=True),  
        "reg__learning_rate_init": trial.suggest_float("learning_rate_init", 0.0001, 0.01, log=True),
        "reg__batch_size": trial.suggest_categorical("batch_size", [32, 64, 128]),
        "reg__max_iter": 500,  
        "reg__early_stopping": True,  
        "reg__validation_fraction": 0.15,  
        "reg__n_iter_no_change": 20,  
        "reg__solver": "adam",  
        "reg__random_state": 42,
    }
  

    pipe = clone(pipe_base)
    pipe.set_params(**params)
    
    cv_results = cross_validate(
        pipe, X_train, y_train,
        cv=cv_func,
        scoring='r2',
        return_train_score=True,
        return_estimator=True,
        n_jobs=1
    )
    
    test_preds = []
    for estimator in cv_results['estimator']:
        y_pred = estimator.predict(X_test)
        test_preds.append(r2_score(y_test,y_pred))
    

    mean_train_cv = cv_results['train_score'].mean()
    mean_val_cv = cv_results['test_score'].mean()
    std_cv = cv_results['test_score'].std()
    val_cv = np.mean(test_preds)
    
    
    
    trial.set_user_attr("mean_train_score_cv", mean_train_cv)
    trial.set_user_attr("mean_test_score_cv", mean_val_cv)
    trial.set_user_attr("std_test_cv", std_cv)
    trial.set_user_attr("test_score_cv", val_cv)
    
    
    
    overfit_gap = mean_train_cv - mean_val_cv
    lambda_penalty = 5 
    penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)

    if mean_train_cv/mean_val_cv > 1.05 and mean_val_cv >0.05 :
        penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)
    else:
        penalized_score = mean_val_cv
    
    trial.set_user_attr("penalized_score", penalized_score)
    
    return penalized_score 

def objective_catboost(trial, X_train, y_train,X_test,y_test, cv_func, pipe_base):
    from sklearn.base import clone
    from sklearn.model_selection import cross_validate
    
    
    
    params = {
    "reg__iterations": trial.suggest_int("iterations", 200, 1000, step=100),
    "reg__depth": trial.suggest_int("depth", 3, 8),
    "reg__learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
    "reg__l2_leaf_reg": trial.suggest_float("l2_leaf_reg", 1, 50),  
    "reg__bagging_temperature": trial.suggest_float("bagging_temperature", 0, 5),  
    "reg__random_strength": trial.suggest_float("random_strength", 0, 5),  
    "reg__subsample": trial.suggest_float("subsample", 0.5, 0.9),
    "reg__min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 10, 50),
    "reg__leaf_estimation_iterations": trial.suggest_int("leaf_estimation_iterations", 1, 10),  
    "reg__verbose": 0,  
    "reg__rsm": trial.suggest_float("rsm", 0.5, 0.9),  
    "reg__border_count": trial.suggest_int("border_count", 32, 128),  
    "reg__leaf_estimation_method": trial.suggest_categorical("leaf_estimation_method", ["Newton", "Gradient"]), 
    "reg__boosting_type": trial.suggest_categorical("boosting_type", ["Ordered", "Plain"]),  
    "reg__max_ctr_complexity": trial.suggest_int("max_ctr_complexity", 1, 4),  
    "reg__diffusion_temperature": trial.suggest_float("diffusion_temperature", 0, 10000),  
}
  
    
   
    
    pipe = clone(pipe_base)
    pipe.set_params(**params)
    
    cv_results = cross_validate(
        pipe, X_train, y_train,
        cv=cv_func,
        scoring='r2',
        return_train_score=True,
        return_estimator=True,
        n_jobs=1
    )
    
    
    
    
    test_preds = []
    for estimator in cv_results['estimator']:
        y_pred = estimator.predict(X_test)
        test_preds.append(r2_score(y_test,y_pred))
    

    mean_train_cv = cv_results['train_score'].mean()
    mean_val_cv = cv_results['test_score'].mean()
    std_cv = cv_results['test_score'].std()
    val_cv = np.mean(test_preds)
    
    
    
    trial.set_user_attr("mean_train_score_cv", mean_train_cv)
    trial.set_user_attr("mean_test_score_cv", mean_val_cv)
    trial.set_user_attr("std_test_cv", std_cv)
    trial.set_user_attr("test_score_cv", val_cv)
    
    
    
    overfit_gap = np.abs(mean_train_cv - mean_val_cv)
    lambda_penalty = 5 
    penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)
    
    if (mean_train_cv/mean_val_cv > 1.05 or mean_train_cv/mean_val_cv < 0.95) and mean_val_cv >0.05 :
        penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)
    else:
        penalized_score = mean_val_cv
    
    trial.set_user_attr("penalized_score", penalized_score)
    
    return penalized_score 


def objective_lgbm(trial, X_train, y_train,X_test,y_test, cv_func, pipe_base):
    from sklearn.base import clone
    from sklearn.model_selection import cross_validate
    
    
    
    params = {
        "reg__n_estimators": trial.suggest_int("n_estimators", 200, 800, step=100),
        "reg__max_depth": trial.suggest_int("max_depth", 3, 8),  
        "reg__learning_rate": trial.suggest_float("learning_rate", 0.01, 0.1, log=True),
        "reg__num_leaves": trial.suggest_int("num_leaves", 15, 63),  
        "reg__subsample": trial.suggest_float("subsample", 0.5, 0.9),
        "reg__colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 0.9),
        "reg__min_child_samples": trial.suggest_int("min_child_samples", 10, 50),  
        "reg__reg_alpha": trial.suggest_float("reg_alpha", 0, 10),  
        "reg__reg_lambda": trial.suggest_float("reg_lambda", 0, 50),  
        "reg__min_split_gain": trial.suggest_float("min_split_gain", 0, 5),  
        "reg__path_smooth": trial.suggest_float("path_smooth", 0, 5),  
        "reg__min_child_weight": trial.suggest_float("min_child_weight", 0.001, 10, log=True),  
        "reg__feature_fraction": trial.suggest_float("feature_fraction", 0.5, 0.9),  
        "reg__bagging_fraction": trial.suggest_float("bagging_fraction", 0.5, 0.9),  
        "reg__bagging_freq": trial.suggest_int("bagging_freq", 1, 7),  
        "reg__max_bin": trial.suggest_int("max_bin", 63, 255),  
        "reg__min_data_per_group": trial.suggest_int("min_data_per_group", 50, 200),  
    }
    
    
    pipe = clone(pipe_base)
    pipe.set_params(**params)
    
    cv_results = cross_validate(
        pipe, X_train, y_train,
        cv=cv_func,
        scoring='r2',
        return_train_score=True,
        return_estimator=True,
        n_jobs=1
    )
    
    
    test_preds = []
    for estimator in cv_results['estimator']:
        y_pred = estimator.predict(X_test)
        test_preds.append(r2_score(y_test,y_pred))
    

    mean_train_cv = cv_results['train_score'].mean()
    mean_val_cv = cv_results['test_score'].mean()
    std_cv = cv_results['test_score'].std()
    val_cv = np.mean(test_preds)
    
    trial.set_user_attr("mean_train_score_cv", mean_train_cv)
    trial.set_user_attr("mean_test_score_cv", mean_val_cv)
    trial.set_user_attr("std_test_cv", std_cv)
    trial.set_user_attr("test_score_cv", val_cv)
    
    
    
    overfit_gap = np.abs(mean_train_cv - mean_val_cv)
    lambda_penalty = 5  
    penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)
      
    if (mean_train_cv/mean_val_cv > 1.05 or mean_train_cv/mean_val_cv < 0.95)  and mean_val_cv >0.05 :
        penalized_score = mean_val_cv - lambda_penalty * max(0, overfit_gap)
    else:
        penalized_score = mean_val_cv
    
    trial.set_user_attr("penalized_score", penalized_score)
    
    return penalized_score 




all_param_optuna = {
    "Linear": {},
    "RFR": objective_rfr,
    "XGB": objective_xgb,
    "MLP": objective_mlp,
    "CatBoost": objective_catboost,
    "LGBM": objective_lgbm,
    }

#%% Utilitaires QUARTO

def build_df(data):
    if flag_IR:
        df, features_engineered = import_data_IR()

    if flag_ER:
        df, features_engineered = import_data_ER()
        

    cols_to_check = target_col + features_X # Removing of the columns where there is more than 15% of nan
    nan_ratio = df[cols_to_check].isna().mean()
    valid_features = nan_ratio[nan_ratio <= 0.15].index 
    valid_features_list = list(valid_features)
    
    mask = np.isfinite(df[valid_features]).all(axis=1) # Removing of last np.nan
    df = df[mask]

        
    cols = list(dict.fromkeys(valid_features_list + # Choosing of all the cols usefull for the mai  workflow
                              feats_to_balance + feats_grouping +
                              feats_reference+ feats_postproc))
    df = df[cols]
    
    new_feats_X = [x for x in features_X if x in valid_features_list]
    new_feats_add = [x for x in feats_eng if x in valid_features_list]
    
    data["df"]=df
    data["features_X"] = new_feats_X
    data["feats_added"] = new_feats_add
    
    column_removed = [x for x in cols_to_check if x not in valid_features_list]
    print(f'Column removed because np.isnan > 15%: {column_removed}')
    
    return data

def build_config():
    len_test = 0.3
    rd_state = 42
    excl_window = 0
   
    
    data = {
        "df": None,
        "target_col": target_col,
        "feats_base": feats_base,
        "feats_added": feats_eng,
        "features_X": features_X,
        "features_to_use": None,
        "feats_to_balance": feats_to_balance,
        "feats_grouping": feats_grouping,
        "feats_postproc": feats_postproc,
        "feats_ref": feats_reference,
        "id_cols": id_cols
    }
    
    
    config_main = {
        "model_name": None,
        "model": None,
        "param_grid": None,
        "best_param": None,
        "len_test": len_test,
        "use_grouping": False,
        "use_balance": False,
        "split_func": timeseriesplitgroup,#train_test_split,#timeseriesplitgroup# #, for use_balance = True StratifiedShuffleSplit()
        "split_args": {'df': None,'test_size' : len_test, 'group_cols' : id_cols, 
                       'datetime_col' : "datetime", 'n_splits' : 1, 'max_window_hours' : excl_window},#{"test_size":len_test,"random_state":rd_state}, # for use_balance = True {n_splits=1, test_size=config_main["len_test"], random_state=config_main["random_state"]}
                      #{"test_size":len_test,"random_state":rd_state},
        "scaler": StandardScaler(),
        "scorer": "r2",
        "scorer_args": None,
        "random_state": rd_state
    }

    config_cluster = {
        "show":True, 
        "corr_threshold":0.8,
        "mode":  "by_window", #["all", "by_window","feats_add"]
        "windows": window_size if flag_eng else []
        }
    
    config_gridsearch = {
        "show":True, 
        "search_type": "optuna",
        "model_name": None,
        "model": None,
        "param_grid": None,
        "best_param": None,
        "cv_func":#GroupTimeSeriesSplitter(df_full = None,
                                           # group_cols=id_cols,
                                           # datetime_col='datetime',
                                           # n_splits_list=[1,2,3,4,5],  # 3 folds: fin,début, centre
                                           # test_size=len_test,
                                           # max_window_hours=excl_window),
                                          ShuffleSplit(n_splits=5,test_size=len_test,random_state=rd_state), #KFold(n_splits=5, shuffle=True, random_state=rd_state), #
        "save_models": True,
        "sumup-table": True
        } 
    
    config_lc = {
        "show": True,
        "nb_linspace":20,
        "cv_func": #GroupTimeSeriesSplitter(df_full = None,
                                           # group_cols= id_cols,
                                           # datetime_col='datetime',
                                           # n_splits_list=[1,2,3,4,5],   # 3 folds: fin, centre, 2/3
                                           # test_size=len_test,
                                           # max_window_hours=excl_window),
                                           ShuffleSplit(n_splits=5,test_size=len_test,random_state=rd_state), #KFold(n_splits=5, shuffle=True, random_state=rd_state),
        "flag_ref":False,
        "flag_ref_as_ml":False,
        "ref_process":None,
        "ref_args":None
    }
    
    config_scatter = {
        "show": True,
        "show_res": True
        }
    
    config_plot = {
        "show":True,
        "measurement": measurement,
        "unit": unit,
        "list_models": list_models,
        "dic_plot": {},
        "id_cols":  id_cols_postproc,
        "time_windows": [24,48,"ALL"], # To expend more or less the plot : in hour, ALL for all the period
        "flag_compare": True, # To plot all models of the study + ref on one figure
        "flag_alone": True, # To plot plot one model of the study+ ref on one figure
        "ref_column": ref_column,
        "ref_func":None,
        "ref_args":None,
        "ref_ml": None, #joblib.load(path)
        "flag_agg": False,
        "agg_freq": "1h", #"30min", "1D"
        } 
    
    if flag_eng == False:
        config_cluster["show"] = False

    return data, config_main, config_cluster, config_lc, config_gridsearch, config_scatter, config_plot







#%% Command of controls for Quarto report

# Model choosing
list_models = ["LGBM"] #,"CatBoost"] 
models_choosen, param_grid_choosen = choose_model_PG(list_models,all_models,all_param_optuna)#param_grids_old)#all_param_grids)#all_param_optuna
# =======================
# Data import and maskf
flag_IR = True # Innova
flag_ER = False # Envea
flag_eng = False # Features engineered

# Features choosing
feats_reference = []
feats_to_balance = [] 
feats_grouping = [] 

if flag_IR:
    target_col = ["i_NH3"]
    feats_base = ["r_NH3", "r_temperature","r_umidity","r_CO2","r_THI"] 
    feats_postproc = ["datetime","id_channel","id_rabbit","campaign"]
    id_cols = ['campaign'] #["campaign","id_rabbit"]#, "id_channel"] # Groupby for split/CV 
    id_cols_postproc = ["campaign","id_rabbit","id_channel"]
    ref_column = ["r_NH3"]
    measurement,unit ="NH3", "ppm"
if flag_ER:
    target_col = ["e_PM_2.5"]
    feats_base = ["r_PM_2.5", "r_temperature","r_umidity"]
    feats_postproc = ["datetime","id_rabbit","campaign"]
    id_cols = ["campaign"] #,"id_rabbit"]#["campaign","id_rabbit"]
    ref_column = ["r_PM_2.5"]
    measurement,unit ="PM 2.5", "µg/m3"

if flag_eng:
    methods = ["wavelet"] #"stats","wavelet" #,"fft"
    window_size = ["2h","8h"]#["8h","12h","24h"]#"3h","8h","12h","24h"
    if flag_IR:
        _,features_engineered = import_data_IR()
        feats_decomp = ["r_NH3", "r_temperature","r_umidity"]
    if flag_ER:
        _,features_engineered = import_data_ER()
        feats_decomp = ["r_PM_2.5", "r_temperature","r_umidity"]
    feats_eng = choose_features_eng(features_engineered,methods, feats_decomp, window_size)
else:
    feats_eng = []
features_X = feats_base+feats_eng

warnings.filterwarnings("ignore", message="X does not have valid feature names, but LGBMRegressor was fitted with feature names")












