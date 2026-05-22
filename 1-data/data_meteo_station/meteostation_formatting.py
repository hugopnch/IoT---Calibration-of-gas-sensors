import pandas as pd
import glob
import os

def cluster_one_group(sub, threshold_seconds=5, rep_method="mean"):
    """Cluster les timestamps proches dans un sous-DataFrame."""
    unique_times = pd.Series(pd.to_datetime(sub["datetime"].unique())).sort_values().reset_index(drop=True)
    clusters = []
    current = [unique_times.iloc[0]]
    for t in unique_times.iloc[1:]:
        if (t - current[-1]).total_seconds() <= threshold_seconds:
            current.append(t)
        else:
            clusters.append(current)
            current = [t]
    clusters.append(current)

    dt_map = {}
    for cluster in clusters:
        if rep_method == "min":
            rep_t = min(cluster)
        elif rep_method == "mean":
            mean_ns = int(sum([c.value for c in cluster]) / len(cluster))
            rep_t = pd.to_datetime(mean_ns).round("s")
        else:
            rep_t = pd.to_datetime(min(cluster))
        for c in cluster:
            dt_map[pd.Timestamp(c)] = rep_t

    sub = sub.copy()
    sub["datetime"] = sub["datetime"].map(lambda x: dt_map.get(pd.Timestamp(x)))
    return sub

def cluster_by_location(df, threshold_seconds=5, rep_method="mean"):
    """Sépare in/out et applique le clustering à chaque groupe."""
    dfs = []
    for loc in df["location"].unique():
        sub = df[df["location"] == loc].copy()
        sub_clustered = cluster_one_group(sub, threshold_seconds, rep_method)
        dfs.append(sub_clustered)
    return pd.concat(dfs, ignore_index=True)

def cluster_datetimes_and_pivot(input_path, output_path,
                                threshold_seconds=5,
                                rep_method="mean",
                                pivot_agg="first"):

    df = pd.read_csv(input_path, sep=",")
    df["datetime"] = pd.to_datetime(df["Data"], format="%Y-%m-%d %H:%M:%S")

    # Identifier in/out
    df["location"] = df["Postazione"].astype(str).apply(
        lambda x: "out" if "_1" in x else ("in" if "_2" in x else "unknown")
    )

    # --- Clustering séparé ---
    df = cluster_by_location(df, threshold_seconds=threshold_seconds, rep_method=rep_method)

    # Colonnes date/hour
    df["date"] = df["datetime"].dt.strftime("%Y-%m-%d")
    df["hour"] = df["datetime"].dt.strftime("%H:%M:%S")

    # Nettoyage mesures
    df["measure_raw"] = df["Sensore"].astype(str).str.extract(r"^([^\(]+)")[0].str.strip()
    rename_map = {
        "Umidità aria": "humidity",
        "Temperatura aria": "temperature",
        "Punto di rugiada": "dew_point",
        "Bulbo umido": "wet_bulb",
        "Raffica vento": "wind_gust",
        "Velocità del vento": "wind_speed",
        "Direzione vento": "wind_dir",
        "Corrente": "current",
        "Pannello fotovoltaico": "pv_voltage",
    }
    df["measure"] = df["measure_raw"].replace(rename_map).fillna(df["measure_raw"])
    df["measure"] = df["measure"] + "_" + df["location"]

    df["value"] = pd.to_numeric(df["Misura"], errors="coerce")

    # Pivot
    df_wide = df.pivot_table(
        index=["datetime", "date", "hour"],
        columns="measure",
        values="value",
        aggfunc=pivot_agg
    ).reset_index()

    df_wide.to_csv(output_path, index=False)
    return df_wide

def main(folder_raw,folder_output):
    # Cherche tous les CSV dans le dossier
    csv_files = glob.glob(os.path.join(folder_raw, "*.csv"))
    # Création d'un dossier "mon_dossier"
    os.makedirs(folder_output, exist_ok=True)
    if not csv_files:
        print("[!] Aucun fichier CSV trouvé.")
        return None
    
    print(f"[*] {len(csv_files)} fichiers trouvés dans {folder_raw}.")

 
    for file in csv_files:
       
        try:
            cluster_datetimes_and_pivot(file, file.replace(folder_raw,folder_output), threshold_seconds=5, rep_method="mean", pivot_agg="first")
            
        except Exception as e:
            print(f"[!] Erreur avec {file}: {e}")
    
    return

# df_out = cluster_datetimes_and_pivot("data_meteo_station/data_raw/2025-01-02.csv", "output_2.csv", threshold_seconds=5, rep_method="mean", pivot_agg="first")
# print(df_out.head())