import pandas as pd
import numpy as np
import glob
import os

def transform_ghcn_data():
    # Adjust file paths for raw data and landmask
    data_file_path = os.path.join('data', 'raw')
    name = glob.glob(data_file_path + "/ghcnm*")

    GHCNDat = glob.glob(name[0] + "/*.dat")
    GHCNmeta = glob.glob(name[0] + "/*.inv")
    landmask = os.path.join('data', 'raw', 'landmask.dta')

    # load the GHCNV4 monthly with column names
    colspecs = [(0, 2), (0, 11), (11, 15), (15, 19)]
    names = ['country_code', 'station', 'year', 'variable']
    i = 19
    for m in range(1, 13):
        mon = str(m)
        colspecs_tmp = (i, i + 5)
        names_tmp = 'VALUE' + mon

        colspecs.append(colspecs_tmp)
        names.append(names_tmp)

        i = i + 8

    ghcnv4 = pd.read_fwf(GHCNDat[0],
                        colspecs=colspecs, names=names)

    # load landmask
    lndmsk = pd.read_stata(landmask)


    # Load station metadata
    stnMeta = pd.read_fwf(GHCNmeta[0], colspecs=[(0, 2), (0, 12), (12, 21), (21, 31),
                                            (31, 38), (38, 69)],
                        names=['country_code', 'station',
                                'lat', 'lon', 'elev', 'name'])
    
    # create grids
    grid_size = 5
    count = -90 + (grid_size / 2)
    stnMeta['latgrid'] = 0.0

    for x in range(-90, 90, 5):
        stnMeta.loc[stnMeta['lat'].between(x, x+5), 'latgrid'] = count
        count = count + grid_size

    count = -180 + (grid_size / 2)
    stnMeta['longrid'] = 0.0

    for x in range(-180, 180, 5):
        stnMeta.loc[stnMeta['lon'].between(x, x+5), 'longrid'] = count
        count = count + grid_size

    stnMeta['gridbox'] = stnMeta['latgrid'].map(str) + " lat " + stnMeta['longrid'].map(str) + " lon"
    stnMetaGrid = stnMeta.merge(lndmsk, on='gridbox')
    stnMetaGrid['grid_weight'] = np.sin((stnMetaGrid['latgrid'] + grid_size / 2) * np.pi / 180) - np.sin(
        (stnMetaGrid['latgrid'] - grid_size / 2) * np.pi / 180)
    stnMetaGrid['grid_weight'] = stnMetaGrid['grid_weight'] * stnMetaGrid['land_percent']

    # clean ghcn and create anomalies
    ghcnv4NoNullYears =  ghcnv4.replace(-9999, np.nan)

    for m in range(1, 13):
        ghcnv4NoNullYears['VALUE' + str(m)] = ghcnv4NoNullYears['VALUE' + str(m)] / 100
    ghcnv4NoNullYears = ghcnv4NoNullYears[ghcnv4NoNullYears.year.notnull()]

    ghcnlong = ghcnv4NoNullYears.set_index('station')
    ghcnlong = ghcnlong.reset_index()
    ghcnlong = pd.melt(ghcnlong, id_vars=['station', 'year'],
                    value_vars=['VALUE1', 'VALUE2', 'VALUE3', 'VALUE4', 'VALUE5', 'VALUE6',
                                'VALUE7', 'VALUE8', 'VALUE9', 'VALUE10', 'VALUE11', 'VALUE12'])

    ghcnBaselines = ghcnlong[ghcnlong['year'].between(1961, 1990)]
    ghcnBaselines = ghcnBaselines.drop(columns='year')
    ghcnBaselines = ghcnBaselines.groupby(['station', 'variable']).mean()
    ghcnBaselines = ghcnBaselines.rename(columns={"value": "baseline"})

    ghcnAnoms = ghcnlong.merge(ghcnBaselines, on=['station', 'variable'])
    ghcnAnoms['anomalies'] = ghcnAnoms['value'] - ghcnAnoms['baseline']

    # merge on the metadata
    ghcnAnomsGrid = ghcnAnoms.merge(stnMetaGrid, on=['station'])
    ghcnAnomsGrid = ghcnAnomsGrid[ghcnAnomsGrid.anomalies.notnull()]
    ghcnAnomsGrid = ghcnAnomsGrid.drop(columns=['baseline', 'station', 'name', 'lat', 'lon', 'elev', 'latgrid', 'longrid', 'land_percent',
                                                'ocean_percent', 'value', 'country_code'])

    # take the mean of the anomalies grouped by gridbox, variable, and year
    ghcnAnomsGrid = ghcnAnomsGrid.groupby(['gridbox', 'variable', 'year']).mean().reset_index()

    # take weighted average of anomalies using the grid_weight column as weights
    ghcnAnomsWtd = ghcnAnomsGrid.groupby(['year']).apply(lambda x: np.average(x['anomalies'], weights=x['grid_weight'])).reset_index()

    # rename the columns
    ghcnAnomsWtd.columns = ['year', 'anomaly (deg C)']

    # filter to only years between 1900 and current year - 1 (current year isn't over yet)
    latest_year = pd.Timestamp.now().year-1
    ghcnAnomsWtd = ghcnAnomsWtd[ghcnAnomsWtd['year'].between(1900, latest_year)]

    output_file_path = os.path.join('data', 'clean', 'ghcnm_anomalies_clean.csv')
    ghcnAnomsWtd.to_csv(output_file_path, index=False)

if __name__ == '__main__':
    transform_ghcn_data()