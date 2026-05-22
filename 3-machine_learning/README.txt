4 notebooks py can be found in this file

1-specific_analyses.py: is used to do some data analysis specific (fourrier transform, bin error analysis, visalisation of potentiel working regimes with a simple decision tree…)

2-signal_decomposition.py: is used to do a decomposition of the historic of the IoT instrument in order to calibrate it better. The exported file (.csv) can be find in the file csv_decomposed/(innova or envea)/df_signal_decomposition_... .csv

3-workflow_main.py : it is the most important file and is used to do the main analysis. It is required to change the build_config() function as well as the pannel command to control the worflow. The main workflow is then launched with the file quarto_report.qmd in a terminal where quarto has been installed launch 'quarto render quarto_report.qmd' and a full pdf analysis of the model ill be produced. 
To be noted: you can find examples of the reports in ../4-machine_learning_results/..

4-plot_data_corrected.py: it's a postprocessing that allows to control which model you want to load and plot in order to compare well the results