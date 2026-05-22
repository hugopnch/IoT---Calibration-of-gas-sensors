import os
import shutil
import pandas as pd
import datetime

# === CONFIG ===
BASE_DIR = os.getcwd()
TO_ADD_DIR = os.path.join(BASE_DIR, "31032025_11052025")  # FILE TO ADD (to change but keep the structure date_to_add)
BACKUP_DIR = os.path.join(BASE_DIR, "extensions_files")          # <- archive

def merge_csv(base_file, to_add_file):
    # On garde une copie de sécurité avant d’écraser
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = base_file.replace("current_", "backup_files/").replace(".csv", f"_backup_{timestamp}.csv")
    print("backupfile:",backup_file)
    print("basefile:",base_file)
    shutil.copy(base_file, backup_file)

    # Lecture des CSV
    df_base = pd.read_csv(base_file, sep=";", encoding="utf-8")
    df_new = pd.read_csv(to_add_file, sep=";", encoding="utf-8")

    # Fusion
    df_final = pd.concat([df_base, df_new], ignore_index=True).drop_duplicates()
    if "id_channel" in df_final.columns:
        key_cols = ["id_channel", "datetime"] 
        base_index = df_base.set_index(key_cols).index
        df_new_filtered = df_new[~df_new.set_index(key_cols).index.isin(base_index)]
        df_final = pd.concat([df_base, df_new_filtered], ignore_index=True)
        df_final = df_final.sort_values(by=["date","id_channel","hour"], ascending=[True,True,True])
    
    if "id_rabbit" in df_final.columns:
        key_cols = ["id_rabbit", "datetime"] 
        base_index = df_base.set_index(key_cols).index
        df_new_filtered = df_new[~df_new.set_index(key_cols).index.isin(base_index)]
        df_final = pd.concat([df_base, df_new_filtered], ignore_index=True)
        df_final = df_final.sort_values(by=["date","id_rabbit","hour"], ascending=[True,True,True])
       
    if "temperature_in" in df_final.columns:
        key_cols = ["datetime"] 
        base_index = df_base.set_index(key_cols).index
        df_new_filtered = df_new[~df_new.set_index(key_cols).index.isin(base_index)]
        df_final = pd.concat([df_base, df_new_filtered], ignore_index=True)
        df_final = df_final.sort_values(by=["date","hour"], ascending=[True,True])
        
    # Sauvegarde du fichier mis à jour
    df_final.to_csv(base_file, sep=";", index=False, encoding="utf-8-sig")
    print(f"✅ Merge effectué : {base_file} (backup: {backup_file})")
    return df_base,df_new



def main():
    merge_list = []
    # Rabbit
    print("START OF THE UPDATE OF THE DATAFRAMES")
    print("***************")
    
    # Rabbit
    extension_rabbit = os.path.join(TO_ADD_DIR, "rabbit_to_add", "merged_rabbit.csv")
    if os.path.exists(extension_rabbit):
        print("New RABBIT file detected")
        df_r_base,df_r_new = merge_csv("data_rabbit/current_df_rabbit.csv",extension_rabbit)
        merge_list.append("RABBIT")
        print("Update of RABBIT dataframe : DONE")
        print("***************")
    else:
        print("No new RABBIT file detected")
        print("***************")
    
    # Innova
    extension_innova = os.path.join(TO_ADD_DIR, "innova_to_add", "merged_innova.csv")
    if os.path.exists(extension_innova):
        print("New INNOVA file detected")
        df_i_base,df_i_new = merge_csv("data_innova/current_df_innova.csv",extension_innova)
        merge_list.append("INNOVA")
        print("Update of INNOVA dataframe : DONE")
        print("***************")
    else:
        print("No new INNOVA file detected")
        print("***************")
    
    # Meteo station
    extension_meteo = os.path.join(TO_ADD_DIR, "meteo_station_to_add", "merged_meteo_station.csv")
    if os.path.exists(extension_meteo):
        print("New METEO STATION file detected")
        merge_csv("data_meteo_station/current_df_meteostation.csv",extension_meteo)
        merge_list.append("METEO STATION")
        print("Update of METEO STATION dataframe : DONE")
        print("***************")
    else:
        print("No new METEO STATION file detected")
        print("***************")
    
    

    print(f"🚀 The following dataframe update were done : {merge_list} ")

    # Nom du dossier sans le suffixe "_to_add"
    clean_name = os.path.basename(TO_ADD_DIR).replace("_to_add", "")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # Nouveau chemin final
    final_path = os.path.join(BACKUP_DIR, f"{clean_name}_{timestamp}")
    # Déplacement avec renommage
    shutil.move(TO_ADD_DIR, final_path)
    print(f"📦 Dossier archivé dans {final_path}")
    
    return 
# if __name__ == "__main__":
#     main()