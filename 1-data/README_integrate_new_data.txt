********************************************************************************************
HOW TO : update the .csv of the different instruments with new data
********************************************************************************************

⦁	Create a file "data/YYYYMMDD_YYYYMMDD_to_add". Create a file "data/YYYYMMDD_YYYYMMDD_to_add/INSTRUMENT_to_add" per instrument you want to update with INSTRUMENT = [innova,rabbit,meteo_station,envea]

⦁	Add the new data Inside:
1.	In the file "innova_to_add": copy/paste a PDF version of the measurement from Lumasoft software of all the SL (the export is usually in xps you need to convert it before, you can use the following link: https://xpstopdf.com/fr/). For the moment the code is not made to handle excel file (as no file like that were found)
2.	In the file "rabbit_to_add": if the data is extracted from the application: copy/paste a CSV version of the measurement (not xlsx/xls) of each SL. If the data is exported from the website: copy/paste a CSV version of all the measurement you have taken (temperature/humidity/co2/nh3/…) (the documents should not be regrouped in one file). If you exported the data as xlsx/xls please convert it to CSV before or it will not work properly.
3.	In the file "meteo_station_to_add". To extract new data : go to to the next steps.   
4.	In the file "envea": not programmed yet

⦁	Inside the files copy/paste the appropriate python file(s) "csv_functions/merge_csv_INSTRUMENT.py"
⦁	You can now open the Python code:

1.	For innova you need to change the "date" parameter as well as the "SL_list" parameter. 
* If you have the pdf version of the data. Launch the function read_pdf_camelot (be sure to have the correct name format the the files ({date}_SL{X}.pdf). The function will extract the data from pdf and create a csv. The function can take several minutes per file. You should now have the files "Channel_{SL}_Measurement_Data.csv" (one per SL). on the folder.
* If you have the csv version of the data. Launch the function formatting_csv(SL_list). This function will create you formatted files (so you can check that each one is ok) (Channel_{SL}_Measurement_Data_formatted.csv) as well as the merged file "merged_innova.csv".
* If you have the pdf version you can also launch only "main_merge_csv_innova_2" that will do the two steps
* NB: the mean of innova is done on 2 out of 3 points on the current python file. If you want to change to take the 3 measurement you need to change the lines:
	 fused_numeric = block[numeric_cols].iloc[1:].mean() --> fused_numeric = block[numeric_cols].iloc[0:].mean()
	 dt_mean = (block["datetime"].iloc[1:]).astype("int64").mean() --> dt_mean = (block["datetime"].iloc[0:]).astype("int64").mean() 


2.	For rabbit the you launch the formatting of the new dataframe with "main_csv_rabbit(type_extract, debug)" ou type extract = "computer" or "app", debug = True or False. You don't have to change any parameters as the code is looking for all ".csv" present inside the file. Be sure that no parasite file is here. You should have as output a file "merged_rabbit.csv". You can control it to see if the results are coherent. To be noted that some other Excel file might be created (XXXX_fixed.csv) as they were some problems with exports from website (missing some ",).

3.	For meteo_station: 
Connect you to the website "https://live.netsens.it/login.php". Click on "Misure", "Intervello temporale","Personalizza". Choose "Inizio" "Fine. Be sure to have at least one week of interval (even if it's too much you can suppress it after but the format of the site change if there is not enough date and the program is not programmed to do it.). Then let the program work "extract_from_web". You should have one csv per day.
Use the function "meteostation_formatting" by writting main(folder_raw,folder_output). 
Then you can use  "merge_all_day_meteo" to have only one dataframe with all the csv formated: be sure to change the name of the folder in order with where you've put the data formatted (line 53). "merge_csv_folder("original_file/data_formated_tkinter", "merged_meteo_station.csv"). You should now have the new dataframe "merged_meteo_station" (composed only of new data).

4.	For envea : not programmed yet

⦁	Finally you can open the code "data/merge_data_new". Change the parameter "TO_ADD_DIR" to the date file you created. Execute the code with main().

⦁	Outputs/File modifications:
1.	The file "data/YYYYMMDD_YYYYMMDD_to_add" has been moved to "data/extension_files/".
2.	For each instruments you wanted to update, the following file were created/modificated at the location "data_INSTRUMENT/:
 	* The file current_df_instrument.csv : updated CSV with all the merged data
 	* The file df_instrument_backup_backuptimestamp.csv was created in the backup file with the old dataframe


You should be back with the same files as explained in "Organization of the file". To be noted: this data are the one used in the graphic interface. These data are not filtered by common dates and are just "raw" data formated. To filter by common dates (of rabbit and innova) : check README_create_df_aligned