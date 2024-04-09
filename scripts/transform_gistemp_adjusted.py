import os
import pandas as pd

def transform_giss_data():
    # Assuming this script is in the `scripts` directory, adjust paths accordingly
    data_file_path = os.path.join('data', 'raw', 'giss_temp_data.csv')

    giss = pd.read_csv(data_file_path, skiprows=2, header=None)
    giss.columns = ['Year+Month', 'Station','Land+Ocean','Land_Only','Open_Ocean']

    # Extract the year and month from the column 'Year+month'
    giss['year'] = giss['Year+Month'].astype(str).str[:4].astype(int)

    # Calculate the average of the 'Land_Only' column, grouping by year
    giss = giss.groupby('year').mean()

    # Drop all columns except year and Land_Only, rename Land_Only to 'anomaly (deg C)'
    giss = giss.drop(columns=['Land+Ocean','Open_Ocean', 'Year+Month', 'Station'])
    giss = giss.rename(columns={'Land_Only': 'anomaly (deg C)'})

    latest_year = pd.Timestamp.now().year-1
    # Retain only the data from 1900 to the latest year
    giss = giss.loc[1900:latest_year]

    output_file_path = os.path.join('data', 'clean', 'giss_anomalies_clean.csv')
    # Save the data to a new csv file
    giss.to_csv(output_file_path, index=False)

# If you want to keep the script runnable as a standalone for testing
if __name__ == '__main__':
    transform_giss_data()
