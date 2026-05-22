# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 11:56:07 2025

@author: titou
"""
from tkinter import Tk, Label, LabelFrame, StringVar, BooleanVar, Entry, Frame, DISABLED, NORMAL
from tkinter.ttk import Radiobutton, Checkbutton, Combobox, Button

from tkinter.messagebox import showinfo
import pandas as pd


class Block2Analysis(LabelFrame):
    def __init__(self, master, dataframes = None, callback_on_update = None, callback_on_update_bis = None):
        super().__init__(master, text="BLOC 2 : Analysis Type")
        self.grid(sticky="ew", padx=10, pady=5)
        self.callback_on_update = callback_on_update
        self.callback_on_update_bis = callback_on_update_bis
        
        # ---------------- Variables ----------------
        self.analysis_type = StringVar(master=self, value="data")
        self.analysis_date_start = StringVar(master=self, value="2025-09-01")
        self.analysis_hour_start = StringVar(master=self, value="00:00:00")
        self.analysis_date_end = StringVar(master=self, value="2025-09-26")
        self.analysis_hour_end = StringVar(master=self, value="00:00:00")
        
        self.flag_sync_timescale = BooleanVar(master=self, value=False)
        self.sync_timescale_cb = None
        self.flag_threshold_instr = BooleanVar(master=self, value=False)
        self.threshold_instrument_cb = None
        self.flag_isNA = BooleanVar(master=self, value = False)
        self.isNA_cb = None
        self.flag_normalize = BooleanVar(master=self, value=False)
        self.normalize_cb = None
        
        
        #amelioration à prevoir
        self.end_hour_e = None
        self.start_hour_e = None
        self.guided_mode_cb = None
        self.filtre_na_cb = None
        self.break_interpol_threshold_cb_e = None #Pour ne pas interpoller si dt > threshold
        

        # ✅ ajout pour recevoir les dataframes du bloc 1
        self.dataframes = dataframes # raw df from bloc 1
        
        self.dfs_loaded = {} #df non-None
        self.filtered_dfs = {} # df filtered
        self.threshold_instrument_dic = {}
        
        #Button(self, text="Afficher infos", command=self.show_info).grid(row=8, column=0, padx=10, pady=5)
        
        self.create_widgets()

    def create_widgets(self):
        
        # Type analysis
        Label(self, text="Type analysis:", font=("", 10, "underline")).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(5, 5))
        options = [("Data anaysis", "data"),
                   ("Simple plot", "plot"),
                   ("Sensor correlation", "s_corr"),
                   ("Environment correlation", "e_corr")]
        for i, (text, val) in enumerate(options):
            Radiobutton(self, text=text, variable=self.analysis_type, value=val,
                        command=self.update_state_cb_sync).grid(row=1, column=i, padx=5, sticky="w")

        Label(self, text="Data range:", font=("", 10, "underline")).grid(
            row=2, column=0, columnspan=4, sticky="w", pady=(5, 5))
        
        Label(self, text="Start Date (YYYY-MM-DD):").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        Entry(self, textvariable=self.analysis_date_start, width=12).grid(row=3, column=1, sticky="w", padx=5, pady=2)
        Label(self, text="Start Hour (HH:MM:SS):").grid(row=3, column=2, sticky="e", padx=5, pady=2)
        self.start_hour_e =Entry(self, textvariable=self.analysis_hour_start, width=10)
        self.start_hour_e.grid(row=3, column=3, sticky="w", padx=5, pady=2)
        self.start_hour_e.config(state=DISABLED)

        Label(self, text="End Date (YYYY-MM-DD):").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        Entry(self, textvariable=self.analysis_date_end, width=12).grid(row=4, column=1, sticky="w", padx=5, pady=2)
        Label(self, text="End Hour (HH:MM:SS):").grid(row=4, column=2, sticky="e", padx=5, pady=2)
        self.end_hour_e =Entry(self, textvariable=self.analysis_hour_end, width=10)
        self.end_hour_e.grid(row=4, column=3, sticky="w", padx=5, pady=2)
        self.end_hour_e.config(state=DISABLED)

        

        # Other options (put before to create the reference for the command of radiobutton)
        Label(self, text="Filters:", font=("", 10, "underline")).grid(row=5, column=0, columnspan=4, sticky="w", pady=(5, 5))
        
        # Crée d'abord le Checkbutton et stocke la référence
        self.sync_timescale_cb = Checkbutton(self, text="Synchronised timescale", variable=self.flag_sync_timescale,
                                              command=self.update_state_cb_sync)
        # Ensuite, place le Checkbutton dans la grille sinon erreur non référencé
        self.sync_timescale_cb.grid(row=6, column=0, columnspan=1, padx=5, sticky="we")
        
        self.threshold_instrument_cb = Checkbutton(self, text="Threshold instruments", variable=self.flag_threshold_instr)
        self.threshold_instrument_cb.grid(row=6, column=1, columnspan=1, padx=5, sticky="we")
        #self.flag_threshold_instrument_cb.config(state=DISABLED)
        
        self.flag_isNA_cb = Checkbutton(self, text="isNA", variable=self.flag_isNA)
        self.flag_isNA_cb.grid(row=6, column=2, padx=5, sticky="we")
        
        self.normalize_cb = Checkbutton(self, text="Normalize", variable=self.flag_normalize)
        self.normalize_cb.grid(row=6, column=3, padx=5, sticky="we")
        #self.normalize_cb.config(state=DISABLED)
        
        

         # ✅ bouton filtrage
        Button(self, text="Apply configuration", command=self.apply_configuration).grid(row=7, column=0, columnspan=4, pady=(10, 5))
    
    
    
    
    def update_state_cb_sync(self):
        """Met à jour l'état des options en fonction du type d'analyse."""
        print("****** UPDATE_STATE_CB_SYNC ***********")
        
        if self.sync_timescale_cb is None:
            print("Erreur: self.sync_timescale_cb n'est pas initialisé")
            return
        
        if self.analysis_type.get() == "plot":
            self.sync_timescale_cb.config(state=NORMAL)
        elif self.analysis_type.get() == "s_corr":
            self.flag_sync_timescale.set(True)
            self.sync_timescale_cb.config(state=DISABLED)
        elif self.analysis_type.get() == "e_corr":
            self.flag_sync_timescale.set(True)
            self.sync_timescale_cb.config(state=DISABLED)
            self.flag_isNA.set(True)
            self.flag_isNA_cb.config(state=DISABLED)
    
        print("flag_sync_timescale =", self.flag_sync_timescale.get())

            
    def show_info(self):
        print("Bloc 2 contient :", list(self.dataframes.keys()))
    # ---------- liaison depuis Bloc 1 ----------
    
    
    
    # def filter_by_date(self, start_date, end_date, col_date="datetime"):
    #     """Filtrage sur la date (colonne datetime)"""
    #     self.dfs_filtered = {}
        
    #     for k, df in self.dfs_loaded.items():
    #         if col_date in df.columns:
    #             df_filtered = df[(df[col_date] >= start_date) & (df[col_date] <= end_date)]
    #             self.dfs_filtered[k] = df_filtered
    #         else:
    #             self.dfs_filtered[k] = df.copy()  # si pas de colonne datetime, garde tel quel

    #     print("[Bloc 2] DataFrames après filtrage :")
    #     for k,v in self.dfs_filtered.items():
    #         print(f"{k}: {v.shape}")
    #     return self.dfs_filtered
    
    
    # ---------- liaison depuis Bloc 1 ----------
    def update_from_block1(self, dfs_dict):
       """Recevoir les df du bloc 1"""
       self.dataframes = dfs_dict.copy()
       self.dfs_loaded = {k: v for k, v in self.dataframes.items() if v is not None}
       print(f"[Bloc 2] {len(self.dfs_loaded)} DataFrames reçus : {list(self.dfs_loaded.keys())}")
       
    
    def apply_configuration(self):
        if not self.dfs_loaded:
            showinfo("Info", "Aucun DataFrame reçu depuis le Bloc 1.")
            return
    
        try:
            start = pd.to_datetime(self.analysis_date_start.get())
            end = pd.to_datetime(self.analysis_date_end.get())
        except Exception as e:
            showinfo("Erreur", f"Format de date invalide : {e}")
            return
    
        self.filtered_dfs = {}
        for name, df in self.dfs_loaded.items():
            if "datetime" in df.columns:
                df_filtered = df[(df["datetime"] >= start) & (df["datetime"] <= end)]
                self.filtered_dfs[name] = df_filtered
                #print("DF DAT FILTERED:", df_filtered[0:20])
            else:
                self.filtered_dfs[name] = df.copy()
        
        self.threshold_instrument_dic = {
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

    
        showinfo("Configuration appliquée", f"{len(self.filtered_dfs)} DataFrames filtrés.")
    
        # 🔹 Envoi des DF filtrés à Bloc3
        if self.callback_on_update:
            self.callback_on_update(self.filtered_dfs,self.analysis_type.get(),
                                    self.flag_sync_timescale.get(), self.threshold_instrument_dic,
                                    self.flag_threshold_instr.get(), self.flag_isNA.get(),self.flag_normalize.get())
        if self.callback_on_update_bis:
            self.callback_on_update_bis(self.analysis_type.get())
    
    

# Pour test individuel
if __name__ == "__main__":
    root = Tk()
    Block2Analysis(root)
    #root.mainloop()
