# -*- coding: utf-8 -*-
"""
Created on Wed Nov 26 14:36:30 2025

@author: titou
"""







# # -*- coding: utf-8 -*-
# """
# Created on Wed Nov 26 14:36:30 2025

# @author: titou
# """

from tkinter import Frame, Label, Button, Checkbutton, BooleanVar, filedialog, DISABLED, NORMAL,Scrollbar,filedialog,simpledialog,Entry
from tkinter.ttk import Treeview, Notebook, Combobox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.dates as mdates
import matplotlib.colors as mcolors 
import os
import csv

class Block4DataAnalysis(Frame):
    def __init__(self, parent, dataframes_to_process):
        super().__init__(parent)
        
        
        # Variables pour les options
        self.p_barchart = BooleanVar(master=self, value=True)
        self.p_stats = BooleanVar(master=self, value=False)
        self.p_data = BooleanVar(master = self, value = False)
        
    
        # Frame pour les options
        self.options_frame = Frame(self)
        self.options_frame.pack(fill="x", padx=10, pady=5)

        
        # Remplacer self.plot_frame par un Notebook
        self.notebook = None
        #self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
    
        # Créer un onglet pour chaque type de plot
        
        
        self.barchart_plot_frame = None
        self.stats_display_frame = None
        self.data_display_frame = None
    

        # Données
        self.dataframes_to_process = dataframes_to_process
        self.create_widgets()

    def create_widgets(self):
        """Crée les widgets d'interface."""
        # Options de plot
        Checkbutton(self.options_frame, text="Barchart", variable=self.p_barchart).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Statistics", variable=self.p_stats).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Data", variable=self.p_data).pack(side="left", padx=5)
        
        
        # Bouton pour exécuter l'analyse
        Button(self.options_frame, text="Run Analysis", command=self.run_analysis).pack(side="left", padx=5)
        Button(self.options_frame, text="Save", command=self.save_analysis).pack(side="left", padx=5)

    def run_analysis(self):
        """Exécute l'analyse et affiche les plots et les statistiques."""
        if hasattr(self, "notebook") and self.notebook is not None:
            self.notebook.destroy()
            self.notebook = None

        # Créer le notebook
        self.notebook = Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        if self.p_barchart.get():
            # Barchart tab
            self.barchart_plot_frame = Frame(self.notebook)
            self.notebook.add(self.barchart_plot_frame, text="Barchart")
            # Création du bloc d'options + plot dans ce tab
            self.create_barchart_tab()

        if self.p_stats.get():
            # Stats tab
            self.stats_display_frame = Frame(self.notebook)
            self.notebook.add(self.stats_display_frame, text="Statistics parameters")
            # Remplir le tab stats
            self.display_stats(self.stats_display_frame)

        if self.p_data.get():
            # Data tab
            self.data_display_frame = Frame(self.notebook)
            self.notebook.add(self.data_display_frame, text="Data")
            self.display_data(self.data_display_frame)
        
 
        
    
    def save_analysis(self):
        """Exécute l'analyse et affiche les plots."""
        """Sauvegarde la figure."""
        default_path = os.getcwd().replace("tkinter","data_analysis/new")
        
        if not os.path.exists(default_path):
            default_path = os.getcwd()
        
        directory = filedialog.askdirectory(initialdir=default_path)
        
        
        if directory:
            if self.p_barchart.get():
                self.save_barchart(directory,self.options_frame)#self.barchart_plot_frame)  # Passer le frame cible
            if self.p_stats.get():
                self.save_stats(directory,self.options_frame)#self.stats_display_frame)
            if self.p_data.get():
                self.save_data(directory,self.options_frame)#self.data_display_frame)
            
    

    def create_barchart_tab(self):

        #frame = Frame(self.notebook)
        # self.notebook.add(frame, text="Barchart")
    
        # ----- ZONE CONTROLES -----
        control_frame = Frame(self.barchart_plot_frame)
        control_frame.pack(side="top", fill="x")
    
        # Checkboxes
        self.check_vars = {}
        check_frame = Frame(control_frame)
        check_frame.pack()
    
        for key, dic in self.dataframes_to_process.items():
            var = BooleanVar(master = self, value=True)
            self.check_vars[key] = var
            Checkbutton(check_frame, text=key, variable=var).pack(side = "left")
    
        # Nombre d'intervalles
        Label(control_frame, text="Nb intervals:").pack(side="bottom")
        self.entry_intervals = Entry(control_frame, width=5)
        self.entry_intervals.insert(0, "10")
        self.entry_intervals.pack(side="bottom", padx=5)
    
        # Bouton update
        Button(control_frame, text="Update", command=self.update_barchart).pack(side="right", padx=10)
    
        # ----- ZONE PLOT -----
        self.plot_frame_barchart = Frame(self.barchart_plot_frame)
        self.plot_frame_barchart.pack(fill="both", expand=True)   

    
    def get_selected_lines_from_df(self):
        """Retourne un DataFrame filtré avec uniquement les lignes cochées."""
        if not hasattr(self, "lines_df"):
            return pd.DataFrame()  # rien à tracer
        
        # On copie uniquement les lignes cochées
        selected_lines = self.lines_df[self.lines_df["selected"].apply(lambda var: var.get() if isinstance(var, BooleanVar) else bool(var))]
        return selected_lines
    
    
    

    # def plot_barcharts(self,frame):
    #     """Trace les histogrammes de comptage d'échantillons."""
    #     print("PROCESS:")
    #     print(self.dataframes_to_process.keys())
    #     envt_dic = self.dataframes_to_process["envt"]
        
        
    #     for i, line in self.dataframes_selected.iterows():
    #         df = line["df"]
            
        
        
    #     print("ENVT DIC")
    #     print(envt_dic.keys())
    #     envt_df = envt_dic["df"]
    #     envt_measure = envt_dic["measure"]
    #     envt_id = envt_dic["id"]
    #     envt_instrument = envt_dic["instrument"]
        
    #     envt_min = envt_df[envt_measure].min()
    #     envt_max = envt_df[envt_measure].max()
    #     envt_bins = np.linspace(envt_min, envt_max, self.nb_interval)
    #     envt_centers = (envt_bins[:-1] + envt_bins[1:]) / 2
    
    #     envt_counts = [
    #         ((envt_df[envt_measure] >= envt_bins[i]) &
    #           (envt_df[envt_measure] < envt_bins[i+1])).sum()
    #         for i in range(len(envt_bins)-1)]

    #     fig, ax = plt.subplots(figsize=(8, 4))
    #     self.figure_barchart = fig
    #     ax.bar(envt_centers, envt_counts, width=envt_bins[1]-envt_bins[0], align="center", alpha=0.7, edgecolor="black")
    #     ax.set_xlabel(envt_measure)
    #     ax.set_ylabel("Number of samples")
    #     ax.set_title(f"Sample counts per {envt_measure} bin ({envt_instrument} ID {envt_id})")
    #     ax.grid(True, axis="y", linestyle="--", alpha=0.6)
    #     # canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
    #     # canvas.draw()
    #     # canvas.get_tk_widget().pack(fill="both", expand=True)
    #     # plt.close(fig)
    #     canvas = FigureCanvasTkAgg(fig, master=frame)  # Utiliser le frame passé en argument
    #     canvas.draw()
    #     canvas.get_tk_widget().pack(fill="both", expand=True)
    #     plt.close(fig)
       
    def update_barchart(self):
        """Met à jour le barchart selon les checkboxes et le nombre d'intervalles."""
        # Récupérer le nombre d'intervalles
        try:
            self.nb_interval = int(self.entry_intervals.get())
        except ValueError:
            self.nb_interval = 10
    
        # Filtrer selon les checkboxes
        self.data_selected = {
            k: v for k, v in self.dataframes_to_process.items() if self.check_vars[k].get()
        }
        
        #print("DATA SELECTED",self.data_selected)
    
        # Effacer ancien plot
        for widget in self.plot_frame_barchart.winfo_children():
            widget.destroy()
    
        # Appeler le plotting
        self.plot_barcharts(self.plot_frame_barchart)
    
    
    # def plot_barcharts(self, frame):
    #     """Trace les histogrammes pour les lignes sélectionnées dans les checkboxes."""
    #     if not hasattr(self, "data_selected") or not self.data_selected:
    #         print("Aucune ligne sélectionnée pour le barchart.")
    #         return
    
    #     # Calculer min et max global sur toutes les séries sélectionnées
    #     all_values = np.concatenate([
    #         v["df"][v["measure"]].dropna().values for v in self.data_selected.values()
    #     ])
    #     global_min = all_values.min()
    #     global_max = all_values.max()
    
    #     bins = np.linspace(global_min, global_max, self.nb_interval)
    #     bin_width = bins[1] - bins[0]
    #     centers = (bins[:-1] + bins[1:]) / 2
    
    #     fig, ax = plt.subplots(figsize=(8, 4))
    #     self.figure_barchart = fig
    
    #     # Tracer chaque ligne sélectionnée
    #     for key, line in self.data_selected.items():
    #         df = line["df"]
    #         measure = line["measure"]
    #         instrument = line.get("instrument", "Unknown")
    #         id_val = line.get("id", "Unknown")
    
    #         counts = [
    #             ((df[measure] >= bins[i]) & (df[measure] < bins[i+1])).sum()
    #             for i in range(len(bins)-1)
    #         ]
    
    #         ax.bar(centers, counts, width=bin_width, alpha=0.5, edgecolor="black",
    #                label=f"{measure}_{instrument}_{id_val}")
    
    #     ax.set_xlabel("Value")
    #     ax.set_ylabel("Number of samples")
    #     ax.set_title("Sample counts per bin")
    #     ax.grid(True, axis="y", linestyle="--", alpha=0.6)
    #     ax.legend()
    
    #     canvas = FigureCanvasTkAgg(fig, master=frame)
    #     canvas.draw()
    #     canvas.get_tk_widget().pack(fill="both", expand=True)
    #     plt.close(fig)
            
    def plot_barcharts(self, frame):
        if not hasattr(self, "data_selected") or not self.data_selected:
            print("Aucune ligne sélectionnée pour le barchart.")
            return
    
        # Calcul min/max global
        all_values = np.concatenate([v["df"][v["measure"]].dropna().values
                                     for k, v in self.data_selected.items()])
        global_min = all_values.min()
        global_max = all_values.max()
        bins = np.linspace(global_min, global_max, self.nb_interval)
        bin_width_total = bins[1] - bins[0]
        n_series = len(self.data_selected)
        bar_width = bin_width_total / n_series
        centers = (bins[:-1] + bins[1:]) / 2
    
        fig, ax = plt.subplots(figsize=(8, 4))
        self.figure_barchart = fig
    
        for i, (key, line) in enumerate(self.data_selected.items()):
            df = line["df"]
            measure = line["measure"]
            instrument = line.get("instrument", "Unknown")
            id_val = line.get("id", "Unknown")
    
            counts = [( (df[measure] >= bins[j]) & (df[measure] < bins[j+1]) ).sum()
                      for j in range(len(bins)-1)]
    
            # Décalage horizontal pour grouped bars
            offset = i * bar_width
            ax.bar(centers + offset - (bar_width*(n_series-1)/2), counts,
                   width=bar_width, alpha=0.7, edgecolor="black",
                   label=f"{measure}_{instrument}_{id_val}")
    
        ax.set_xlabel("Value")
        ax.set_ylabel("Number of samples")
        ax.set_title("Sample counts per bin")
        ax.grid(True, axis="y", linestyle="--", alpha=0.6)
        ax.legend()
    
        # Canvas
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
     
        
       
 

    def display_stats(self,frame):
        """Affiche les statistiques pour chaque combinaison (référence, ligne)."""
        print("START DISPLAY STATS")
    
        # Liste pour stocker tous les DataFrames de statistiques
        all_stats_dfs = []
        for i, data_i in self.dataframes_to_process.items():
            line_df = data_i["df"]
            line_instrument = data_i.get("instrument", "unknown")
            line_id = data_i.get("id", "unknown")
            line_measure = data_i.get("measure", "unknown")
            line_df_renamed = line_df.rename(columns={line_measure: f"{line_instrument}_{line_id}_{line_measure}"})
            stats_df = self.compute_stats(line_df_renamed)
            #print(stats_df)
            if stats_df is not None and not stats_df.empty:
                instrument_map = {
                    "rabbit": "R",
                    "innova": "I",
                    "meteo_station": "MS",
                    "SAIS": "SAIS",
                }
                
             
                line_instrument_abbr = instrument_map.get(line_instrument, line_instrument)
                stats_df["Line n°"] = i
                stats_df["instrument"] = f"{line_instrument_abbr}_{line_id}_{line_measure}"
                 
                all_stats_dfs.append(stats_df)  # Ajouter à la liste
        
        # Afficher toutes les statistiques accumulées
        if all_stats_dfs:
            combined_stats_df = pd.concat(all_stats_dfs, ignore_index=True)
            self._display_stats(frame,combined_stats_df)
        else:
            print("Aucune statistique à afficher.")
    
        print("END DISPLAY STATS")
    
       
    
    
    def compute_stats(self, df):
        """
        Calcule les statistiques entre les deux premières colonnes de mesures du DataFrame.
        La première colonne est considérée comme référence, la seconde comme 'other'.
        """
        
        def autocorrelation(signal, max_lag):
            signal = np.asarray(signal)
            signal = signal - np.nanmean(signal)
        
            autocorr = []
            for lag in range(max_lag + 1):
                if lag == 0:
                    autocorr.append(1.0)
                else:
                    valid = ~np.isnan(signal[:-lag]) & ~np.isnan(signal[lag:])
                    if valid.sum() == 0:
                        autocorr.append(np.nan)
                    else:
                        c = np.corrcoef(signal[:-lag][valid], signal[lag:][valid])[0, 1]
                        autocorr.append(c)
        
            return np.array(autocorr)
        
        def characteristic_time(autocorr, dt, threshold=1/np.e):
            for i, r in enumerate(autocorr):
                if r <= threshold:
                    return i * dt /60
            return np.nan
        
        # Récupérer les colonnes hors datetime
        measure_col = [c for c in df.columns if c != "datetime"]
        print(measure_col)
        # Il faut au moins 2 colonnes
        # if len(measure_col) < 2:
        #     print("Pas assez de colonnes pour calculer les stats.")
        #     return pd.DataFrame()
    
       
        x = df[measure_col].values
     
    
        # Mask valid values
        mask = ~np.isnan(x) 
        if mask.sum() == 0:
            print("Aucune donnée valide après filtrage NaN.")
            return pd.DataFrame()
    
        x_valid = x[mask]
        
    
        # Calcul statistiques
        mean = np.mean(x_valid)
        median = np.median(x_valid)
        autocorr = autocorrelation(x_valid, max_lag=100)
        dt = (df["datetime"].sort_values().diff().dropna().dt.total_seconds().mean())
        print("autocorr",autocorr)
        print("dt",dt)
        time_e = characteristic_time(autocorr, dt, threshold=1/np.e)
        time_0 = characteristic_time(autocorr, dt, threshold=0)
        return pd.DataFrame([{
            "mean": mean,
            "median": median,
            "autocorr_tau_1/e": time_e,
            "autocorr_tau_0": time_0
        }])
 

    def _display_stats(self, frame, stats_df):
        """Affiche les statistiques dans le Treeview."""
        # Effacer les anciennes données
        for widget in frame.winfo_children():
            widget.destroy()

        if stats_df is not None and not stats_df.empty:
            # Créer le Treeview avec une hauteur limitée
            self.stats_tree = Treeview(frame, columns=("Line n°", "instrument", "mean", "median", "autocor 0 tau","autocor 1/e tau"), show="headings", height=5)
            
            # Configurer les en-têtes
            self.stats_tree.heading("Line n°", text="Line n°")
            self.stats_tree.heading("instrument", text="Instrument")
            self.stats_tree.heading("mean", text="Mean")
            self.stats_tree.heading("median", text="Median")
            self.stats_tree.heading("autocor 0 tau", text="autocor tau_0 (mn)")
            self.stats_tree.heading("autocor 1/e tau", text="autocor tau_1/e (mn)")
            

            # Configurer les colonnes
            self.stats_tree.column("Line n°", width=100)
            self.stats_tree.column("instrument", width=100)
            self.stats_tree.column("mean", width=60)
            self.stats_tree.column("median", width=60)
            self.stats_tree.column("autocor 0 tau", width=60)
            self.stats_tree.column("autocor 1/e tau", width=80)
            
            

            self.stats_tree.pack(fill="x", expand=False)

            # Insérer les données
            for _, row in stats_df.iterrows():
                self.stats_tree.insert("", "end", values=(
                    row["Line n°"],
                    row["instrument"],
                    f"{row['mean']:.4f}",
                    f"{row['median']:.4f}",
                    f"{row['autocorr_tau_0']:.4f}",
                    f"{row['autocorr_tau_1/e']:.4f}",
                    
                ))
        else:
            print("Aucune donnée statistique à afficher")


    def display_data(self,frame):
        """Affiche toutes les données dans un Treeview avec défilement horizontal et vertical."""
        # Effacer les anciens widgets
        for widget in frame.winfo_children():
            widget.destroy()
    
        # Créer un conteneur pour le Treeview et les barres de défilement
        container = Frame(frame)
        container.pack(fill="both", expand=True)
    
        # Créer le Treeview
        tree = Treeview(container, show="headings")  # Masquer la colonne vide
    
        # Barres de défilement
        vsb = Scrollbar(container, orient="vertical", command=tree.yview)
        hsb = Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    
        # Pack les widgets
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        tree.pack(side="left", fill="both", expand=True)
    
        # Liste pour stocker les noms des colonnes
        columns = ["datetime"]
    
        # Dictionnaire pour stocker les DataFrames par instrument/ID/measure
        data_dict = {}
    
        # 1. Collecter toutes les colonnes possibles
        for key, data in self.dataframes_to_process.items():
            if isinstance(data, dict) and "df" in data:
                df = data["df"]
                instrument = data.get("instrument", "Unknown")
                id_val = data.get("id", "Unknown")
    
                for measure in [c for c in df.columns if c != "datetime"]:
                    col_name = f"{measure}_{instrument}_{id_val}"
                    if col_name not in columns:
                        columns.append(col_name)
    
        # Configurer les colonnes du Treeview
        tree["columns"] = columns
        for col in columns:
            tree.column(col, width=120, anchor="w")
            tree.heading(col, text=col)
    
        # 2. Collecter tous les timestamps uniques
        all_timestamps = set()
        for key, data in self.dataframes_to_process.items():
            if isinstance(data, dict) and "df" in data:
                df = data["df"]
                for timestamp in df["datetime"]:
                    all_timestamps.add(timestamp)
    
        # Trier les timestamps
        sorted_timestamps = sorted(all_timestamps)
    
        # 3. Remplir le Treeview
        for timestamp in sorted_timestamps:
            values = {col: "" for col in columns}
            values["datetime"] = timestamp
    
            for key, data in self.dataframes_to_process.items():
                if isinstance(data, dict) and "df" in data:
                    df = data["df"]
                    instrument = data.get("instrument", "Unknown")
                    id_val = data.get("id", "Unknown")
    
                    for measure in [c for c in df.columns if c != "datetime"]:
                        col_name = f"{measure}_{instrument}_{id_val}"
                        row = df[df["datetime"] == timestamp]
                        if not row.empty:
                            values[col_name] = row[measure].values[0]
    
            tree.insert("", "end", values=list(values[col] for col in columns))
    
        # Forcer une largeur minimale pour activer le défilement horizontal
        for col in columns:
            tree.column(col, minwidth=120, width=120)
    
    


    
    def save_data(self, directory,frame):
        print("save_data")
        if directory:
            # Demander le nom du fichier via une boîte de dialogue simple
            filename = simpledialog.askstring("Nom du fichier", "Enter the file name for the  (.csv):", parent=frame, initialvalue="data_csv")
            if filename:
                filename = os.path.join(directory, filename + ".csv")
               
            if filename:
                # Créer un DataFrame combiné avec toutes les données
                combined_df = pd.DataFrame()   
                for key, data in self.dataframes_to_process.items():
                    if isinstance(data, dict) and "df" in data:
                        df = data["df"]
                        if df is not None and not df.empty:
                            instrument = data.get("instrument", "Unknown")
                            id_val = data.get("id", "Unknown")
                            for col in df.columns:
                                if col != "datetime":
                                    measure = col
                                    # Renommer les colonnes pour inclure l'instrument et l'ID
                                    new_col_name = f"{measure}_{instrument}_{id_val}"
                                    df = df.rename(columns={col: new_col_name})
    
                            # Fusionner les DataFrames
                            if combined_df.empty:
                                combined_df = df
                            else:
                                combined_df = pd.merge(combined_df, df, on="datetime", how="outer")
                # Sauvegarder le DataFrame combiné
                combined_df.to_csv(filename, sep =";", index=False)
                print(f"Données sauvegardées sous : {filename}")
    

        
               
    def save_stats(self, directory, frame):
        """Sauvegarde le contenu d'un Treeview dans un fichier CSV."""
        print("save_stats")
        
        treeview =  self.stats_tree
        if treeview is None:
            print("No Treeview to save")
            return
    
        
        if directory:
            # Demander le nom du fichier via une boîte de dialogue simple
            filename = simpledialog.askstring("Filename", "Enter the file name for the stats (.csv):", parent=frame, initialvalue="stats_csv")
            if filename:
                filename = os.path.join(directory, filename + ".csv")
            if not filename:
                return
           
        
            # Récupérer les colonnes du Treeview
            columns = treeview["columns"]
        
            # Ouvrir le fichier CSV en écriture
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, delimiter =";")
        
                # Écrire l'en-tête
                writer.writerow(columns)
        
                # Écrire les données
                for item in treeview.get_children():
                    values = []
                    for col in columns:
                        value = treeview.item(item, 'values')[treeview["columns"].index(col)]
                        values.append(value)
                    writer.writerow(values)
        
            print(f"Données du Treeview sauvegardées sous : {filename}")
        
    def save_barchart(self, directory, frame):
        """Sauvegarde la figure actuelle."""
        print("save plot normal")
        if hasattr(self, 'figure_barchart'):
            if directory:
                # Demander le nom du fichier via une boîte de dialogue simple
                filename = simpledialog.askstring("Filename", "Enter the file name for the barchart plot (.png):", parent=frame, initialvalue="barchart")
                if filename:
                    filename = os.path.join(directory, filename + ".png")
                    self.figure_barchart.savefig(filename, dpi=300, bbox_inches='tight')
                    print(f"Figure sauvegardée sous : {filename}")
                
        else:
            print("Aucune figure à sauvegarder.")
        
    
  
        