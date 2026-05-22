


    
# from tkinter import Tk, LabelFrame, Frame, Label, Entry, Button, StringVar, BooleanVar
# from tkinter.ttk import Combobox  # Combobox classique n'existe pas dans Tkinter, ttk reste obligatoire ici



from tkinter import Frame, Label, Button, Toplevel,Text,Scrollbar
from tkinter.ttk import Combobox
import numpy as np
import pandas as pd

class Block3SimplePlot(Frame):
    def __init__(self, parent, dataframe_from_bloc_2, type_analysis, flag_sync_timescale,threshold_instrument_dic,flag_threshold_instr, flag_isNA, flag_normalize, callback_on_update=None):
        super().__init__(parent)
        self.dataframes_from_bloc2 = dataframe_from_bloc_2
        self.type_analysis = type_analysis
        self.flag_sync = flag_sync_timescale
        self.threshold_instrument_dic = threshold_instrument_dic
        self.flag_threshold_instr = flag_threshold_instr
        self.flag_isNA = flag_isNA
        self.flag_normalize = flag_normalize
        self.callback_on_update = callback_on_update
        self.lignes_sources = []
        self._build_interface()

    def _build_interface(self):
        """Construit l'interface principale avec les en-têtes."""
        self.rows_frame = Frame(self)
        self.rows_frame.pack(fill="x", padx=10, pady=10)

        # En-têtes du tableau
        headers = ["Type","Instrument", "ID", "Measure", "Info Line", "Action"]
        for col, text in enumerate(headers):
            Label(self.rows_frame, text=text, width=12, anchor="center",relief="groove").grid(
                row=0, column=col, padx=5, pady=2, sticky="ew")

        # Bouton pour ajouter une ligne
        Button(self, text="Add a Measure", command=self.ajouter_ligne).pack(pady=10)

        # Bouton pour valider les mesures
        Button(self, text="Validate Configuration", command=self.validate_groupe).pack(pady=10)

    def validate_groupe(self):
        """Valide les mesures et envoie les données filtrées au Bloc 4."""
        if self.callback_on_update:
            filtered_data = self.get_filter_data()
            self.callback_on_update(filtered_data, self.type_analysis, self.flag_sync )

    def ajouter_ligne(self):
        """Ajoute une ligne pour une mesure."""
        row_idx = len(self.lignes_sources) + 1
        
        # Numéro de ligne
        label_num = Label(self.rows_frame, text=f"Line {row_idx}", width=5)
        label_num.grid(row=row_idx, column=0, padx=5, pady=2)
    
        # Combobox Instrument
        instrument_cb = Combobox(self.rows_frame, values=list(self.dataframes_from_bloc2.keys()), width=15)
        instrument_cb.set("Select instrument")
        instrument_cb.grid(row=row_idx, column=1, padx=5, pady=2)
    
        # Combobox ID
        id_cb = Combobox(self.rows_frame, values=[], width=15)
        id_cb.set("ID")
        id_cb.grid(row=row_idx, column=2, padx=5, pady=2)
    
        # Combobox Measure
        measure_cb = Combobox(self.rows_frame, values=[], width=15)
        measure_cb.set("Measure")
        measure_cb.grid(row=row_idx, column=3, padx=5, pady=2)
    
        # Info length
        # info_len = Label(self.rows_frame, text="0", width=10)
        # info_len.grid(row=row_idx, column=4, padx=5, pady=2)
        btn_print = Button(self.rows_frame, text="Print") 
        btn_print.grid(row=row_idx, column=4, padx=5, pady=2) 
    
        # Bouton Supprimer
        btn_suppr = Button(self.rows_frame, text="Delete", bg="#ffcccc")
        btn_suppr.grid(row=row_idx, column=5, padx=5, pady=2)
    
        # Callback pour mise à jour ID et Measure
        # --- Callbacks pour mise à jour dynamique ---
        def update_instrument(event=None):
            self.update_id_options(ligne)
            self.update_measure_options(ligne)

        def update_id(event=None):
            self.update_measure_options(ligne)

        

        # --- Bind des événements ---
        instrument_cb.bind("<<ComboboxSelected>>", update_instrument)
        id_cb.bind("<<ComboboxSelected>>", update_id)
        

        # --- Dictionnaires pour les lignes ---
        ligne = {
            "Line ID": label_num,
            "Instrument": instrument_cb,
            "ID": id_cb,
            "Measure": measure_cb,
            "widgets": [label_num, instrument_cb, id_cb, measure_cb, btn_print],
            "btn_suppr": btn_suppr,
            "row_idx": row_idx ,
            "line_num": row_idx
        }

       
        btn_print.config(command=lambda ligne=ligne: self.afficher_infos_df(f"line_{ligne['row_idx']}"))
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
        
        lines = self.lignes_sources[:]  # Les autres lignes "other" à réorganiser
        print("len other lines:", len(lines))
        for idx, ligne in enumerate(lines):
            row_idx = idx + 1 # Nouvelle position de la ligne (commence à la ligne 4)
            print("idx:",idx)
            print("row_idx:",row_idx)
            for i, widget in enumerate(ligne["widgets"]):
                widget.grid(row=row_idx, column=i, padx=5, pady=2)
            
            ligne["btn_suppr"].grid(row=row_idx, column=5, padx=5, pady=2)
            ligne["widgets"][0].config(text=f"Line {row_idx}")  # Mettre à jour le label "Line X"
            #ligne["widgets"][-1].config(text=f"Line {row_idx}")  # Mettre à jour le bouton "Line X"
            ligne["row_idx"] = row_idx
            ligne["line_num"] = row_idx

    # def supprimer_ligne(self, groupe):
    #     """Supprime un groupe (2 lignes + bouton)."""
    #     # Supprimer les widgets de la ligne de référence
    #     for widget in groupe["ligne"]["widgets"]:
    #         widget.destroy()
        
    #     # Supprimer le bouton
    #     groupe["btn_suppr"].destroy()
    #     # Retirer le groupe de la liste
    #     self.lignes_sources.remove(groupe)
    #     # Réorganiser les numéros de groupe et les lignes
    #     self.reorganiser_lignes()

    # def reorganiser_lignes(self):
    #     """Réorganise les numéros de groupe et les lignes après une suppression."""
    #     for idx, groupe in enumerate(self.lignes_sources, start=0):
    #         row_idx = idx  + 1  # Nouvelle position de la première ligne du groupe
    #         # Mettre à jour les positions des widgets
    #         for i, widget in enumerate(groupe["ligne"]["widgets"]):
    #             widget.grid(row=row_idx, column=i, padx=5, pady=2)
            
    #         groupe["btn_suppr"].grid(row=row_idx, column=5, padx=5, pady=2)
    #         # Mettre à jour les labels de numéro de groupe
    #         groupe["ligne"]["widgets"][3].config(text=f"Line {row_idx}")
            
    #     self.num_line = len(self.lignes_sources) + 1  # Mettre à jour le compteur de groupes

    def update_from_block2(self, dataframes, type_analysis, sync_timescale):
        """Met à jour les données depuis le Bloc 2."""
        self.dataframes_from_bloc2 = {k: v.copy() for k, v in dataframes.items() if v is not None}
        print(f"[Bloc 3] Données reçues : {list(self.dataframes_from_bloc2.keys())}")
        self.type_analysis = type_analysis
        print("Type analysis =", self.type_analysis)
    

        # Mettre à jour les options des lignes existantes
        for groupe in self.lignes_sources:
            for ligne_type in ["ligne"]:
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

       # ligne["InfoLen"].config(text=str(len(df_id)))

    def get_filter_data(self):
        filtered_data = {}
 
        for idx, ligne in enumerate(self.lignes_sources, start=1):
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
 
    def afficher_infos_df(self, tag):
        print("afficher_infos_df")
        print("tag",tag)
        
        filtered_data = self.get_filter_data()
        print("filtered_data",filtered_data)
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

    # def afficher_infos_df(self, num_line):
    #     """Affiche une nouvelle fenêtre avec les caractéristiques et le contenu du DataFrame."""
    #     filtered_data  = self.get_filter_data()
    #     group_key = f"ligne_{num_line}"
    #     df = filtered_data[group_key]["df"]
        
    #     # Créer une nouvelle fenêtre
    #     fenetre_infos = Toplevel()
    #     fenetre_infos.title("Informations sur le DataFrame")
    
    #     # Frame pour les caractéristiques
    #     frame_caracteristiques = Frame(fenetre_infos)
    #     frame_caracteristiques.pack(fill="x", padx=10, pady=5)
    
    #     # Calculer les caractéristiques
    #     longueur = len(df)
    #     min_values = df.min(numeric_only=True)
    #     max_values = df.max(numeric_only=True)
    
    #     # Calculer l'espacement max entre deux mesures
    #     if "datetime" in df.columns:
    #         df_sorted = df.sort_values("datetime")
    #         deltas = df_sorted["datetime"].diff().dt.total_seconds().dropna()
    #         espacement_max = deltas.max() if not deltas.empty else 0
    #     else:
    #         espacement_max = "N/A"
    
    #     # Afficher les caractéristiques
    #     Label(frame_caracteristiques, text=f"Longueur: {longueur}").pack(anchor="w")
    #     Label(frame_caracteristiques, text=f"Espacement max entre deux mesures: {espacement_max} secondes").pack(anchor="w")
    
    #     for col in min_values.index:
    #         Label(frame_caracteristiques, text=f"{col} - Min: {min_values[col]}, Max: {max_values[col]}").pack(anchor="w")
    
    #     # Frame pour le contenu du DataFrame
    #     frame_contenu = Frame(fenetre_infos)
    #     frame_contenu.pack(fill="both", expand=True, padx=10, pady=5)
    
    #     # Ajouter un widget Text pour afficher le DataFrame
    #     text = Text(frame_contenu, wrap="none")
    #     text.pack(side="left", fill="both", expand=True)
    
    #     # Ajouter une barre de défilement
    #     scrollbar = Scrollbar(frame_contenu, command=text.yview)
    #     scrollbar.pack(side="right", fill="y")
    #     text.config(yscrollcommand=scrollbar.set)
    
    #     # Afficher le contenu du DataFrame
    #     text.insert("end", df.to_string())


