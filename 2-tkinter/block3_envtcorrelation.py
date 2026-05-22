# -*- coding: utf-8 -*-
"""
Created on Wed Oct 15 12:57:52 2025

@author: titou
"""


from tkinter import Frame, Label, Button, Toplevel,Text,Scrollbar,Entry
from tkinter.ttk import Combobox
import numpy as np
import pandas as pd
from tkinter.messagebox import showinfo

class Block3ECorr(Frame):
    def __init__(self, parent, dataframe_from_bloc_2, type_analysis, flag_sync_timescale,threshold_instrument_dic,flag_threshold_instr,flag_isNA,flag_normalize, callback_on_update=None):
        super().__init__(parent)
        self.dataframes_from_bloc2 = dataframe_from_bloc_2
        self.type_analysis = type_analysis
        self.flag_sync = flag_sync_timescale
        self.threshold_instrument_dic = threshold_instrument_dic
        self.flag_threshold_instr = flag_threshold_instr
        self.flag_isNA = flag_isNA
        self.flag_normalize = flag_normalize
        self.callback_on_update = callback_on_update
        self.lignes_sources = []  # Liste des groupes (chaque groupe = 2 lignes)
        self.num_grp = 1          # Compteur de groupes
        self._build_interface()

    def _build_interface(self):
        """Construit l'interface principale avec les en-têtes."""
        self.rows_frame = Frame(self)
        self.rows_frame.pack(fill="x", padx=10, pady=10)

        # En-têtes du tableau
        headers = ["Type", "Instrument", "ID", "Measure", "Info Line", "Action"]
        for col, text in enumerate(headers):
            Label(self.rows_frame, text=text, width=12, anchor="center", relief="groove").grid(
                row=0, column=col, padx=5, pady=2, sticky="ew"
            )
        
        self.init_ligne_envt()
        self.init_ligne_ref()
        self.init_ligne_other()
        # Bouton pour ajouter un groupe
        Button(self, text="Add a Line", command=self.ajouter_ligne).pack(pady=10)
        
        ####################################
        # Frame pour la configuration des seuils
        self.threshold_frame = Frame(self)
        self.threshold_frame.pack(fill="x", padx=10, pady=5)
         
       
        
        
        # Bouton pour valider les groupes
        Button(self, text="Validate Configuration", command=self.validate_groupe).pack(pady=10)

    def validate_groupe(self):
        """Valide les groupes et envoie les données filtrées au Bloc 4."""
        self.nb_interval = self.validate_interval()
        if self.nb_interval != None:
            if self.callback_on_update:
                filtered_data = self.get_filter_data()
                self.callback_on_update(filtered_data, self.type_analysis,self.flag_sync,self.nb_interval)
    
    
    def init_ligne_envt(self):
        print("ajouter_ligne_ref")
        row_idx = 1  # Position de la ligne de référence (ligne 0 : header)
        label_type_envt = Label(self.rows_frame, text="Envt", width=8)
        label_type_envt.grid(row=row_idx , column=0, padx=5, pady=2)  # +1 pour le header

        instrument_cb_envt = Combobox(self.rows_frame, values=list(self.dataframes_from_bloc2.keys()), width=15)
        instrument_cb_envt.set("Select instrument")
        instrument_cb_envt.grid(row=row_idx, column=1, padx=5, pady=2)

        id_cb_envt = Combobox(self.rows_frame, values=[], width=15)
        id_cb_envt.set("ID")
        id_cb_envt.grid(row=row_idx, column=2, padx=5, pady=2)

        measure_cb_envt = Combobox(self.rows_frame, values=[], width=15)
        measure_cb_envt.set("Measure")
        measure_cb_envt.grid(row=row_idx, column=3, padx=5, pady=2)

        btn_print_envt = Button(self.rows_frame, text="Print", command=lambda: self.afficher_infos_df("envt"))
        btn_print_envt.grid(row=row_idx, column=4, padx=5, pady=2)

        ligne_envt = {
            "Line ID": label_type_envt,
            "Instrument": instrument_cb_envt,
            "ID": id_cb_envt,
            "Measure": measure_cb_envt,
            "widgets": [label_type_envt, instrument_cb_envt, id_cb_envt, measure_cb_envt, btn_print_envt],
            "row_idx": row_idx 
        }

        def update_envt_instrument(event=None):
            self.update_id_options(ligne_envt)
            self.update_measure_options(ligne_envt)

        def update_envt_id(event=None):
            self.update_measure_options(ligne_envt)

        instrument_cb_envt.bind("<<ComboboxSelected>>", update_envt_instrument)
        id_cb_envt.bind("<<ComboboxSelected>>", update_envt_id)
        measure_cb_envt.bind("<<ComboboxSelected>>", self.update_threshold_info)

        self.lignes_sources.append(ligne_envt)
        self.update_id_options(ligne_envt)
        
    def init_ligne_ref(self):
        print("ajouter_ligne_ref")
        row_idx = 2  # Position de la ligne de référence (ligne 0 : header)
        label_type_ref = Label(self.rows_frame, text="Reference", width=8)
        label_type_ref.grid(row=row_idx , column=0, padx=5, pady=2)  # +1 pour le header

        instrument_cb_ref = Combobox(self.rows_frame, values=list(self.dataframes_from_bloc2.keys()), width=15)
        instrument_cb_ref.set("Select instrument")
        instrument_cb_ref.grid(row=row_idx, column=1, padx=5, pady=2)

        id_cb_ref = Combobox(self.rows_frame, values=[], width=15)
        id_cb_ref.set("ID")
        id_cb_ref.grid(row=row_idx, column=2, padx=5, pady=2)

        measure_cb_ref = Combobox(self.rows_frame, values=[], width=15)
        measure_cb_ref.set("Measure")
        measure_cb_ref.grid(row=row_idx, column=3, padx=5, pady=2)

        btn_print_ref = Button(self.rows_frame, text="Print", command=lambda: self.afficher_infos_df("ref"))
        btn_print_ref.grid(row=row_idx, column=4, padx=5, pady=2)

        ligne_ref = {
            "Line ID": label_type_ref,
            "Instrument": instrument_cb_ref,
            "ID": id_cb_ref,
            "Measure": measure_cb_ref,
            "widgets": [label_type_ref, instrument_cb_ref, id_cb_ref, measure_cb_ref, btn_print_ref],
            "row_idx": row_idx 
        }

        def update_ref_instrument(event=None):
            self.update_id_options(ligne_ref)
            self.update_measure_options(ligne_ref)

        def update_ref_id(event=None):
            self.update_measure_options(ligne_ref)

        instrument_cb_ref.bind("<<ComboboxSelected>>", update_ref_instrument)
        id_cb_ref.bind("<<ComboboxSelected>>", update_ref_id)

        self.lignes_sources.append(ligne_ref)
        self.update_id_options(ligne_ref)

    def init_ligne_other(self):
        print("ajouter_ligne_other")
        row_idx = 3  # Position de la première ligne "other" (ligne 3 dans l'interface)
        label_type_other = Label(self.rows_frame, text="Line 1", width=8)
        label_type_other.grid(row=row_idx, column=0, padx=5, pady=2)  # +1 pour le header

        instrument_cb_other = Combobox(self.rows_frame, values=list(self.dataframes_from_bloc2.keys()), width=15)
        instrument_cb_other.set("Select instrument")
        instrument_cb_other.grid(row=row_idx, column=1, padx=5, pady=2)

        id_cb_other = Combobox(self.rows_frame, values=[], width=15)
        id_cb_other.set("ID")
        id_cb_other.grid(row=row_idx, column=2, padx=5, pady=2)

        measure_cb_other = Combobox(self.rows_frame, values=[], width=15)
        measure_cb_other.set("Measure")
        measure_cb_other.grid(row=row_idx, column=3, padx=5, pady=2)

        btn_print_other = Button(self.rows_frame, text="Print", command=lambda: self.afficher_infos_df("line_1"))
        btn_print_other.grid(row=row_idx, column=4, padx=5, pady=2)

        ligne_other = {
            "Line ID": label_type_other,
            "Instrument": instrument_cb_other,
            "ID": id_cb_other,
            "Measure": measure_cb_other,
            "widgets": [label_type_other, instrument_cb_other, id_cb_other, measure_cb_other, btn_print_other],
            "row_idx": row_idx 
        }

        def update_other_instrument(event=None):
            self.update_id_options(ligne_other)
            self.update_measure_options(ligne_other)

        def update_other_id(event=None):
            self.update_measure_options(ligne_other)

        instrument_cb_other.bind("<<ComboboxSelected>>", update_other_instrument)
        id_cb_other.bind("<<ComboboxSelected>>", update_other_id)
        measure_cb_other.bind("<<ComboboxSelected>>", self.update_threshold_info)

        self.lignes_sources.append(ligne_other)
        self.update_id_options(ligne_other)

    def ajouter_ligne(self):
        print("ajouter_ligne")
        row_idx_new_line = len(self.lignes_sources) + 1  # +1 pour le header
        line_num_new_line = row_idx_new_line - 2  # Numéro de la nouvelle ligne (-2 pour enlever ref et envt)

        label_type = Label(self.rows_frame, text=f"Line {line_num_new_line}", width=8)
        label_type.grid(row=row_idx_new_line, column=0, padx=5, pady=2)  # +1 pour le header

        instrument_cb = Combobox(self.rows_frame, values=list(self.dataframes_from_bloc2.keys()), width=15)
        instrument_cb.set("Select instrument")
        instrument_cb.grid(row=row_idx_new_line, column=1, padx=5, pady=2)

        id_cb = Combobox(self.rows_frame, values=[], width=15)
        id_cb.set("ID")
        id_cb.grid(row=row_idx_new_line, column=2, padx=5, pady=2)

        measure_cb = Combobox(self.rows_frame, values=[], width=15)
        measure_cb.set("Measure")
        measure_cb.grid(row=row_idx_new_line, column=3, padx=5, pady=2)

        btn_print = Button(self.rows_frame, text="Print")
        btn_print.grid(row=row_idx_new_line, column=4, padx=5, pady=2)

        btn_suppr = Button(self.rows_frame, text="Delete", bg="#ffcccc")
        btn_suppr.grid(row=row_idx_new_line, column=5, padx=5, pady=2)

        ligne = {
            "Line ID": label_type,
            "Instrument": instrument_cb,
            "ID": id_cb,
            "Measure": measure_cb,
            "widgets": [label_type, instrument_cb, id_cb, measure_cb, btn_print],
            "btn_suppr": btn_suppr,
            "row_idx": row_idx_new_line ,
            "line_num": line_num_new_line
        }

        def update_instrument(event=None):
            self.update_id_options(ligne)
            self.update_measure_options(ligne)

        def update_id(event=None):
            self.update_measure_options(ligne)

        instrument_cb.bind("<<ComboboxSelected>>", update_instrument)
        id_cb.bind("<<ComboboxSelected>>", update_id)
        
        btn_print.config(command=lambda ligne=ligne: self.afficher_infos_df(f"line_{ligne['line_num']}"))
        btn_suppr.config(command=lambda ligne=ligne: self.supprimer_ligne(ligne))
        
        
        self.lignes_sources.append(ligne)
        self.update_id_options(ligne)

    def supprimer_ligne(self, ligne):
        print("----------")
        print("supprimer_ligne")
        if ligne not in self.lignes_sources:
            print("ligne déjà supprimée ou invalide")
            return
    
        idx = self.lignes_sources.index(ligne)
        print("len lignes_sources:", len(self.lignes_sources))
        print("idx", idx)
        print("ligne row_idx", ligne["row_idx"])
        print("ligne line_num", ligne.get("line_num"))
    
        for widget in ligne["widgets"]:
            widget.destroy()
        if "btn_suppr" in ligne:
            ligne["btn_suppr"].destroy()
    
        self.lignes_sources.remove(ligne)
        self.reorganiser_lignes()


    def reorganiser_lignes(self):
        print("reorganiser_lignes")
        fixed_lines = self.lignes_sources[:3]  # Les deux premières lignes sont fixes
        print("len fixed lines:", len(fixed_lines))
        other_lines = self.lignes_sources[3:]  # Les autres lignes "other" à réorganiser
        print("len other lines:", len(other_lines))
        for idx, ligne in enumerate(other_lines):
            row_idx = idx + 4 # Nouvelle position de la ligne (commence à la ligne 4)
            print("idx:",idx)
            print("row_idx:",row_idx)
            for i, widget in enumerate(ligne["widgets"]):
                widget.grid(row=row_idx, column=i, padx=5, pady=2)
            
            ligne["btn_suppr"].grid(row=row_idx, column=5, padx=5, pady=2)
            ligne["widgets"][0].config(text=f"Line {idx+2}")  # Mettre à jour le label "Line X"
            #ligne["widgets"][-1].config(text=f"Line {idx+2}")  # Mettre à jour le bouton "Line X"
            ligne["row_idx"] = row_idx
            ligne["line_num"] = idx+2
    
    

    def update_from_block2(self, dataframes, type_analysis):
        """Met à jour les données depuis le Bloc 2."""
        self.dataframes_from_bloc2 = {k: v.copy() for k, v in dataframes.items() if v is not None}
        print(f"[Bloc 3] Données reçues : {list(self.dataframes_from_bloc2.keys())}")
        self.type_analysis = type_analysis
        print("Type analysis =", self.type_analysis)

        # Mettre à jour les options des lignes existantes
        for groupe in self.lignes_sources:
            for ligne_type in ["ref", "other"]:
                ligne = groupe[ligne_type]
                ligne["Instrument"]["values"] = list(self.dataframes_from_bloc2.keys())
                if ligne["Instrument"].get() not in ligne["Instrument"]["values"]:
                    ligne["Instrument"].set("Select instrument")
                self.update_id_options(ligne)

    def update_id_options(self, ligne):
        """Met à jour les ID selon l’instrument choisi."""
        instr = ligne["Instrument"].get()
        df = self.dataframes_from_bloc2.get(instr)
        if df is not None:
            
            if instr.lower() == "meteo_station":
                ligne["ID"]["values"] = ["in", "out"]
                if ligne["ID"].get() not in ["in", "out"]:
                    ligne["ID"].set("in")
                self.update_measure_options(ligne)
            
            elif instr.lower() == "sias" and "id_sias" in df.columns:
                ids = df["id_sias"].dropna().unique().tolist()
                ligne["ID"]["values"] = ids
                if ids:
                    ligne["ID"].set(ids[0])
                    self.update_measure_options(ligne)
                else:
                    ligne["ID"].set("")
                    ligne["Measure"]["values"] = []
                    ligne["Measure"].set("Measure")
            
            elif instr.lower() == "innova" and "id_channel" in df.columns:
                ids = df["id_channel"].dropna().unique().tolist()
                ligne["ID"]["values"] = ids
                if ids:
                    ligne["ID"].set(ids[0])
                    self.update_measure_options(ligne)
                else:
                    ligne["ID"].set("")
                    ligne["Measure"]["values"] = []
                    ligne["Measure"].set("Measure")
                    
            elif instr.lower() == "rabbit" and "id_rabbit" in df.columns:
                ids = df["id_rabbit"].dropna().unique().tolist()
                ligne["ID"]["values"] = ids
                if ids:
                    ligne["ID"].set(ids[0])
                    self.update_measure_options(ligne)
                else:
                    ligne["ID"].set("")
                    ligne["Measure"]["values"] = []
                    ligne["Measure"].set("Measure")
            elif instr.lower() == "corrected" and "id_rabbit" in df.columns:
                print("entered_block")
                ids = df["id_rabbit"].dropna().unique().tolist()
                ligne["ID"]["values"] = ids
                if ids:
                    print(ids)
                    ligne["ID"].set(ids[0])
                    self.update_measure_options(ligne)
                else:
                    ligne["ID"].set("")
                    ligne["Measure"]["values"] = []
                    ligne["Measure"].set("Measure")
            else:
                ligne["ID"]["values"] = []
                ligne["ID"].set("")
                ligne["Measure"]["values"] = []
                ligne["Measure"].set("Measure")
            
        else:
            ligne["ID"]["values"] = []
            ligne["ID"].set("")
            ligne["Measure"]["values"] = []
            ligne["Measure"].set("Measure")

    def update_measure_options(self, ligne):
        """Met à jour les options de mesure en fonction de l'ID sélectionné."""
        instrument = ligne["Instrument"].get()
        id_selected = ligne["ID"].get()

        if not instrument or not id_selected:
            ligne["Measure"]["values"] = ["No data"]
            ligne["Measure"].set("No data")
            return

        df = self.dataframes_from_bloc2.get(instrument)
        if df is None:
            ligne["Measure"]["values"] = ["No dataframe"]
            ligne["Measure"].set("No dataframe")
            return

        if instrument.lower() == "meteo_station":
            if id_selected not in ["in", "out"]:
                ligne["Measure"]["values"] = ["Invalid ID (must be 'in' or 'out')"]
                ligne["Measure"].set("Invalid ID (must be 'in' or 'out')")
                return

            suffix = f"_{id_selected}"
            measure_options_with_suffix = [col for col in df.columns if col.endswith(suffix) and df[col].notna().any()]
            
            # Enlever le suffixe pour l'affichage
            measure_options = [col.replace(suffix, "") for col in measure_options_with_suffix]

            if not measure_options:
                ligne["Measure"]["values"] = [f"No measures for {id_selected}"]
                ligne["Measure"].set(f"No measures for {id_selected}")
            else:
                ligne["Measure"]["values"] = measure_options
                ligne["Measure"].set(measure_options[0])

            #ligne["InfoLen"].config(text=str(len(df)))
            return
        
        # if instrument.lower() == "sias":
        #     id_col = "id_sias"
        #     excluded_columns = ["datetime","date","hour","id_sias"]
        #     df_id = df[df[id_col] == id_selected]
        
        if instrument.lower() == "innova":
            id_col = "id_channel"
        elif instrument.lower() == "rabbit":
            id_col = "id_rabbit"
        elif instrument.lower() == "sias":
            id_col = "id_sias"
        elif instrument.lower() == "corrected":
             id_col = "id_rabbit"
        
            
        else:
            ligne["Measure"]["values"] = ["Unknown instrument"]
            ligne["Measure"].set("Unknown instrument")
            return

        if id_col not in df.columns:
            ligne["Measure"]["values"] = ["No ID column"]
            ligne["Measure"].set("No ID column")
            return
        
        if instrument.lower() in ["innova","rabbit","corrected"]:
            try:
                id_selected = int(float(id_selected))
            except ValueError:
                ligne["Measure"]["values"] = ["Invalid ID"]
                ligne["Measure"].set("Invalid ID")
                return

        df_id = df[df[id_col] == id_selected]

        if df_id.empty:
            ligne["Measure"]["values"] = ["No data for this ID"]
            ligne["Measure"].set("No data for this ID")
            return

        excluded_columns = []
        if instrument.lower() == "innova":
            excluded_columns = ["datetime","date","hour","id_channel"]
        elif instrument.lower() == "rabbit":
            excluded_columns = ["datetime","date","hour","id_rabbit"]
        elif instrument.lower() == "meteo_station":
            excluded_columns = ["datetime","date","hour"]
        elif instrument.lower() == "sias":
            excluded_columns = ["datetime","date","hour","id_sias"]
        elif instrument.lower() == "corrected":
            excluded_columns = ["datetime","date","hour","id_rabbit","id_channel"]

        


        measure_options = [col for col in df_id.columns if col not in excluded_columns and df_id[col].notna().any()]

        if not measure_options:
            ligne["Measure"]["values"] = ["No measures available"]
            ligne["Measure"].set("No measures available")
        else:
            ligne["Measure"]["values"] = measure_options
            ligne["Measure"].set(measure_options[0])

        #ligne["InfoLen"].config(text=str(len(df_id)))
    
    def get_filter_data(self):
        filtered_data = {}
        
        envt_line = self.lignes_sources[0]
        envt_instrument = envt_line["Instrument"].get()
        envt_id = envt_line["ID"].get()
        envt_measure = envt_line["Measure"].get()

        if envt_instrument and envt_id and envt_measure:
            df_envt = self.dataframes_from_bloc2.get(envt_instrument)
            if df_envt is not None:
                if envt_instrument.lower() == "meteo_station":
                    measure_suffix = f"{envt_measure}_{envt_id}"
                    if measure_suffix in df_envt.columns:
                        df_envt_filtered = df_envt[["datetime", measure_suffix]].copy()
                        
                        df_envt_filtered.rename(columns={measure_suffix: envt_measure}, inplace=True)
               
                elif envt_instrument.lower() == "sias":
                    id_col = "id_sias"    
                    df_envt_filtered = df_envt[df_envt[id_col] == envt_id].copy()
                    if "datetime" in df_envt_filtered.columns and envt_measure in df_envt_filtered.columns:
                        df_envt_filtered = df_envt_filtered[["datetime", envt_measure]].copy()
                        # df_envt_filtered[envt_measure] = (df_envt_filtered[envt_measure]
                        #                                     .astype(str)                     # convertit tout en string
                        #                                     .str.replace(",", ".", regex=False)  # remplacer les virgules par des points
                        #                                     .replace(["", "nan", "None"], np.nan)  # valeurs invalides → NaN
                        #                                     .astype(float)                   # conversion finale en float
                        #                                 )
                        
                else:
                    id_col = "id_channel" if envt_instrument.lower() == "innova" else "id_rabbit"
                    try:
                        envt_id = int(float(envt_id))
                        df_envt_filtered = df_envt[df_envt[id_col] == envt_id].copy()
                        if "datetime" in df_envt_filtered.columns and envt_measure in df_envt_filtered.columns:
                            df_envt_filtered = df_envt_filtered[["datetime", envt_measure]].copy()
                    except ValueError:
                        pass

                if self.flag_isNA:
                    df_envt_filtered = df_envt_filtered.dropna(subset=["datetime", envt_measure])

                if self.flag_threshold_instr:
                    if envt_instrument in self.threshold_instrument_dic and envt_measure in self.threshold_instrument_dic[envt_instrument]:
                        min_val = self.threshold_instrument_dic[envt_instrument][envt_measure]["min"]
                        max_val = self.threshold_instrument_dic[envt_instrument][envt_measure]["max"]
                        df_envt_filtered = df_envt_filtered[(df_envt_filtered[envt_measure] >= min_val) & (df_envt_filtered[envt_measure] <= max_val)]
                
                if self.flag_normalize:
                    mean_val = df_envt_filtered[envt_measure].mean()
                    centered_values = df_envt_filtered[envt_measure] - mean_val
                    max_abs_centered = max(abs(centered_values)) if not centered_values.empty else 1
                    if max_abs_centered != 0:  # Éviter la division par zéro
                        df_envt_filtered[envt_measure] = centered_values / max_abs_centered

                filtered_data["envt"] = {
                    "instrument": envt_instrument,
                    "id": envt_id,
                    "measure": envt_measure,
                    "df": df_envt_filtered
                }
        
        
        ref_line = self.lignes_sources[1]
        ref_instrument = ref_line["Instrument"].get()
        ref_id = ref_line["ID"].get()
        ref_measure = ref_line["Measure"].get()

        if ref_instrument and ref_id and ref_measure:
            df_ref = self.dataframes_from_bloc2.get(ref_instrument)
            if df_ref is not None:
                if ref_instrument.lower() == "meteo_station":
                    measure_suffix = f"{ref_measure}_{ref_id}"
                    if measure_suffix in df_ref.columns:
                        df_ref_filtered = df_ref[["datetime", measure_suffix]].copy()
                        df_ref_filtered.rename(columns={measure_suffix: ref_measure}, inplace=True)
                
                elif ref_instrument.lower() == "sias":
                    id_col = "id_sias"    
                    df_ref_filtered = df_ref[df_ref[id_col] == ref_id].copy()
                    if "datetime" in df_ref_filtered.columns and ref_measure in df_ref_filtered.columns:
                        df_ref_filtered = df_ref_filtered[["datetime", ref_measure]].copy()
                
                else:
                    id_col = "id_channel" if ref_instrument.lower() == "innova" else "id_rabbit"
                    try:
                        ref_id = int(float(ref_id))
                        df_ref_filtered = df_ref[df_ref[id_col] == ref_id].copy()
                        if "datetime" in df_ref_filtered.columns and ref_measure in df_ref_filtered.columns:
                            df_ref_filtered = df_ref_filtered[["datetime", ref_measure]].copy()
                    except ValueError:
                        pass

                if self.flag_isNA:
                    df_ref_filtered = df_ref_filtered.dropna(subset=["datetime", ref_measure])

                if self.flag_threshold_instr:
                    if ref_instrument in self.threshold_instrument_dic and ref_measure in self.threshold_instrument_dic[ref_instrument]:
                        min_val = self.threshold_instrument_dic[ref_instrument][ref_measure]["min"]
                        max_val = self.threshold_instrument_dic[ref_instrument][ref_measure]["max"]
                        df_ref_filtered = df_ref_filtered[(df_ref_filtered[ref_measure] >= min_val) & (df_ref_filtered[ref_measure] <= max_val)]
                
                if self.flag_normalize:
                    mean_val = df_ref_filtered[ref_measure].mean()
                    centered_values = df_ref_filtered[ref_measure] - mean_val
                    max_abs_centered = max(abs(centered_values)) if not centered_values.empty else 1
                    if max_abs_centered != 0:  # Éviter la division par zéro
                        df_ref_filtered[ref_measure] = centered_values / max_abs_centered
                
                filtered_data["ref"] = {
                    "instrument": ref_instrument,
                    "id": ref_id,
                    "measure": ref_measure,
                    "df": df_ref_filtered
                }

        for idx, ligne in enumerate(self.lignes_sources[2:], start=1):
            other_instrument = ligne["Instrument"].get()
            other_id = ligne["ID"].get()
            other_measure = ligne["Measure"].get()

            if other_instrument and other_id and other_measure:
                df_other = self.dataframes_from_bloc2.get(other_instrument)
                if df_other is not None:
                    if other_instrument.lower() == "meteo_station":
                        measure_suffix = f"{other_measure}_{other_id}"
                        if measure_suffix in df_other.columns:
                            df_other_filtered = df_other[["datetime", measure_suffix]].copy()
                            df_other_filtered.rename(columns={measure_suffix: other_measure}, inplace=True)
                    
                    elif other_instrument.lower() == "sias":
                        id_col = "id_sias"    
                        df_other_filtered = df_other[df_other[id_col] == other_id].copy()
                        if "datetime" in df_other_filtered.columns and other_measure in df_other_filtered.columns:
                            df_other_filtered = df_other_filtered[["datetime", other_measure]].copy()
                    
                    else:
                        id_col = "id_channel" if other_instrument.lower() == "innova" else "id_rabbit"
                        try:
                            other_id = int(float(other_id))
                            df_other_filtered = df_other[df_other[id_col] == other_id].copy()
                            if "datetime" in df_other_filtered.columns and other_measure in df_other_filtered.columns:
                                df_other_filtered = df_other_filtered[["datetime", other_measure]].copy()
                        except ValueError:
                            continue

                    if self.flag_isNA:
                        df_other_filtered = df_other_filtered.dropna(subset=["datetime", other_measure])

                    if self.flag_threshold_instr:
                        if other_instrument in self.threshold_instrument_dic and other_measure in self.threshold_instrument_dic[other_instrument]:
                            min_val = self.threshold_instrument_dic[other_instrument][other_measure]["min"]
                            max_val = self.threshold_instrument_dic[other_instrument][other_measure]["max"]
                            df_other_filtered = df_other_filtered[(df_other_filtered[other_measure] >= min_val) & (df_other_filtered[other_measure] <= max_val)]
                    
                    if self.flag_normalize:
                        mean_val = df_other_filtered[other_measure].mean()
                        centered_values = df_other_filtered[other_measure] - mean_val
                        max_abs_centered = max(abs(centered_values)) if not centered_values.empty else 1
                        if max_abs_centered != 0:  # Éviter la division par zéro
                            df_other_filtered[other_measure] = centered_values / max_abs_centered
                    
                    filtered_data[f"line_{idx}"] = {
                        "instrument": other_instrument,
                        "id": other_id,
                        "measure": other_measure,
                        "df": df_other_filtered
                    }
        
                    
        if self.flag_sync:
            # Extraire les DataFrames de dataframes_from_bloc3
            dfs = []
            for key, data in filtered_data.items():
                if isinstance(data, dict) and "df" in data:
                    dfs.append(data["df"])
            if len(dfs) >= 2:
                self.dataframes_aligned = {}
                aligned_dfs = self.align_dataframes(dfs)
                for i, (key, data) in enumerate(filtered_data.items()):
                    if isinstance(data, dict):
                        data["df"] = aligned_dfs[i]
                        self.dataframes_aligned[key] = data
            else:
                self.dataframes_aligned = filtered_data
        else:
            self.dataframes_aligned = filtered_data
        
        
        
        return self.dataframes_aligned
    
    
    # def align_dataframes(self, df_list, debug=False, time_col="datetime"):
    #     """
    #     Aligne plusieurs DataFrames sur une échelle de temps commune basée sur la série la plus lente,
    #     en interpolant les séries rapides uniquement sur les points internes.
    #     Retourne une liste de DataFrames avec la même structure que l'entrée, mais avec les données alignées.
    #     """
    #     if debug:
    #         print("align_dataframes")
        
    #     # Vérifier qu'il y a au moins deux DataFrames à aligner
    #     if len(df_list) < 2:
    #         return df_list
        
    #     # Extraire les séries de temps
    #     t_list = [df[time_col].values.astype("datetime64[s]").astype(float) for df in df_list]
        
    #     # Trouver l'intervalle de temps commun
    #     t_start = max(t.min() for t in t_list)
    #     t_end = min(t.max() for t in t_list)
        
    #     # Trouver la série la plus lente
    #     dt_list = [np.median(np.diff(t)) for t in t_list]
    #     slow_idx = np.argmax(dt_list)
    #     t_slow = t_list[slow_idx]
    #     df_slow = df_list[slow_idx]
        
    #     # Créer les points de temps internes
    #     t_internal = t_slow[(t_slow > t_start) & (t_slow < t_end)]
    #     t_common = np.concatenate(([t_start], t_internal, [t_end]))
        
    #     # Créer le DataFrame commun avec seulement la colonne de temps
    #     df_common_time = pd.DataFrame({"datetime": pd.to_datetime(t_common, unit="s")})
        
    #     # Aligner chaque DataFrame individuellement
    #     aligned_dfs = []
    #     for i, df in enumerate(df_list):
    #         aligned_df = df_common_time.copy()
    #         for measure in df.columns:
    #             if measure != time_col:
    #                 if i == slow_idx:
    #                     # Série lente = valeurs exactes
    #                     values = [df[measure].iloc[np.argmin(np.abs(t_slow - t))] for t in t_internal]
        
    #                     # Gestion du premier point
    #                     if df[time_col].iloc[0] == pd.Timestamp(t_start, unit='s'):
    #                         first_value = df[measure].iloc[0]
    #                     else:
    #                         first_value = np.interp(t_start, t_slow, df[measure].values)
        
    #                     # Gestion du dernier point
    #                     if df[time_col].iloc[-1] == pd.Timestamp(t_end, unit='s'):
    #                         last_value = df[measure].iloc[-1]
    #                     else:
    #                         last_value = np.interp(t_end, t_slow, df[measure].values)
        
    #                     aligned_df[measure] = np.concatenate(([first_value], values, [last_value]))
    #                 else:
    #                     # Séries rapides = interpolation
    #                     t_fast = t_list[i]
        
    #                     # Interpolation sur les points internes
    #                     values = np.interp(t_internal, t_fast, df[measure].values)
        
    #                     # Gestion du premier point
    #                     if df[time_col].iloc[0] == pd.Timestamp(t_start, unit='s'):
    #                         first_value = df[measure].iloc[0]
    #                     else:
    #                         first_value = np.interp(t_start, t_fast, df[measure].values)
        
    #                     # Gestion du dernier point
    #                     if df[time_col].iloc[-1] == pd.Timestamp(t_end, unit='s'):
    #                         last_value = df[measure].iloc[-1]
    #                     else:
    #                         last_value = np.interp(t_end, t_fast, df[measure].values)
        
    #                     aligned_df[measure] = np.concatenate(([first_value], values, [last_value]))
    #         aligned_dfs.append(aligned_df)
        
    #     return aligned_dfs
    
    def align_dataframes(self, df_list, debug=False, time_col="datetime"):
        """
        Aligne plusieurs DataFrames sur une échelle de temps commune basée sur la série la plus lente,
        en interpolant les séries rapides uniquement sur les points internes.
        Retourne une liste de DataFrames avec la même structure que l'entrée, mais avec les données alignées.
        """
        if debug:
            print("align_dataframes")
        
        # Vérifier qu'il y a au moins deux DataFrames à aligner
        if len(df_list) < 2:
            return df_list
        
        # Extraire les séries de temps
        t_list = [df[time_col].values.astype("datetime64[s]").astype(float) for df in df_list]
        
        # Trouver l'intervalle de temps commun
        t_start = max(t.min() for t in t_list)
        t_end = min(t.max() for t in t_list)
        
        # Trouver la série la plus lente
        dt_list = [np.median(np.diff(t)) for t in t_list]
        slow_idx = np.argmax(dt_list)
        t_slow = t_list[slow_idx]
        df_slow = df_list[slow_idx]
        
        # Créer les points de temps internes
        t_internal = t_slow[(t_slow > t_start) & (t_slow < t_end)]
        t_common = np.concatenate(([t_start], t_internal, [t_end]))
        
        # Créer le DataFrame commun avec seulement la colonne de temps
        df_common_time = pd.DataFrame({"datetime": pd.to_datetime(t_common, unit="s")})
        
        # Aligner chaque DataFrame individuellement
        aligned_dfs = []
        for i, df in enumerate(df_list):
            aligned_df = df_common_time.copy()
            for measure in df.columns:
                if measure != time_col:
                    # S'assurer que df[measure] est bien float
                    # df[measure] = (
                    #     df[measure]
                    #     .astype(str)                     # convertir tout en string
                    #     .str.replace(",", ".", regex=False)  # remplacer les virgules par des points
                    #     .replace(["", "nan", "None"], np.nan)  # valeurs invalides → NaN
                    #     .astype(float)                   # conversion finale en float
                    # )
                    if i == slow_idx:
                        # Série lente = valeurs exactes
                        values = [df[measure].iloc[np.argmin(np.abs(t_slow - t))] for t in t_internal]
        
                        # Gestion du premier point
                        if df[time_col].iloc[0] == pd.Timestamp(t_start, unit='s'):
                            first_value = df[measure].iloc[0]
                        else:
                            first_value = np.interp(t_start, t_slow, df[measure].values)
                          
                        # Gestion du dernier point
                        if df[time_col].iloc[-1] == pd.Timestamp(t_end, unit='s'):
                            last_value = df[measure].iloc[-1]
                        else:
                            last_value = np.interp(t_end, t_slow, df[measure].values)
        
                        aligned_df[measure] = np.concatenate(([first_value], values, [last_value]))
                    else:
                        # Séries rapides = interpolation
                        t_fast = t_list[i]
        
                        # Interpolation sur les points internes
                        if measure != "wind_dir":
                            values = np.interp(t_internal, t_fast, df[measure].values)
                        else: 
                            values = self.interp_circular(t_internal,t_fast,df[measure].values)
        
                        # Gestion du premier point
                        if df[time_col].iloc[0] == pd.Timestamp(t_start, unit='s'):
                            first_value = df[measure].iloc[0]
                        else:
                            if measure != "wind_dir":
                                first_value = np.interp(t_start, t_fast, df[measure].values)
                            else:
                                first_value = self.interp_circular(t_start,t_fast,df[measure].values)
        
                        # Gestion du dernier point
                        if df[time_col].iloc[-1] == pd.Timestamp(t_end, unit='s'):
                            last_value = df[measure].iloc[-1]
                        else:
                            if measure != "wind_dir":
                                last_value = np.interp(t_end, t_fast, df[measure].values)
                            else:
                                last_value = self.interp_circular(t_end, t_fast, df[measure].values)
        
                        aligned_df[measure] = np.concatenate(([first_value], values, [last_value]))
            aligned_dfs.append(aligned_df)
        
        return aligned_dfs
    
    def interp_circular(self, t_common, t, measure):
        """
        Interpolation circulaire pour des angles en degrés (ex : direction du vent).
        Gère automatiquement le cas scalaire ou vectoriel pour t_common.
        """
        angles = np.deg2rad(np.asarray(measure))
        x = np.cos(angles)
        y = np.sin(angles)
    
        # Interpolation linéaire sur les composantes x et y
        x_interp = np.interp(t_common, t, x, left=np.nan, right=np.nan)
        y_interp = np.interp(t_common, t, y, left=np.nan, right=np.nan)
    
        # Recalcule l’angle interpolé en degrés (valeurs entre 0 et 360)
        result = (np.degrees(np.arctan2(y_interp, x_interp)) + 360) % 360
    
        # Si t_common est un scalaire → renvoie un float, sinon un tableau
        if np.isscalar(t_common):
            return float(result)
        else:
            return result
    

    def afficher_infos_df(self, tag):
        print("afficher_infos_df")
        filtered_data = self.get_filter_data()
        if tag in filtered_data:
            df = filtered_data[tag]["df"]
    
            fenetre_infos = Toplevel()
            fenetre_infos.title("Informations sur le DataFrame")
    
            frame_caracteristiques = Frame(fenetre_infos)
            frame_caracteristiques.pack(fill="x", padx=10, pady=5)
    
            longueur = len(df)
            min_values = df.min(numeric_only=True)
            max_values = df.max(numeric_only=True)
    
            if "datetime" in df.columns:
                df_sorted = df.sort_values("datetime")
                deltas = df_sorted["datetime"].diff().dt.total_seconds().dropna()
                espacement_max = deltas.max() if not deltas.empty else 0
            else:
                espacement_max = "N/A"
    
            Label(frame_caracteristiques, text=f"Longueur: {longueur}").pack(anchor="w")
            Label(frame_caracteristiques, text=f"Espacement max entre deux mesures: {espacement_max} secondes").pack(anchor="w")
    
            for col in min_values.index:
                Label(frame_caracteristiques, text=f"{col} - Min: {min_values[col]}, Max: {max_values[col]}").pack(anchor="w")
    
            frame_contenu = Frame(fenetre_infos)
            frame_contenu.pack(fill="both", expand=True, padx=10, pady=5)
    
            text = Text(frame_contenu, wrap="none")
            text.pack(side="left", fill="both", expand=True)
    
            scrollbar = Scrollbar(frame_contenu, command=text.yview)
            scrollbar.pack(side="right", fill="y")
            text.config(yscrollcommand=scrollbar.set)
    
            text.insert("end", df.to_string())


    def update_threshold_info(self, event = None):
        """Met à jour les informations de seuil."""
        # Paramètre sélectionné (affichage fixe)
        for widget in self.threshold_frame.winfo_children():
            widget.destroy()
        
        filtered_data = self.get_filter_data()
        if "envt" in filtered_data:
            df = filtered_data["envt"]["df"]
            instr = filtered_data["envt"]["instrument"]
            instr_id = filtered_data["envt"]["id"]
            measure = filtered_data["envt"]["measure"]
            min_values = df[measure].min(numeric_only=True)
            max_values = df[measure].max(numeric_only=True)
            len_measure = len(df[measure])
            print("filtered_data[envt]:", filtered_data["envt"])
            print("min_values:",min_values)
            print("max values", max_values)
            print("len measure", len_measure)
            
        self.param_label = Label(self.threshold_frame, text="Parameter choosen:",font=("", 8, "underline"))
        self.param_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
         
        self.param_value = Label(self.threshold_frame, text=f"{instr}_{instr_id}_{measure} (min : {min_values:.2f} ; max : {max_values:.2f} ; len : {len_measure})")
        self.param_value.grid(row=0, column=1, sticky="w", padx=20, pady=2)
         
         
        # Écart entre les groupes (entrée utilisateur)
        self.step_label = Label(self.threshold_frame, text="Nb of intervals to consider:",font=("", 8, "underline"))
        self.step_label.grid(row=1, column=0, sticky="w", padx=5, pady=2)
         
        self.nb_interval_entry = Entry(self.threshold_frame, width=5)
        self.nb_interval_entry.grid(row=1, column=1, sticky="w", padx=20, pady=2)
        self.nb_interval_entry.insert(0, "10")  # Valeur par défaut
        
    def validate_interval(self):
        """Récupère la valeur de l'Entry et l'utilise."""
        try:
            interval_value = int(self.nb_interval_entry.get())
            print(f"Nombre d'intervalles à considérer : {interval_value}")
            return interval_value
            # Utilisez step_value pour votre logique
        except ValueError:
            print("Erreur : La valeur saisie n'est pas un entier valide.")
            showinfo("Error", "You must enter an integer value for the interval number")
            return None
                
                
  