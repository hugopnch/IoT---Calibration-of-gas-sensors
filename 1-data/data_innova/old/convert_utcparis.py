# -*- coding: utf-8 -*-
"""
Created on Mon Jan 12 09:49:10 2026

@author: titou
"""
import pandas as pd


df = pd.read_csv("current_df_innova_UTC.csv",sep=";")
df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
df["datetime_paris"] = df["datetime"].dt.tz_convert("Europe/Paris")
df["datetime_paris"] = df["datetime_paris"].dt.tz_localize(None)
df["date_paris"] = df["datetime_paris"].dt.date
df["hour_paris"] = df["datetime_paris"].dt.time
df = df.drop(columns=["datetime", "date", "hour"])
df = df.rename(columns={
    "datetime_paris": "datetime",
    "date_paris": "date",
    "hour_paris": "hour"
})

df.to_csv("current_df_innova_UTCEurope.csv",sep=";",index=False)

