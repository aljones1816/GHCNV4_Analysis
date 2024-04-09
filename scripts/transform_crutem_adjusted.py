import pandas as pd
import os

def transform_crutem_data():
    # Adjust the file path for the raw data according to the new structure
    data_file_path = os.path.join('data', 'raw', 'crutem_temp_data.txt')
    crutem = pd.read_csv(data_file_path, skiprows=1, header=None)

    # Separate columns by whitespace
    crutem = crutem[0].str.split(expand=True)

    # Label the columns
    crutem.columns = ['year', "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "anomaly (deg C)"]

    # Starting with the second row, remove every other row
    crutem = crutem.iloc[1::2]

    # Keep only the columns 'year' and 'anomaly (deg C)'
    crutem = crutem[['year', 'anomaly (deg C)']]

    # Convert the columns 'year' and 'anomaly (deg C)' to numeric
    crutem['year'] = pd.to_numeric(crutem['year'])
    crutem['anomaly (deg C)'] = pd.to_numeric(crutem['anomaly (deg C)'])

    latest_year = pd.Timestamp.now().year-1
    # Retain only the data from 1900 to the latest year
    crutem = crutem.loc[crutem['year'].between(1900, latest_year)]

    # Export the data to a new csv file in the clean directory, ignore index column
    output_file_path = os.path.join('data', 'clean', 'crutem_anomalies_clean.csv')
    crutem.to_csv(output_file_path, index=False)

if __name__ == '__main__':
    transform_crutem_data()
