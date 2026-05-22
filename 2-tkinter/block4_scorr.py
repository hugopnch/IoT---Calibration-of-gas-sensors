# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 10:19:37 2025

@author: titou
"""


from tkinter import Frame, Label, Button, Checkbutton, BooleanVar, filedialog, DISABLED, NORMAL,Scrollbar,simpledialog
from tkinter.ttk import Treeview,Notebook
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.dates as mdates
import os
import csv

class Block4SCorr(Frame):
    def __init__(self, parent, dataframes_to_process):
        super().__init__(parent)

        # Variables pour les options
        self.p_figure = BooleanVar(master = self,value=True)
        self.p_cross_corr = BooleanVar(master = self,value=True)
        self.p_stats = BooleanVar(master = self,value=True)
        self.p_data = BooleanVar(master = self, value=False)
        

        # Frame pour les options
        self.options_frame = Frame(self)
        self.options_frame.pack(fill="x", padx=10, pady=5)

        # # Frame pour les statistiques
        # self.stats_frame = Frame(self)
        # self.stats_frame.pack(fill="x", padx=10, pady=5)

        # # Frame pour les plots
        # self.plot_frame = Frame(self)
        # self.plot_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Remplacer self.plot_frame par un Notebook
        self.notebook = Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
    
        # Créer un onglet pour chaque type de plot
        self.normal_plot_frame = Frame(self.notebook)
        self.cross_corr_plot_frame = Frame(self.notebook)
        self.stats_display_frame = Frame(self.notebook)
        self.data_display_frame = Frame(self.notebook)
    
        self.notebook.add(self.normal_plot_frame, text="Normal Plot")
        self.notebook.add(self.cross_corr_plot_frame, text="Cross Corr Plot")
        self.notebook.add(self.stats_display_frame, text="Statistics parameters")
        self.notebook.add(self.data_display_frame, text="Data")

        # Données
        self.dataframes_to_process = dataframes_to_process
        print("dataframes_to_process", self.dataframes_to_process.keys())
        self.create_widgets()

    def create_widgets(self):
        """Crée les widgets d'interface."""
        # Options de plot
        Checkbutton(self.options_frame, text="Plot", variable=self.p_figure).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Cross_corr plot", variable=self.p_cross_corr).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Statistics", variable=self.p_stats).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Data", variable=self.p_data).pack(side="left", padx=5)


        # Bouton pour exécuter l'analyse
        Button(self.options_frame, text="Plot", command=self.run_analysis).pack(side="left", padx=5)
        Button(self.options_frame, text="Save", command=self.save_analysis).pack(side="left", padx=5)

    def run_analysis(self):
        """Exécute l'analyse et affiche les plots et les statistiques."""
        # Effacer les anciens widgets
        for widget in self.normal_plot_frame.winfo_children():
            widget.destroy()
        for widget in self.cross_corr_plot_frame.winfo_children():
            widget.destroy()
        for widget in self.stats_display_frame.winfo_children():
            widget.destroy()
        for widget in self.data_display_frame.winfo_children():
            widget.destroy()
            
        if self.p_figure.get():
            self.plot_normal(self.normal_plot_frame)  # Passer le frame cible
        if self.p_cross_corr.get():
            self.plot_cross_corr(self.cross_corr_plot_frame)  # Passer le frame cible
        if self.p_stats.get():
            self.display_stats(self.stats_display_frame)  # Passer le frame cible
        if self.p_data.get():
            self.display_data(self.data_display_frame)  # Passer le frame cible

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
            if self.p_cross_corr.get():
                self.save_plot_normal(directory,self.normal_plot_frame)
            if self.p_stats.get():
                self.save_stats(directory,self.stats_display_frame)
            if self.p_data.get():
                self.save_data(directory,self.data_display_frame)
     

    def plot_normal(self, frame):
    
        """
        Trace les données avec :
        - titre centré sur la figure entière,
        - légende centrée sur la zone des courbes,
        - marges haut/bas optimisées pour Tkinter.
        """
        
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
    # def plot_normal(self,frame):
        
    #     def legend_axis(measure):
    #         if measure.lower() in ["temperature","dew_point","wet_bulb"]:
    #             return f"{measure.capitalize()} (°C)"
    #         elif measure.lower() in ["humidity","umidity"]:
    #             return "Humidity (%)"
    #         elif measure.lower() == "wind_dir":
    #             return "Wind direction (°)"
    #         elif measure.lower() in ["wind_gust","wind_speed"]:
    #             return f"{measure} (m/s)"
    #         else:
    #             return f"{measure} concentration"
        
    #     # Possible amélioration : creer un axe par "measure" pour ne pas avoir d'échelles distendus
    #     # measures = []
    #     # for key, data in self.dataframes_to_process.items():
    #     #     msr = data["measure"]
    #     #     if msr in measures:
    #     #         continue
    #     #     else:
    #     #         measures.append(msr)
        
    #     # Création d'une figure pour le plot
    #     fig, ax = plt.subplots()
    #     self.figure_plot = fig
    
    #     # Tracer les données
    #     for key, data in self.dataframes_to_process.items():
    #         if isinstance(data, dict) and "df" in data:
    #             df = data["df"]
    #             #print(df[0:20])
    #             if df is not None and not df.empty:
    #                 for col in df.columns:
    #                     if col != "datetime":
    #                         instrument = data.get("instrument", "Unknown")
    #                         id_val = data.get("id", "Unknown")
    #                         measure = col
    #                         ax.plot(df["datetime"], df[col], label=f"{instrument} ID {id_val}, {measure}")
        
        
    #     # Ajustement des abscisses
    #     ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    #     plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        
    #     ax.legend()
    #     ax.set_title("Simple Plot Analysis")
    #     ax.set_xlabel("Time")
    #     ax.set_ylabel("Value")
        
    #     plt.tight_layout()
    
    #     # Afficher le plot
    #     canvas = FigureCanvasTkAgg(fig, master=frame)  # Utiliser le frame passé en argument
    #     canvas.draw()
    #     canvas.get_tk_widget().pack(fill="both", expand=True)
    #     plt.close(fig)

    # def plot_normal_test(self,frame):
    #     """Trace les graphiques normaux."""
    
    #     def legend_axis(measure):
    #         if measure.lower() in ["temperature","dew_point","wet_bulb"]:
    #             return f"{measure.capitalize()} (°C)"
    #         elif measure.lower() in ["humidity","umidity"]:
    #             return "Humidity (%)"
    #         elif measure.lower() == "wind_dir":
    #             return "Wind direction (°)"
    #         elif measure.lower() in ["wind_gust","wind_speed"]:
    #             return f"{measure} (m/s)"
    #         else:
    #             return f"{measure} concentration"
        
        
    #     # Étape 1 : Regrouper les données par mesure
    #     groups = {}
    #     for key, data in self.dataframes_to_process.items():
    #         if isinstance(data, dict) and "df" in data:
    #             df = data["df"]
    #             for col in df.columns:
    #                 if col != "datetime":
    #                     measure = col
    #                     groups.setdefault(measure, []).append({
    #                         "key": key,
    #                         "data": data,
    #                         "df": df,
    #                         "measure": measure,
    #                         "instrument": data.get("instrument", "Unknown"),
    #                         "id": data.get("id", "Unknown")
    #                     })
    
    #     if not groups:
    #         return
        
    #     if len(groups) == 1:
            
            
    #     """Trace les données avec 'envt' à gauche et les autres à droite."""
    #     fig, ax1 = plt.subplots()
    #     self.figure_plot = fig
        
    #     ax2 = ax1.twinx()  # Créer un second axe Y
    #     all_colors = list(mcolors.TABLEAU_COLORS.keys())
    #     non_red_colors = [color for color in all_colors if "red" not in color]
    #     # Parcourir les données
    #     for i,(key, data) in enumerate(self.dataframes_to_process.items()):
    #         if isinstance(data, dict) and "df" in data:
    #             df = data["df"]
    #             if df is not None and not df.empty:
    #                 for col in df.columns:
    #                     if col != "datetime":
    #                         instrument = data.get("instrument", "Unknown")
    #                         id_val = data.get("id", "Unknown")
    #                         measure = col
        
    #                         # Tracer 'envt' sur ax1 (à gauche)
    #                         if key == "envt":
    #                             ax1.plot(df["datetime"], df[col],
    #                                     label=f"{measure} : {instrument} ID {id_val}",color="red",linestyle=":")
    #                             ax1.set_ylabel(legend_axis(measure))# color="blue")
    #                             ax1.tick_params(axis="y")#, labelcolor="blue")
        
    #                         # Tracer les autres sur ax2 (à droite)
    #                         else:
    #                             if key == "ref":
    #                                 linewidth = 1.3
    #                                 linestyle = "--"
    #                             else:
    #                                 linewidth = 0.8
    #                                 linestyle ="-"
    #                             color = non_red_colors[i-1 % len(non_red_colors)]
    #                             ax2.plot(df["datetime"], df[col],
    #                                     label=f"{measure} : {instrument} ID {id_val}" ,linewidth=linewidth, linestyle = linestyle, color=color)
    #                             ax2.set_ylabel(legend_axis(measure))# ,color="red")
    #                             ax2.tick_params(axis="y")#, labelcolor="red")
        
    #     # Ajustement des abscisses
    #     ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    #     plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
        
    #     # Légendes
    #     ax1.legend(loc="upper left")
    #     ax2.legend(loc="upper right")
        
    #     plt.tight_layout()
    #     # Afficher le plot dans Tkinter
    #     # canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
    #     # canvas.draw()
    #     # canvas.get_tk_widget().pack(fill="both", expand=True)   
        
    #     canvas = FigureCanvasTkAgg(fig, master=frame)  # Utiliser le frame passé en argument
    #     canvas.draw()
    #     canvas.get_tk_widget().pack(fill="both", expand=True)
    #     plt.close(fig)         
    
    def plot_cross_corr(self,frame):
        def cross_correlation(ref, other, max_lag):
           """
           Corrélation croisée normalisée entre ref et other
           Retourne lags (en pas de temps) et corrélations
           """
           ref = np.asarray(ref, dtype=float)
           other = np.asarray(other, dtype=float)
       
           # Centrage
           ref -= np.nanmean(ref)
           other -= np.nanmean(other)
       
           lags = np.arange(-max_lag, max_lag + 1)
           corr = np.full(len(lags), np.nan)
       
           for i, lag in enumerate(lags):
               if lag < 0:
                   r = ref[:lag]
                   o = other[-lag:]
               elif lag > 0:
                   r = ref[lag:]
                   o = other[:-lag]
               else:
                   r = ref
                   o = other
       
               valid = ~np.isnan(r) & ~np.isnan(o)
               if valid.sum() < 3:
                   continue
       
               corr[i] = np.corrcoef(r[valid], o[valid])[0, 1]
       
           return lags, corr
       
        def estimate_tau_from_crosscorr(lags, corr, dt):
           """
           Retourne le tau (en secondes) correspondant au maximum de corrélation
           et la valeur du maximum
           """
           if np.all(np.isnan(corr)):
               return np.nan, np.nan
       
           idx = np.nanargmax(corr)
           tau = lags[idx] * dt / 60
           return tau, corr[idx]
        
      
        """Trace les corrélations en fonction des mesures environnementales."""
        print("PLOT CORRELATION VS ENV")
        groups = {"ref" : None, "line": []}
        
        # Regrouper les données par groupe
        for key, data in self.dataframes_to_process.items():
            print("KEY:",key)
            print("DATA:",data.keys())
            
            if isinstance(data, dict) and "df" in data:
                df = data["df"]
                if df is not None and not df.empty:
                    if "ref" in key:
                        groups["ref"] = data
                    if "line" in key:
                        groups["line"].append(data)

        
        ref_df = groups["ref"]["df"]
        ref_measure = groups["ref"]["measure"]
        ref_id = groups["ref"]["id"]
        ref_instrument = groups["ref"]["instrument"]
        measure_ref_col = [c for c in ref_df.columns if c != "datetime"]
        x = ref_df[measure_ref_col]
        
        
        all_cross_corr = []
        for k in range(len(groups["line"])):
         
            line_df = (groups["line"][k])["df"]
            line_measure = (groups["line"][k])["measure"]
            dt = (df["datetime"].sort_values().diff().dropna().dt.total_seconds().mean())
            print("dt",dt)
            print(line_df)
            measure_line_col = [c for c in line_df.columns if c != "datetime"]
            y = line_df[measure_line_col]
            lags, corr = cross_correlation(x,y,max_lag=100)
            #tau, corr_max = estimate_tau_from_crosscorr(lags, corr, dt)
                
            all_cross_corr.append(corr)
            
            
        
        fig, ax = plt.subplots()
        self.figure_corr = fig
        #all_colors = list(mcolors.TABLEAU_COLORS.keys())
        for k in range(len(all_cross_corr)):
            #color = all_colors[k-1 % len(all_colors)]
            line_measure = (groups["line"][k])["measure"]
            line_id = (groups["line"][k])["id"]
            line_instrument = (groups["line"][k])["instrument"]
            tau = [x*dt/60 for x in lags]
            ax.plot(tau, all_cross_corr[k],label = f"{ref_measure}:{ref_instrument} ID {ref_id} // {line_measure}:{line_instrument} ID {line_id} ", marker='o')
        
        # def legend_x_axis(measure):
        #     if measure.lower() in ["temperature","dew_point","wet_bulb"]:
        #         return f"{measure.capitalize()} (°C)"
        #     elif measure.lower() in ["humidity","umidity"]:
        #         return "Humidity (%)"
        #     elif measure.lower() == "wind_dir":
        #         return "Wind direction (°)"
        #     elif measure.lower() in ["wind_gust","wind_speed"]:
        #         return f"{measure} (m/s)"
        #     else:
        #         return f"{measure} concentration"
        
        ax.set_xlabel("Tau (min)")
        #ax.set_xlabel(legend_x_axis(envt_measure))
        ax.set_ylabel("Cross Correlation")
        ax.set_title(f"Cross correlation of {ref_measure}  ({ref_measure} ID:{ref_id}) between instruments")
        ax.grid(True)
        ax.legend()
        
        plt.tight_layout()
        # canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        # canvas.draw()
        # canvas.get_tk_widget().pack(fill="both", expand=True)
        # plt.close(fig)
        canvas = FigureCanvasTkAgg(fig, master=frame)  # Utiliser le frame passé en argument
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
          
        
    
    
    
    def display_stats(self,frame):
        """Affiche les statistiques pour chaque combinaison (référence, ligne)."""
        print("START DISPLAY STATS")
    
        # Liste pour stocker tous les DataFrames de statistiques
        all_stats_dfs = []
    
        # Récupérer la référence
        ref_dic = self.dataframes_to_process["ref"]
        ref_df = ref_dic["df"]
        ref_instrument = ref_dic.get("instrument", "unknown")
        ref_id = ref_dic.get("id", "unknown")
        ref_measure = ref_dic.get("measure", "unknown")
    
        # Renommer la colonne de mesure de référence
        ref_col_name = f"ref_{ref_id}_{ref_measure}"
        ref_df_renamed = ref_df.rename(columns={ref_measure: ref_col_name})
    
        # Traiter chaque ligne (ligne1, ligne2, ...) avec la référence
        for key, data in list(self.dataframes_to_process.items())[1:]:
            print(f"\nTraitement de la ligne: {key}")
            if isinstance(data, dict) and "df" in data:
                other_df = data["df"]
                other_instrument = data.get("instrument", "unknown")
                other_id = data.get("id", "unknown")
                other_measure = data.get("measure", "unknown")
    
                # Renommer la colonne de mesure "other"
                other_col_name = f"other_{other_id}_{other_measure}"
                other_df_renamed = other_df.rename(columns={other_measure: other_col_name})
    
                # Fusionner les DataFrames
                merged_df = pd.merge(ref_df_renamed, other_df_renamed, on="datetime", how="inner")
                if merged_df.empty:
                    print(f"Aucune correspondance pour {key} ! Vérifiez les datetime.")
                    continue
    
                # Calculer les statistiques
                stats_df = self.compute_stats(merged_df)
                if stats_df is not None and not stats_df.empty:
                    instrument_map = {
                        "rabbit": "R",
                        "innova": "I",
                        "meteo_station": "MS",
                    }
                    ref_instrument_abbr = instrument_map.get(ref_instrument, ref_instrument)
                    other_instrument_abbr = instrument_map.get(other_instrument, other_instrument)
    
                    stats_df["reference"] = f"{ref_instrument_abbr}_{ref_id}_{ref_measure}"
                    stats_df["instrument"] = f"{other_instrument_abbr}_{other_id}_{other_measure}"
    
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
        Calcule les statistiques pour chaque paire de colonnes où une colonne commence par "ref_"
        et l'autre par "other_". Retourne un DataFrame avec les indicateurs statistiques.
        """
        def cross_correlation(ref, other, max_lag):
            """
            Corrélation croisée normalisée entre ref et other
            Retourne lags (en pas de temps) et corrélations
            """
            ref = np.asarray(ref, dtype=float)
            other = np.asarray(other, dtype=float)
        
            # Centrage
            ref -= np.nanmean(ref)
            other -= np.nanmean(other)
        
            lags = np.arange(-max_lag, max_lag + 1)
            corr = np.full(len(lags), np.nan)
        
            for i, lag in enumerate(lags):
                if lag < 0:
                    r = ref[:lag]
                    o = other[-lag:]
                elif lag > 0:
                    r = ref[lag:]
                    o = other[:-lag]
                else:
                    r = ref
                    o = other
        
                valid = ~np.isnan(r) & ~np.isnan(o)
                if valid.sum() < 3:
                    continue
        
                corr[i] = np.corrcoef(r[valid], o[valid])[0, 1]
        
            return lags, corr
        
        def estimate_tau_from_crosscorr(lags, corr, dt):
            """
            Retourne le tau (en secondes) correspondant au maximum de corrélation
            et la valeur du maximum
            """
            if np.all(np.isnan(corr)):
                return np.nan, np.nan
        
            idx = np.nanargmax(corr)
            tau = lags[idx] * dt / 60
            return tau, corr[idx]
        
        def estimate_near_zero_extremum(lags, corr, dt, max_lag_near0=50):
            """
            Retourne l'extrémum (max ou min) le plus proche de lag=0
            dans une fenêtre |lag| <= max_lag_near0
            """
            if corr is None or np.all(np.isnan(corr)):
                return np.nan, np.nan
        
            mask = np.abs(lags) <= max_lag_near0
            if not np.any(mask):
                return np.nan, np.nan
        
            lags_sel = lags[mask]
            corr_sel = corr[mask]
        
            # Max et min
            idx_max = np.nanargmax(corr_sel)
            idx_min = np.nanargmin(corr_sel)
        
            lag_max = lags_sel[idx_max]
            lag_min = lags_sel[idx_min]
        
            # Choisir l'extrémum le plus proche de 0
            if abs(lag_max) <= abs(lag_min):
                tau = lag_max * dt / 60
                corr_val = corr_sel[idx_max]
            else:
                tau = lag_min * dt / 60
                corr_val = corr_sel[idx_min]
        
            return tau, corr_val
        
        
        results = []
        measure_cols = [col for col in df.columns if col not in ["datetime"]]
    
        # Identifier les colonnes de référence (commencent par "ref_")
        ref_cols = [col for col in measure_cols if col.startswith("ref_")]
        print("REF COLS:", ref_cols)
    
        # Identifier les colonnes "other" (commencent par "other_")
        other_cols = [col for col in measure_cols if col.startswith("other_")]
        print("OTHER COLS:", other_cols)
        # Comparer chaque colonne de référence avec chaque colonne "other"
        for ref_col in ref_cols:
            for other_col in other_cols:
                x = df[ref_col].values
                y = df[other_col].values
                mask = ~np.isnan(x) & ~np.isnan(y)
                if mask.sum() == 0:
                    continue
                x_valid, y_valid = x[mask], y[mask]
                
                dt = (df["datetime"].sort_values().diff().dropna().dt.total_seconds().mean())
                
                lags, corr = cross_correlation(x_valid,y_valid,max_lag=100)
                tau, corr_max = estimate_tau_from_crosscorr(lags, corr, dt)
                tau0, corr0 = estimate_near_zero_extremum(lags, corr, dt, max_lag_near0=50)
                
                mbe = np.mean(y_valid - x_valid)
                mae = np.mean(np.abs(y_valid - x_valid))
                rmse = np.sqrt(mean_squared_error(x_valid, y_valid))
                r = np.corrcoef(x_valid, y_valid)[0, 1]
                r2 = r**2
                R2 = r2_score(x_valid, y_valid)
                # y_centered = y_valid - mbe
                # r2_centered = r2_score(x_valid, y_centered)
                mean_ratio = np.mean(y_valid) / np.mean(x_valid) if np.mean(x_valid) != 0 else np.nan
                results.append({
                    "reference": ref_col,
                    "instrument": other_col,
                    "tau": tau,
                    "cross_corr_max": corr_max,
                    "extremum_near_0":tau0,
                    "MBE": mbe,
                    "MAE": mae,
                    "RMSE": rmse,
                    "r": r,
                    "r2":r2,
                    "R2": R2,
                    "MeanRatio": mean_ratio
                })
    
        return pd.DataFrame(results) if results else pd.DataFrame(columns=["reference", "instrument","tau","cross_cor_max", "MBE", "MAE", "RMSE", "r", "r2", "R2", "MeanRatio"])

    def _display_stats(self, frame, stats_df):
        """Affiche les statistiques dans le Treeview."""
        # Effacer les anciennes données
        for widget in frame.winfo_children():
            widget.destroy()

        if stats_df is not None and not stats_df.empty:
            # Créer le Treeview avec une hauteur limitée
            self.stats_tree = Treeview(frame, columns=("reference", "instrument","tau","cross_corr_max","extremum_near_0", "MBE", "MAE", "RMSE", "r", "r2", "R2", "MeanRatio"), show="headings", height=5)
            
            # Configurer les en-têtes
            self.stats_tree.heading("reference", text="Reference")
            self.stats_tree.heading("instrument", text="Instrument")
            self.stats_tree.heading("tau", text="tau (mn)")
            self.stats_tree.heading("cross_corr_max", text="cross_corr_max")
            self.stats_tree.heading("extremum_near_0", text="extremum_near_0 (mn)")
            self.stats_tree.heading("MBE", text="MBE")
            self.stats_tree.heading("MAE", text="MAE")
            self.stats_tree.heading("RMSE", text="RMSE")
            self.stats_tree.heading("r", text="r")
            self.stats_tree.heading("r2", text="r²")
            self.stats_tree.heading("R2", text="R²")
            self.stats_tree.heading("MeanRatio", text="Mean Ratio")

            # Configurer les colonnes
            self.stats_tree.column("reference", width=100)
            self.stats_tree.column("instrument", width=100)
            self.stats_tree.column("tau", width=60)
            self.stats_tree.column("cross_corr_max", width=60)
            self.stats_tree.column("extremum_near_0", width=60)
            self.stats_tree.column("MBE", width=60)
            self.stats_tree.column("MAE", width=60)
            self.stats_tree.column("RMSE", width=60)
            self.stats_tree.column("r", width=60)
            self.stats_tree.column("r2", width=60)
            self.stats_tree.column("R2", width=80)
            self.stats_tree.column("MeanRatio", width=80)

            self.stats_tree.pack(fill="x", expand=False)

            # Insérer les données
            for _, row in stats_df.iterrows():
                self.stats_tree.insert("", "end", values=(
                    row["reference"],
                    row["instrument"],
                    f"{row['tau']:.4f}",
                    f"{row['cross_corr_max']:.4f}",
                    f"{row['extremum_near_0']:.4f}",
                    f"{row['MBE']:.4f}",
                    f"{row['MAE']:.4f}",
                    f"{row['RMSE']:.4f}",
                    f"{row['r']:.4f}",
                    f"{row['r2']:.4f}",
                    f"{row['R2']:.4f}",
                    f"{row['MeanRatio']:.4f}"
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
        
        
    