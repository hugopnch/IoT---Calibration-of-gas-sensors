# -*- coding: utf-8 -*-
"""
Created on Mon Oct 13 16:27:33 2025

@author: titou
"""

# block3.py
import importlib
from tkinter import BooleanVar, IntVar, Spinbox, Frame, Tk, StringVar,DoubleVar, Label, LabelFrame, Entry 
from tkinter.ttk import Button, Checkbutton, Combobox, Entry , Radiobutton
from tkinter.messagebox import showinfo
import numpy as np
import pandas as pd


class Block3Main(LabelFrame):
    def __init__(self, parent, callback_on_update = None):
        super().__init__(parent, text="BLOC 3 : Parameters")
        self.parent = parent
        self.callback_on_update = callback_on_update
        self.dataframes_from_bloc2 = {}
        self.type_analysis = None
        self.current_subblock = None  # Référence au sous-bloc actuel

    def update_from_block2(self, dataframes, type_analysis, flag_sync_timescale,threshold_instrument_dic,flag_threshold_instr,flag_isNA,flag_normalize):
        self.dataframes_from_bloc2 = dataframes
        self.type_analysis = type_analysis
        self.flag_sync_timescale = flag_sync_timescale
        self.flag_threshold_instr = flag_threshold_instr
        self.threshold_instr_dic = threshold_instrument_dic
        self.flag_isNA = flag_isNA
        self.flag_normalize = flag_normalize
        print("FLAG sync timescale:", flag_sync_timescale)
        print("FLAG threshold inst:", flag_threshold_instr)
        print("FLAG threshold inst:", threshold_instrument_dic)
        print("FLAG is NA:", flag_isNA)
        self._switch_subblock()

    def _switch_subblock(self):
        # 1. Détruire le sous-bloc actuel s'il existe
        if self.current_subblock is not None:
            self.current_subblock.destroy()

        # 2. Créer le nouveau sous-bloc en fonction du type d'analyse
        if self.type_analysis == "plot":
            from block3_simpleplot import Block3SimplePlot  # Import local
            self.current_subblock = Block3SimplePlot(self,self.dataframes_from_bloc2,self.type_analysis,
                                                     self.flag_sync_timescale,self.threshold_instr_dic, 
                                                     self.flag_threshold_instr,self.flag_isNA,self.flag_normalize,
                                                     self.callback_on_update)
        elif self.type_analysis == "s_corr":
            from block3_sensorcorrelation import Block3SCorr
            self.current_subblock = Block3SCorr(self, self.dataframes_from_bloc2,self.type_analysis,
                                                self.flag_sync_timescale,self.threshold_instr_dic, 
                                                self.flag_threshold_instr,self.flag_isNA, self.flag_normalize,
                                                self.callback_on_update)
        elif self.type_analysis == "e_corr":
            from block3_envtcorrelation import Block3ECorr
            self.current_subblock = Block3ECorr(self, self.dataframes_from_bloc2,self.type_analysis,
                                                self.flag_sync_timescale,self.threshold_instr_dic, 
                                                self.flag_threshold_instr,self.flag_isNA, self.flag_normalize,
                                                self.callback_on_update)
            
        elif self.type_analysis == "data":
            from block3_dataanalysis import Block3DataAnalysis
            self.current_subblock = Block3DataAnalysis(self, self.dataframes_from_bloc2,self.type_analysis,
                                                self.flag_sync_timescale,self.threshold_instr_dic, 
                                                self.flag_threshold_instr,self.flag_isNA, self.flag_normalize,
                                                self.callback_on_update)
        else:
            # Sous-bloc par défaut (vide ou message)
            self.current_subblock = Label(self, text="Sélectionnez une configuration")
            self.current_subblock.pack()

        

        # 4. Afficher le sous-bloc
        self.current_subblock.pack(fill="both", expand=True)

    

if __name__ == "__main__":
    root = Tk()
    root.title("Test Block 3")
    Block3Main(root)