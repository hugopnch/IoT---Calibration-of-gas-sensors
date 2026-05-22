from tkinter import Frame, Label, Button, Checkbutton, BooleanVar, filedialog, DISABLED, NORMAL,Scrollbar,filedialog,simpledialog
from tkinter.ttk import Treeview, Notebook
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.dates as mdates
import matplotlib.colors as mcolors 
import os
import csv

class Block4ECorr(Frame):
    def __init__(self, parent, dataframes_to_process, nb_interval):
        super().__init__(parent)
        
        
        # Variables pour les options
        self.p_figure = BooleanVar(master=self, value= True)
        self.p_ecorr = BooleanVar(master = self, value = True) 
        self.p_autocorr = BooleanVar(master = self, value = True) 
        self.p_barchart = BooleanVar(master=self, value=True)
        self.p_stats = BooleanVar(master=self, value=False)
        self.p_data = BooleanVar(master = self, value = False)
        
    
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
        self.correlation_plot_frame = Frame(self.notebook)
        self.autocorr_plot_frame = Frame(self.notebook)
        self.barchart_plot_frame = Frame(self.notebook)
        self.stats_display_frame = Frame(self.notebook)
        self.data_display_frame = Frame(self.notebook)
    
        self.notebook.add(self.normal_plot_frame, text="Plot")
        self.notebook.add(self.correlation_plot_frame, text="Corr vs Envt Plot")
        self.notebook.add(self.autocorr_plot_frame, text="Autocorr vs Envt Plot")
        self.notebook.add(self.barchart_plot_frame, text="Barchart")
        self.notebook.add(self.stats_display_frame, text="Statistics parameters")
        self.notebook.add(self.data_display_frame, text="Data")

        # Données
        self.dataframes_to_process = dataframes_to_process
        self.nb_interval = nb_interval
        self.create_widgets()

    def create_widgets(self):
        """Crée les widgets d'interface."""
        # Options de plot
        Checkbutton(self.options_frame, text="Plot", variable=self.p_figure).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Corr vs Envt", variable=self.p_ecorr).pack(side="left", padx=5)  # Non utilisé directement
        Checkbutton(self.options_frame, text="Autocorr vs Envt", variable=self.p_autocorr).pack(side="left", padx=5) 
        Checkbutton(self.options_frame, text="Barchart", variable=self.p_barchart).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Statistics", variable=self.p_stats).pack(side="left", padx=5)
        Checkbutton(self.options_frame, text="Data", variable=self.p_data).pack(side="left", padx=5)


        # Bouton pour exécuter l'analyse
        Button(self.options_frame, text="Run Analysis", command=self.run_analysis).pack(side="left", padx=5)
        Button(self.options_frame, text="Save", command=self.save_analysis).pack(side="left", padx=5)

    def run_analysis(self):
        """Exécute l'analyse et affiche les plots et les statistiques."""
        # Effacer les anciens widgets dans chaque onglet
        for widget in self.normal_plot_frame.winfo_children():
            widget.destroy()
        for widget in self.correlation_plot_frame.winfo_children():
            widget.destroy()
        for widget in self.autocorr_plot_frame.winfo_children():
            widget.destroy()
        for widget in self.barchart_plot_frame.winfo_children():
            widget.destroy()
        for widget in self.stats_display_frame.winfo_children():
            widget.destroy()
        for widget in self.data_display_frame.winfo_children():
            widget.destroy()
    
        if self.p_figure.get():
            self.plot_normal(self.normal_plot_frame)  # Passer le frame cible
        if self.p_ecorr.get():
            self.plot_correlation_vs_env(self.correlation_plot_frame)  # Passer le frame cible
        if self.p_autocorr.get():
            self.plot_autocorr_vs_env(self.autocorr_plot_frame)
        if self.p_barchart.get():
            self.plot_barcharts(self.barchart_plot_frame)  # Passer le frame cible
        if self.p_stats.get():
            self.display_stats(self.stats_display_frame)
        if self.p_data.get():
            self.display_data(self.data_display_frame)
        
    
    def save_analysis(self):
        """Exécute l'analyse et affiche les plots."""
        """Sauvegarde la figure."""
        default_path = os.getcwd().replace("tkinter","data_analysis/new")
        
        if not os.path.exists(default_path):
            default_path = os.getcwd()
        
        directory = filedialog.askdirectory(initialdir=default_path)
        
        
        if directory:
            if self.p_figure.get():
                self.save_plot_normal(directory,self.options_frame)#self.normal_plot_frame)
            if self.p_ecorr.get():
                self.save_plot_corr(directory,self.options_frame)#self.correlation_plot_frame)  # Passer le frame cible
            if self.p_autocorr.get():
                self.save_plot_corr(directory,self.options_frame)
            if self.p_barchart.get():
                self.save_barchart(directory,self.options_frame)#self.barchart_plot_frame)  # Passer le frame cible
            if self.p_stats.get():
                self.save_stats(directory,self.options_frame)#self.stats_display_frame)
            if self.p_data.get():
                self.save_data(directory,self.options_frame)#self.data_display_frame)
            
    
    def plot_correlation_vs_env(self,frame):
        """Trace les corrélations en fonction des mesures environnementales."""
        print("PLOT CORRELATION VS ENV")
        groups = {"envt" : None, "ref" : None, "line": []}
        
        # Regrouper les données par groupe
        for key, data in self.dataframes_to_process.items():
            print("KEY:",key)
            print("DATA:",data.keys())
            
            if isinstance(data, dict) and "df" in data:
                df = data["df"]
                if df is not None and not df.empty:
                    
                    if "envt" in key:
                        groups["envt"] = data
                    if "ref" in key:
                        groups["ref"] = data
                    if "line" in key:
                        groups["line"].append(data)
        
        envt_df = groups["envt"]["df"]
        envt_measure = groups["envt"]["measure"]
        envt_id = groups["envt"]["id"]
        envt_instrument = groups["envt"]["instrument"]
        
        ref_df = groups["ref"]["df"]
        ref_measure = groups["ref"]["measure"]
        ref_id = groups["ref"]["id"]
        ref_instrument = groups["ref"]["instrument"]
        # Groups parameters
        envt_min = envt_df[envt_measure].min()
        envt_max = envt_df[envt_measure].max()
        envt_bins = np.linspace(envt_min, envt_max, self.nb_interval)
        envt_centers = (envt_bins[:-1] + envt_bins[1:]) / 2
        envt_corr = []
        
        
        
        for k in range(len(groups["line"])):
            envt_corr_k = []
            line_df = (groups["line"][k])["df"]
            line_measure = (groups["line"][k])["measure"]
            
            for i in range(len(envt_bins)-1):
                mask = ((envt_df[envt_measure] >= envt_bins[i]) &
                        (envt_df[envt_measure] < envt_bins[i+1]))
                
                data_ref = ref_df.loc[mask, ref_measure]
                data_line = line_df.loc[mask, line_measure]
                if len(data_ref) > 1:
                    data_ref_c = data_ref - data_ref.mean()
                    data_line_c = data_line - data_line.mean()
                    corr = data_ref_c.corr(data_line_c)
                else:
                    corr = np.nan
                envt_corr_k.append(corr)
            
            envt_corr.append(envt_corr_k)

        fig, ax = plt.subplots()
        self.figure_corr = fig
        #all_colors = list(mcolors.TABLEAU_COLORS.keys())
        for k in range(len(envt_corr)):
            #color = all_colors[k-1 % len(all_colors)]
            line_measure = (groups["line"][k])["measure"]
            line_id = (groups["line"][k])["id"]
            line_instrument = (groups["line"][k])["instrument"]
            ax.plot(envt_centers, envt_corr[k],label = f"{ref_measure}:{ref_instrument} ID {ref_id} // {line_measure}:{line_instrument} ID {line_id} ", marker='o')
        
        def legend_x_axis(measure):
            if measure.lower() in ["temperature","dew_point","wet_bulb"]:
                return f"{measure.capitalize()} (°C)"
            elif measure.lower() in ["humidity","umidity"]:
                return "Humidity (%)"
            elif measure.lower() == "wind_dir":
                return "Wind direction (°)"
            elif measure.lower() in ["wind_gust","wind_speed"]:
                return f"{measure} (m/s)"
            else:
                return f"{measure} concentration"
        
        ax.set_xlabel("Time")
        ax.set_xlabel(legend_x_axis(envt_measure))
        ax.set_ylabel("Correlation between instrument")
        ax.set_title(f"Influence of {envt_measure} ({envt_instrument} ID:{envt_id}) on the correlation between instruments")
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
        
        
    def plot_autocorr_vs_env(self,frame):
        
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
            if autocorr is None:
                return np.nan
            for i, r in enumerate(autocorr):
                if r <= threshold:
                    return i * dt /60
            return np.nan
        
        def split_continuous_segments(df, time_col="datetime", max_gap_sec=120):
            """
            Découpe un DataFrame en segments continus selon un gap temporel max.
            """
            df = df.sort_values(time_col)
            dt = df[time_col].diff().dt.total_seconds()
        
            segments = []
            start = 0
        
            for i in range(1, len(df)):
                if dt.iloc[i] > max_gap_sec:
                    segments.append(df.iloc[start:i])
                    start = i
        
            segments.append(df.iloc[start:])
            
            return segments
        
        def mean_autocorr_by_bin(df, value_col, time_col, max_lag, max_gap_sec):
            segments = split_continuous_segments(df, time_col, max_gap_sec)
            print(f"SEGMENTS {value_col}")
            print(len(segments))
            print(segments)
            autocorrs = []
            for seg in segments:
                if len(seg) > max_lag + 5:   # sécurité
                    ac = autocorrelation(seg[value_col].values, max_lag)
                    autocorrs.append(ac)
        
            if len(autocorrs) == 0:
                return None
        
            return np.nanmean(autocorrs, axis=0)
        
        """Trace les corrélations en fonction des mesures environnementales."""
        print("PLOT CORRELATION VS ENV")
        groups = {"envt" : None, "ref" : None, "line": []}
        
        # Regrouper les données par groupe
        for key, data in self.dataframes_to_process.items():
            print("KEY:",key)
            print("DATA:",data.keys())
            
            if isinstance(data, dict) and "df" in data:
                df = data["df"]
                if df is not None and not df.empty:
                    
                    if "envt" in key:
                        groups["envt"] = data
                    if "ref" in key:
                        groups["ref"] = data
                    if "line" in key:
                        groups["line"].append(data)
        
        envt_df = groups["envt"]["df"]
        envt_measure = groups["envt"]["measure"]
        envt_id = groups["envt"]["id"]
        envt_instrument = groups["envt"]["instrument"]
        measure_envt_col = [c for c in envt_df.columns if c != "datetime"]
        
        # Groups parameters
        envt_min = envt_df[envt_measure].min()
        envt_max = envt_df[envt_measure].max()
        envt_bins = np.linspace(envt_min, envt_max, self.nb_interval)
        envt_centers = (envt_bins[:-1] + envt_bins[1:]) / 2
        envt_corr = []
        
        ref_df = groups["ref"]["df"]
        ref_measure = groups["ref"]["measure"]
        ref_id = groups["ref"]["id"]
        ref_instrument = groups["ref"]["instrument"]
        print("BLOC REF",[ref_measure,ref_id,ref_instrument])
        measure_ref_col = [c for c in ref_df.columns if c != "datetime"]
        
        tau_envt = []
        tau_ref = []
        tau_line = []
        max_lag =10
        dt_moyen = (df["datetime"].sort_values().diff().dropna().dt.total_seconds().mean())
        max_gap_sec = 3 * dt_moyen
        label = []
        label.append([envt_measure,envt_instrument,envt_id])
        label.append([ref_measure,ref_instrument,ref_id])
        
        for i in range(len(envt_bins)-1):
            mask = ((envt_df[envt_measure] >= envt_bins[i]) &
                    (envt_df[envt_measure] < envt_bins[i+1]))
            
            x_envt = envt_df.loc[mask, ["datetime",envt_measure]]
            x_ref = ref_df.loc[mask, ["datetime",ref_measure]]
            
            autocorr_envt = mean_autocorr_by_bin(x_envt,value_col=envt_measure,time_col="datetime",max_lag=max_lag,max_gap_sec=max_gap_sec)
            tau_envt.append(characteristic_time(autocorr_envt, dt_moyen, threshold=0.75))
            
            autocorr_ref = mean_autocorr_by_bin(x_ref,value_col=ref_measure,time_col="datetime",max_lag=max_lag,max_gap_sec=max_gap_sec)
            tau_ref.append(characteristic_time(autocorr_ref, dt_moyen, threshold=0.75))
            
            
        
        print("len_groups_line",len(groups["line"]))
        print("tau_envt",tau_envt)
        print("tau_ref",tau_ref)
        for k in range(len(groups["line"])):
            line_corr_k = []
            line_df = (groups["line"][k])["df"]
            line_measure = (groups["line"][k])["measure"]
            line_id = (groups["line"][k])["id"]
            line_instrument = (groups["line"][k])["instrument"]
            label.append([line_measure,line_instrument,line_id])
            for i in range(len(envt_bins)-1):
                mask = ((envt_df[envt_measure] >= envt_bins[i]) &
                        (envt_df[envt_measure] < envt_bins[i+1]))
                
                x_line = line_df.loc[mask, ["datetime",line_measure]]
                autocorr_line = mean_autocorr_by_bin(x_line,value_col=line_measure,time_col="datetime",max_lag=max_lag,max_gap_sec=max_gap_sec)
                tau_line_loc = characteristic_time(autocorr_line, dt_moyen, threshold=0.75)
                # autocorr_line = autocorrelation(x_line, max_lag)
                # tau_line_loc = characteristic_time(autocorr_line, dt_moyen, threshold=0.75)
                
                line_corr_k.append(tau_line_loc)
                
            
            tau_line.append(line_corr_k)
        
        print("tau_line",tau_line)
        tau = [tau_envt,tau_ref]+tau_line
        
        print("tau",tau)
        print("label",label)
        fig, ax = plt.subplots()
        self.figure_corr = fig
        #all_colors = list(mcolors.TABLEAU_COLORS.keys())
        for k in range(len(tau)):
            #color = all_colors[k-1 % len(all_colors)]
            
            ax.plot(envt_centers, tau[k],label = f"Autocorrelation {label[k][0]} {label[k][1]} ID {label[k][2]}", marker='o')
        
        def legend_x_axis(measure):
            if measure.lower() in ["temperature","dew_point","wet_bulb"]:
                return f"{measure.capitalize()} (°C)"
            elif measure.lower() in ["humidity","umidity"]:
                return "Humidity (%)"
            elif measure.lower() == "wind_dir":
                return "Wind direction (°)"
            elif measure.lower() in ["wind_gust","wind_speed"]:
                return f"{measure} (m/s)"
            else:
                return f"{measure} concentration"
        
    
        ax.set_xlabel(legend_x_axis(envt_measure))
        ax.set_ylabel("Tau 0.75 (min)")
        ax.set_title(f"Influence of {envt_measure} ({envt_instrument} ID:{envt_id}) on the correlation between instruments")
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
        
    def plot_barcharts(self,frame):
        """Trace les histogrammes de comptage d'échantillons."""
        print("PROCESS:")
        print(self.dataframes_to_process.keys())
        envt_dic = self.dataframes_to_process["envt"]
        
        print("ENVT DIC")
        print(envt_dic.keys())
        envt_df = envt_dic["df"]
        envt_measure = envt_dic["measure"]
        envt_id = envt_dic["id"]
        envt_instrument = envt_dic["instrument"]
        
        envt_min = envt_df[envt_measure].min()
        envt_max = envt_df[envt_measure].max()
        envt_bins = np.linspace(envt_min, envt_max, self.nb_interval)
        envt_centers = (envt_bins[:-1] + envt_bins[1:]) / 2
    
        envt_counts = [
            ((envt_df[envt_measure] >= envt_bins[i]) &
              (envt_df[envt_measure] < envt_bins[i+1])).sum()
            for i in range(len(envt_bins)-1)]

        fig, ax = plt.subplots(figsize=(8, 4))
        self.figure_barchart = fig
        ax.bar(envt_centers, envt_counts, width=envt_bins[1]-envt_bins[0], align="center", alpha=0.7, edgecolor="black")
        ax.set_xlabel(envt_measure)
        ax.set_ylabel("Number of samples")
        ax.set_title(f"Sample counts per {envt_measure} bin ({envt_instrument} ID {envt_id})")
        ax.grid(True, axis="y", linestyle="--", alpha=0.6)
        # canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        # canvas.draw()
        # canvas.get_tk_widget().pack(fill="both", expand=True)
        # plt.close(fig)
        canvas = FigureCanvasTkAgg(fig, master=frame)  # Utiliser le frame passé en argument
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)
        
        
        
        
       
    def plot_normal(self,frame):
        """Trace les graphiques normaux."""

        def legend_axis(measure):
            if measure.lower() in ["temperature","dew_point","wet_bulb"]:
                return f"{measure.capitalize()} (°C)"
            elif measure.lower() in ["humidity","umidity"]:
                return "Humidity (%)"
            elif measure.lower() == "wind_dir":
                return "Wind direction (°)"
            elif measure.lower() in ["wind_gust","wind_speed"]:
                return f"{measure} (m/s)"
            else:
                return f"{measure} concentration"
        
        """Trace les données avec 'envt' à gauche et les autres à droite."""
        fig, ax1 = plt.subplots()
        self.figure_plot = fig
        
        ax2 = ax1.twinx()  # Créer un second axe Y
        all_colors = list(mcolors.TABLEAU_COLORS.keys())
        non_red_colors = [color for color in all_colors if "red" not in color]
        # Parcourir les données
        for i,(key, data) in enumerate(self.dataframes_to_process.items()):
            if isinstance(data, dict) and "df" in data:
                df = data["df"]
                if df is not None and not df.empty:
                    for col in df.columns:
                        if col != "datetime":
                            instrument = data.get("instrument", "Unknown")
                            id_val = data.get("id", "Unknown")
                            measure = col
        
                            # Tracer 'envt' sur ax1 (à gauche)
                            if key == "envt":
                                ax1.plot(df["datetime"], df[col],
                                        label=f"{measure} : {instrument} ID {id_val}",color="red",linestyle=":")
                                ax1.set_ylabel(legend_axis(measure))# color="blue")
                                ax1.tick_params(axis="y")#, labelcolor="blue")
        
                            # Tracer les autres sur ax2 (à droite)
                            else:
                                if key == "ref":
                                    linewidth = 1.3
                                    linestyle = "--"
                                else:
                                    linewidth = 0.8
                                    linestyle ="-"
                                color = non_red_colors[i-1 % len(non_red_colors)]
                                ax2.plot(df["datetime"], df[col],
                                        label=f"{measure} : {instrument} ID {id_val}" ,linewidth=linewidth, linestyle = linestyle, color=color)
                                ax2.set_ylabel(legend_axis(measure))# ,color="red")
                                ax2.tick_params(axis="y")#, labelcolor="red")
        
        # Ajustement des abscisses
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
        
        # Légendes
        ax1.legend(loc="upper left")
        ax2.legend(loc="upper right")
        
        plt.tight_layout()
        # Afficher le plot dans Tkinter
        # canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        # canvas.draw()
        # canvas.get_tk_widget().pack(fill="both", expand=True)   
        
        canvas = FigureCanvasTkAgg(fig, master=frame)  # Utiliser le frame passé en argument
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)         
        


    def display_stats(self,frame):
        """Affiche les statistiques pour chaque combinaison (référence, ligne)."""
        print("START DISPLAY STATS")
    
        # Liste pour stocker tous les DataFrames de statistiques
        all_stats_dfs = []
        
        
        
        envt_dic = self.dataframes_to_process["envt"]
        envt_df = envt_dic["df"]
        envt_instrument = envt_dic.get("instrument", "unknown")
        envt_id = envt_dic.get("id", "unknown")
        envt_measure = envt_dic.get("measure", "unknown")
    
        # Renommer la colonne de mesure de référence
        envt_col_name = f"envt_{envt_id}_{envt_measure}"
        envt_df_renamed = envt_df.rename(columns={envt_measure: envt_col_name})
        
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
                
                print("KEY:", key)
                if key == "ref":
                    df_keyref = envt_df.copy()
                    keyref_col_name = f"ref_{envt_id}_{envt_measure}"
                    df_keyref_renamed = df_keyref.rename(columns={envt_measure: keyref_col_name})
                    df_keyother = ref_df.copy()
                    keyother_col_name = f"other_{ref_id}_{ref_measure}"
                    df_keyother_renamed = df_keyother.rename(columns={ref_measure: keyother_col_name})
                    
                    merged_df = pd.merge(df_keyref_renamed, df_keyother_renamed, on="datetime", how="inner")
                else:
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
                    
                    if key == "ref":
                        ref_instrument_abbr = instrument_map.get(envt_instrument, envt_instrument)
                        other_instrument_abbr = instrument_map.get(ref_instrument, ref_instrument)
                        stats_df["reference"] = f"{ref_instrument_abbr}_{envt_id}_{envt_measure}"
                        stats_df["instrument"] = f"{other_instrument_abbr}_{ref_id}_{ref_measure}"
                    else:
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
                    "MBE": mbe,
                    "MAE": mae,
                    "RMSE": rmse,
                    "r": r,
                    "r2":r2,
                    "R2": R2,
                    "MeanRatio": mean_ratio
                })
    
        return pd.DataFrame(results) if results else pd.DataFrame(columns=["reference", "instrument", "MBE", "MAE", "RMSE", "r", "r2", "R2", "MeanRatio"])

    def _display_stats(self, frame, stats_df):
        """Affiche les statistiques dans le Treeview."""
        # Effacer les anciennes données
        for widget in frame.winfo_children():
            widget.destroy()

        if stats_df is not None and not stats_df.empty:
            # Créer le Treeview avec une hauteur limitée
            self.stats_tree = Treeview(frame, columns=("reference", "instrument", "MBE", "MAE", "RMSE", "r", "r2", "R2", "MeanRatio"), show="headings", height=5)
            
            # Configurer les en-têtes
            self.stats_tree.heading("reference", text="Reference")
            self.stats_tree.heading("instrument", text="Instrument")
            self.stats_tree.heading("MBE", text="MBE")
            self.stats_tree.heading("MAE", text="MAE")
            self.stats_tree.heading("RMSE", text="RMSE")
            self.stats_tree.heading("r", text="r")
            self.stats_tree.heading("r2", text="r²")
            self.stats_tree.heading("R2", text="R² ")
            self.stats_tree.heading("MeanRatio", text="Mean Ratio")

            # Configurer les colonnes
            self.stats_tree.column("reference", width=100)
            self.stats_tree.column("instrument", width=100)
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
        
    
    def save_plot_corr(self, directory, frame):
        """Sauvegarde la figure actuelle."""
        print("save plot normal")
        if hasattr(self, 'figure_corr'):
            if directory:
                # Demander le nom du fichier via une boîte de dialogue simple
                filename = simpledialog.askstring("Filename", "Enter the file name for the barchart plot (.png):", parent=frame, initialvalue="figure_corr")
                if filename:
                    filename = os.path.join(directory, filename + ".png")
                    self.figure_corr.savefig(filename, dpi=300, bbox_inches='tight')
                    print(f"Figure sauvegardée sous : {filename}")
                
        else:
            print("Aucune figure à sauvegarder.")
        