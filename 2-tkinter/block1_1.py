# -*- coding: utf-8 -*-
"""
Created on Thu Oct  9 12:06:33 2025

@author: titou
"""

from tkinter import BooleanVar, StringVar, IntVar, DoubleVar, Spinbox, Tk, Label, LabelFrame, END,DISABLED, NORMAL
from tkinter.ttk import Button, Checkbutton, Entry, Combobox, Frame
from tkinter.messagebox import showinfo
from tkinter import filedialog
import pandas as pd
import os

class Block1Read(LabelFrame):
    def __init__(self, master, callback_on_load=None):
        super().__init__(master, text="BLOC 1 : Read Data")
        self.grid(sticky="ew", padx=10, pady=5)
        self.dataframes = {"rabbit": None, "innova": None, "envea": None, "meteo station": None,"data corrected":None}
        self.callback_on_load = callback_on_load
        self.last_loaded_df = None

        self.inner_frame = Frame(self)
        self.inner_frame.grid(sticky="ew", padx=10, pady=10)
        self.create_widgets()

    def create_widgets(self):
        #for i, src in enumerate(self.dataframes.keys()):
        Label(self.inner_frame, text="rabbit".capitalize(), width=12).grid(row=0, column=0, sticky="w", pady=2)
        entry_r =Entry(self.inner_frame, width=70)
        entry_r.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        Button(self.inner_frame, text="Browse",command=lambda s="rabbit", e=entry_r: self.load_csv(s, e)).grid(row=0, column=2, padx=5, pady=2)
        
        Label(self.inner_frame, text="innova".capitalize(), width=12).grid(row=1, column=0, sticky="w", pady=2)
        entry_i =Entry(self.inner_frame, width=70)
        entry_i.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        Button(self.inner_frame, text="Browse",command=lambda s="innova", e=entry_i: self.load_csv(s, e)).grid(row=1, column=2, padx=5, pady=2)
        
        Label(self.inner_frame, text="meteo station".capitalize(), width=12).grid(row=2, column=0, sticky="w", pady=2)
        entry_ms =Entry(self.inner_frame, width=70)
        entry_ms.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        Button(self.inner_frame, text="Browse",command=lambda s="meteo_station", e=entry_ms: self.load_csv(s, e)).grid(row=2, column=2, padx=5, pady=2)
        
        Label(self.inner_frame, text="SIAS", width=12).grid(row=3, column=0, sticky="w", pady=2)
        entry_dc =Entry(self.inner_frame, width=70)
        entry_dc.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        #entry_dc.config(state=DISABLED)
        button_dc = Button(self.inner_frame, text="Browse",command=lambda s="SIAS", e=entry_dc: self.load_csv(s, e))
        button_dc.grid(row=3, column=2, padx=5, pady=2)
        #button_dc.config(state= DISABLED)
        
        Label(self.inner_frame, text="Data corrected".capitalize(), width=12).grid(row=4, column=0, sticky="w", pady=2)
        entry_dc =Entry(self.inner_frame, width=70)
        entry_dc.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        #entry_e.config(state=DISABLED)
        button_dc = Button(self.inner_frame, text="Browse",command=lambda s="corrected", e=entry_dc: self.load_csv(s, e))
        button_dc.grid(row=4, column=2, padx=5, pady=2)
        #button_e.config(state=DISABLED)
        
        
        
        
        
    
    
    
    
    def load_csv(self, source, entry_widget):
        default_path = os.path.join(os.getcwd()).replace("tkinter",f"data\data_{source}")
        if not os.path.exists(default_path):
            default_path = os.getcwd()
        
        print("DEFAULT PATH",default_path)
        path = filedialog.askopenfilename(initialdir = default_path,filetypes=[("CSV Files", "*.csv")])
        if path:
            entry_widget.delete(0, END)
            entry_widget.insert(0, path)
            try:
                df = pd.read_csv(path, sep = ";")
                # Nettoie les noms de colonnes
                df.columns = df.columns.str.strip()
                # Conversion explicite
                if "datetime" in df.columns:
                    print("DATETIME IN DF")
                    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
                self.dataframes[source] = df
                self.last_loaded_df = df
                print(f"{source} loaded: {df.shape}")

                # ✅ notifier Bloc 2
                if callable(self.callback_on_load):
                    self.callback_on_load(self.dataframes)

            except Exception as e:
                print(f"Loading error for the file {source}: {e}")
                showinfo("Error", f"Error loading {source}: {e}")


# Pour test individuel
if __name__ == "__main__":
    root = Tk()
    root.title("Test Block 1")
    Block1Read(root)
    #df_loaded = Block1Read.dataframes["rabbit"]
    root.mainloop()
