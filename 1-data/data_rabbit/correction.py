# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 10:18:31 2026

@author: titou
"""
import numpy as np
import datetime
import os
import csv
import pandas as pd


df_corrected = pd.read_csv("original_file/rabbit_formated.csv",sep=";")
df_error = pd.read_csv("current_df_rabbit.csv", sep=";")


df_corrected["datetime"] = pd.to_datetime(df_corrected["datetime"])
df_error["datetime"] = pd.to_datetime(df_error["datetime"])

mask_period_corr = (df_corrected["datetime"] >= pd.Timestamp("2025-03-24 16:09:00")) & (df_corrected["datetime"] <= pd.Timestamp("2025-04-19")) 
mask_period_error = (df_error["datetime"] >= pd.Timestamp("2025-03-24 16:09:00")) & (df_error["datetime"] <= pd.Timestamp("2025-04-19")) 

df_corr_fl = df_corrected[mask_period_corr]
df_err_fl = df_error[~mask_period_error]

aligned_df = pd.concat([df_err_fl, df_corr_fl])


aligned_df = aligned_df.sort_values(["date", "id_rabbit", "datetime"]).reset_index(drop=True)
aligned_df["datetime"] = pd.to_datetime(aligned_df["datetime"])
aligned_df["datetime"] = aligned_df["datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")
aligned_df.to_csv("new_rabbit.csv", index=False,sep=";")