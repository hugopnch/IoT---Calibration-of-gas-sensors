# IoT - Calibration of gas sensors - UNICT 
This project aims at providing high precision measurement of gas inside open farms to all by calibrating a high precision instrument on lower precisions instruments. To do so it has been done: 
* Data work: - Formatting of old data
             - Recuperation on site of new data (or scraping on websites) and cleaning
             - Temporal alignement of the data
* Data analysis: - Construction of a graphical interface to automate the analysis
* Calibration: - Use of several machine learning methods in order to match the low precisions instruments to the high one
               - Construction of features on the historic of each IoT to improve the calibration results
               - Automation of the analysis of the calibration via a quarto file
* Results: - All the results are found in the file machine_learning_results (quarto files)
           - A draft sum-up of the work can be found at machine_learning_results/draft_results.pdf

* On going: APP creation (via Streamlit) to globalize this calibration process to all. 
