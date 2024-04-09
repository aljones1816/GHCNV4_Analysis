import urllib.request
import tarfile
import glob
import gdown
import shutil
import os

def clean_previous_data():
    # Recursively delete files and folders in ./data folder
    shutil.rmtree('data/raw', ignore_errors=True)
    shutil.rmtree('data/clean', ignore_errors=True)
    # Recreate the data folders
    os.makedirs('data/raw', exist_ok=True)
    os.makedirs('data/clean', exist_ok=True)

def download_ghcn_data():
    try:
        ghcn_url = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcu.tar.gz'
        with urllib.request.urlopen(ghcn_url) as ftpstream:
            thetarfile = tarfile.open(fileobj=ftpstream, mode="r|gz")
            thetarfile.extractall(path='data/raw/')
        print("Downloaded GHCN data successfully.")
    except Exception as e:
        print(f"Failed to download GHCN data: {e}")

def download_landmask(landmask_output='./data/raw/landmask.dta'):
    try:
        if not glob.glob(landmask_output):
            landmask_url = 'https://drive.google.com/uc?id=1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj'
            gdown.download(landmask_url, landmask_output, quiet=False)  
    except Exception as e:
        print(f"Failed to download landmask data: {e}")        

def download_giss_data():
    try:    
        giss_url = 'https://data.giss.nasa.gov/gistemp/graphs_v4/graph_data/Monthly_Mean_Global_Surface_Temperature/graph.csv'
        # Adjust the path according to the raw data directory
        urllib.request.urlretrieve(giss_url, 'data/raw/giss_temp_data.csv')
    except Exception as e:
        print(f"Failed to download GISS data: {e}")

def download_crutem_data():
    try:
        crutem_url = 'https://crudata.uea.ac.uk/cru/data/temperature/CRUTEM5.0_gl.txt'
        # Adjust the path according to the raw data directory
        urllib.request.urlretrieve(crutem_url, 'data/raw/crutem_temp_data.txt')
    except Exception as e:
        print(f"Failed to download CRUTEM data: {e}")

def download_all_data():
    clean_previous_data()
    download_ghcn_data()
    download_landmask()
    download_giss_data()
    download_crutem_data()

if __name__ == '__main__':
    download_all_data()
