import subprocess
import os
from scripts.raw_data_extract import download_all_data
from scripts.transform_gistemp_adjusted import transform_giss_data
from scripts.transform_crutem_adjusted import transform_crutem_data
from scripts.transform_ghcn_raw import transform_ghcn_data

def main():
    # Step 1: Download Data
    print("Downloading data...")
    download_all_data()
    
    # Step 2: Clean and Transform Data
    print("Cleaning and transforming GISS data...")
    transform_giss_data()
    
    print("Cleaning and transforming Crutem data...")
    transform_crutem_data()
    
    print("Cleaning and transforming GHCN raw data...")
    transform_ghcn_data()
    
    # TODO: Step 3: Start the Flask server
    #print("Starting Flask server...")
    
    #from server import app
    #app.run(debug=True)

if __name__ == "__main__":
    main()
