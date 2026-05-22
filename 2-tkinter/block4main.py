# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 10:16:57 2025

@author: titou
"""

from tkinter import LabelFrame, Tk, Label
from block4_simpleplot import Block4SimplePlot
from block4_scorr import Block4SCorr
import numpy as np
import pandas as pd

class Block4Main(LabelFrame):
    def __init__(self, parent):
        super().__init__(parent, text="BLOC 4 : Output")
        self.dataframes_from_bloc3 = {}
        self.type_analysis = None
        self.sync_flag = False
        self.dataframes_aligned = {}
        self.current_subblock = None
        
    
    def update_from_bloc2(self, type_analysis):
        if self.type_analysis is not None and self.type_analysis != type_analysis:
            self.current_subblock.destroy()
            return
        
    def update_from_block3(self, dataframes, type_analysis, sync_flag, nb_interval = None):
        """Met à jour les données reçues du Bloc 3 et crée le Bloc 4 si nécessaire."""
        # self.dataframes_from_bloc3 = dataframes
        self.dataframes_aligned = dataframes
        self.type_analysis = type_analysis
        self.nb_interval = nb_interval
        #self.sync_flag = sync_flag
        
        print(f"[Bloc 4] Données reçues: {list(dataframes.keys())}")
        print(type_analysis)
        print("Keys:")
        print(self.dataframes_aligned["line_1"].keys())

        if not hasattr(self, 'is_created'):
            self.grid(row=0, column=1, rowspan=3, sticky="nsew", padx=10, pady=5)
            self.is_created = True

        self._switch_subblock()

    def _switch_subblock(self):
        """Change de sous-bloc en fonction du type d'analyse."""
        if self.current_subblock is not None:
            self.current_subblock.destroy()

        if self.type_analysis == "plot":
            print(f"SWITCH SUBBLOCK {self.type_analysis}")
            from block4_simpleplot import Block4SimplePlot
            self.current_subblock = Block4SimplePlot(self, self.dataframes_aligned)
        elif self.type_analysis == "s_corr":
            print(f"SWITCH SUBBLOCK {self.type_analysis}")
            from block4_scorr import Block4SCorr
            self.current_subblock = Block4SCorr(self, self.dataframes_aligned)
        elif self.type_analysis == "e_corr":
            print(f"SWITCH SUBBLOCK {self.type_analysis}")
            from block4_ecorr import Block4ECorr
            self.current_subblock = Block4ECorr(self, self.dataframes_aligned,self.nb_interval)
        elif self.type_analysis == "data":
            print(f"SWITCH SUBBLOCK {self.type_analysis}")
            from block4_dataanalysis import Block4DataAnalysis
            self.current_subblock = Block4DataAnalysis(self, self.dataframes_aligned)
        else:
            self.current_subblock = Label(self, text="Sélectionnez une configuration")
            self.current_subblock.pack()

        self.current_subblock.pack(fill="both", expand=True)



   
