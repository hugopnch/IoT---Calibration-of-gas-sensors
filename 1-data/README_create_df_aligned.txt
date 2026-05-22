*******************************************************************
HOW TO : create a dataframe with aligned data and where only the day where rabbit/innova are working
********************************************************************************************
1 - To update the .csv of each instrument on the common dates of rabbit/innova
*****************************************************************
To do so, if you have updated the data_instrument file (current_df_instrument.csv as explained in README_integrate_new_data). You just need to open the function data/formatting_on_common_dates.py. Execute it with the command : "main_dataframe(True)". The new dataframes of the instruments should be created in "data_common_dates/current_df_instrument_CD.csv". The previous file are moved to "data_common_dates/backup_files/timestamp".

You have now your dataframes by common dates of rabbit/innova. Time to synchronise all of it!

********************************************************************************************
3 - To synchronise all the data 
*****************************************************************
Use the function "time_alignement.py" by writing main(debug) where debug = True or False! You should now have you're dataframe aligned "current_df_aligned_ALL.csv" in your folder!