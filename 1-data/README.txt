This file was created to do two things:
* TASK 1 // Integrate easily the new data acquired to the old data of each instrument.(cf README_integrate_new_data): these dataframes will be used on the tkinter interface.
* TASK 2 // Create a dataframe with all the csv of all the instruments merged and aligned (cf README_create_df_aligned)


Find Following an explanation on how the file is organized. To do one of the previous task please refer to the appropriate readme.

********************************************************************************************
ORGANIZATION OF THE FILE
********************************************************************************************

⦁	csv_functions (folder)
⦁	data_innova (folder)
⦁	data_rabbit (folder)
⦁	data_envea (folder)
⦁	data_meteo_station (folder)
	data_common_dates (folder)
⦁	extensions_files (folder)
⦁	merge_data_new (.py): python function to merge new data of each instrument to the old data of each instrument (task 1)
⦁	formatting_on_common_dates (.py): python function to modify the the .csv of each instrument in order to keep only the date range 	where we can compare innova and rabbit (task 2)
⦁	time_alignement (.py): python function to align all datas from datas_common_dates on one timescale + merge of all .csv (task 2)
⦁	README (.txt): currently reading it
	README_integrate_new_data (.txt)
	README_create_df_aligned (.txt)


The files data_X are composed of :
⦁	backup_files (folder)
⦁	original_file (folder)
⦁	current_df_X (.csv)



********************************************************************************************
GLOBAL LOGIC:
********************************************************************************************

The original data files were inside the Following files :"data_X/original_file/"

As those documents were not "clean" for most of them, python functions "data_formatting_X.py" were created in order to have a regular/clean csv called "X_formated.csv". There is no more need to touch the "original_file" as the work has already been done and the "original/old" dataframe is now built. It served only as backup/history.


Inside the file csv_functions you can find diverses functions (x4) that will extract the new data of the instruments as a formated/clean csv.

The idea will be to use the latest formated dataframe as well as the new csv from the instrument to form the newest csv easily (current_df_X) for each instrument.

Inside the file extensions_file you can find all the différents addings that were made to the original ones.





