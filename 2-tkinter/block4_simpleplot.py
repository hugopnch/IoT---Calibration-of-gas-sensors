# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 10:17:37 2025

@author: titou
"""

from tkinter import Frame, Label, Button, Checkbutton, filedialog,BooleanVar, DISABLED, NORMAL,Scrollbar, Canvas,simpledialog
from tkinter.ttk import Treeview,Notebook
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import os


class Block4SimplePlot(Frame):
    def __init__(self, parent, dataframes_to_process):
        super().__init__(parent)

        # Variables pour les options
        self.p_figure = BooleanVar(master =self,value=True)
        self.p_data = BooleanVar(master = self,value=False)
        

        # Frame pour les options
        self.options_frame = Frame(self)
        self.options_frame.pack(fill="x", padx=10, pady=5)

        # Frame pour les plots
        # self.plot_frame = Frame(self)
        # self.plot_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Remplacer self.plot_frame par un Notebook
        self.notebook = Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.normal_plot_frame = Frame(self.notebook)
        self.data_display_frame = Frame(self.notebook)
        
        self.notebook.add(self.normal_plot_frame, text="Normal Plot")
        self.notebook.add(self.data_display_frame, text="Data")

        # Données
        self.dataframes_to_process = dataframes_to_process
       

        self.create_widgets()

    def create_widgets(self):
        """Crée les widgets d'interface."""
        # Options de plot
        Checkbutton(self.options_frame, text="Figure", variable=self.p_figure).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Data", variable=self.p_data).pack(side="left", padx=5)

        

        # Bouton pour exécuter l'analyse
        Button(self.options_frame, text="Plot", command=self.run_analysis).pack(side="left", padx=5)
        Button(self.options_frame, text="Save", command=self.save_analysis).pack(side="left", padx=5)

    def run_analysis(self):
        """Exécute l'analyse et affiche les plots."""
        # Effacer les anciens plots
        for widget in self.normal_plot_frame.winfo_children():
            widget.destroy()


        if self.p_figure.get():
            self.plot_normal(self.normal_plot_frame)
        if self.p_data.get():
            self.display_data(self.data_display_frame)
        # # Sauvegarder si nécessaire
        # if self.s_figure.get():
        #     self.save_figure(fig)
            
    def save_analysis(self):
        """Exécute l'analyse et affiche les plots."""
        """Sauvegarde la figure."""
        
        default_path = os.getcwd().replace("tkinter","data_analysis/new")
        
        if not os.path.exists(default_path):
            default_path = os.getcwd()
        
        directory = filedialog.askdirectory(initialdir=default_path)
        
        if directory:
            if self.p_figure.get():
                self.save_plot_normal(directory,self.normal_plot_frame)
            if self.p_data.get():
                self.save_data(directory,self.data_display_frame)
            



      

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
            
   
    
            
    def save_plot_normal(self, directory, frame):
        """Sauvegarde la figure actuelle."""
        print("save plot normal")
        if hasattr(self, 'figure_plot'):
            if directory:
                # Demander le nom du fichier via une boîte de dialogue simple
                filename = simpledialog.askstring("Nom du fichier", "Enter the file name for the normal plot (.png):", parent=frame, initialvalue="figure")
                if filename:
                    filename = os.path.join(directory, filename + ".png")
                    self.figure_plot.savefig(filename, dpi=300, bbox_inches='tight')
                    print(f"Figure sauvegardée sous : {filename}")
                
        else:
            print("Aucune figure à sauvegarder.")
    
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

    def plot_normal(self, frame):
    
        """
        Trace les données avec :
        - titre centré sur la figure entière,
        - légende centrée sur la zone des courbes,
        - marges haut/bas optimisées pour Tkinter.
        """
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        import matplotlib.colors as mcolors
    
        # --- Label d'axe selon la mesure ---
        def legend_axis(measure):
            m = measure.lower()
            if m in ["temperature", "dew_point", "wet_bulb"]:
                return f"{measure.capitalize()} (°C)"
            elif m in ["humidity", "umidity"]:
                return "Humidity (%)"
            elif m == "wind_dir":
                return "Wind direction (°)"
            elif m in ["wind_gust", "wind_speed"]:
                return f"{measure} (m/s)"
            else:
                return f"{measure} concentration"
    
        # --- Regrouper les données par mesure ---
        groups = {}
        for key, data in self.dataframes_to_process.items():
            if isinstance(data, dict) and "df" in data:
                df = data["df"]
                for col in df.columns:
                    if col != "datetime":
                        measure = col
                        groups.setdefault(measure, []).append({
                            "key": key,
                            "data": data,
                            "df": df,
                            "measure": measure,
                            "instrument": data.get("instrument", "Unknown"),
                            "id": data.get("id", "Unknown")
                        })
    
        if not groups:
            return
    
        # --- Figure ---
        fig, ax = plt.subplots(constrained_layout=False)
        self.figure_plot = fig
        axes = {list(groups.keys())[0]: ax}
    
        offset_step = 0.2
        all_colors = list(mcolors.TABLEAU_COLORS.keys())
        linestyle_list = ["-", ":", "--", "-."]
    
        # --- Création des axes secondaires ---
        for i, measure in enumerate(groups.keys()):
            if i > 0:
                axes[measure] = ax.twinx()
                axes[measure].spines["right"].set_position(("axes", 1 + (i - 1) * offset_step))
            axes[measure].set_ylabel(legend_axis(measure), fontsize=9)
            axes[measure].tick_params(axis="y", labelsize=8)
    
        # --- Tracé des courbes ---
        color_idx, style_idx = 0, 0
        for measure, group_data in groups.items():
            linestyle = linestyle_list[style_idx % len(linestyle_list)]
            style_idx += 1
            for data_info in group_data:
                color = all_colors[color_idx % len(all_colors)]
                color_idx += 1
    
                instrument_map = {"rabbit": "R", "innova": "I", "meteo_station": "MS"}
                inst = instrument_map.get(data_info["instrument"], data_info["instrument"])
                df = data_info["df"]
                axes[measure].plot(
                    df["datetime"],
                    df[data_info["measure"]],
                    label=f"{data_info['measure']} {data_info['instrument']} {data_info['id']}",
                    color=color,
                    linestyle=linestyle,
                    linewidth=1.0
                )
    
       
        # --- Formatage axe X ---
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%y-%m-%d %H:%M"))
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
        ax.set_xlabel("Time", fontsize=9)
    
        # --- Récupérer handles et labels ---
        handles, labels = [], []
        for ax_i in axes.values():
            h, l = ax_i.get_legend_handles_labels()
            handles.extend(h)
            labels.extend(l)
    
        # --- Légende centrée sur la zone de courbes ---
        # `bbox_transform=ax.transAxes` => ancre dans le repère des axes (pas de la figure)
        n_labels = len(labels)
        
        
        if n_labels <= 2:
            fontsize = 12
            handlelength = 2.0
            ncol = n_labels
            y_anchor = 1.15
        elif n_labels <= 6:
            fontsize = 12
            handlelength = 2.0
            ncol = 3
            y_anchor = 1.15
        else:
            fontsize = 12
            handlelength = 2.0
            ncol = 4
            y_anchor = 1.2
        
        if handles:
            leg = ax.legend(
                handles, labels,
                loc='upper center',
                bbox_to_anchor=(0.5, y_anchor),  # au-dessus des courbes, bien centrée
                bbox_transform=ax.transAxes,  # centré sur le graphe, pas la figure
                ncol=ncol,
                fontsize= fontsize,#8,
                handlelength=handlelength,   #1.2,
                frameon=True,
                borderpad=0.3,
                labelspacing=0.3
            )
    
        # --- Titre centré sur la figure entière ---
        #fig.suptitle("Simple Plot Analysis", y=0.97, fontsize=11, weight="bold", ha="center")
    
        # --- Ajustement marges ---
        plt.subplots_adjust(top=0.95, bottom=0.12)  # réduit marge bas
        plt.tight_layout(rect=[0, 0, 1, 0.88])      # garde tout visible
    
        # --- Affichage Tkinter ---
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        
        # legend_bbox = leg.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
        # legend_top = legend_bbox.y1  # coordonnée top de la légende en fraction de figure
        
        # # On place le titre juste au-dessus de la légende
        # ax.set_title("Simple Plot Analysis", fontsize=11, weight="bold",
        #              y=legend_top + 0.01)  # décalage minimal au-dessus
        
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
        
