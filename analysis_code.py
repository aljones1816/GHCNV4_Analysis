import pandas as pd
import numpy as nm
import math

GHCNDat = "C:/Users/ALAJON/Desktop/Climate Science/GHCNV4 Data/ghcnm.tavg.v4.0.1.20210416.qcu.dat"
GHCNmeta = "C:/Users/ALAJON/Desktop/Climate Science/GHCNV4 Data/ghcnm.tavg.v4.0.1.20210416.qcu.inv"
landmask = "C:/Users/ALAJON/Desktop/Climate Science/GHCNV4 Data/landmask.dta"
colspecs = [(0, 2), (0, 11), (11, 15), (15, 19)]
names = ['country_code', 'station', 'year', 'variable']

# load the GHCNV4 monthly with column names
i = 19
for m in range(1, 13):

    mon = str(m)
    colspecs_tmp = [(i, i + 5), (i + 5, i + 6), (i + 6, i + 7), (i + 7, i + 8)]
    names_tmp = ['VALUE' + mon, 'DMFLAG' + mon, 'QCFLAG' + mon, 'DSFLAG' + mon]

    for j in range(0, 4):
        colspecs.append(colspecs_tmp[j])
        names.append(names_tmp[j])

    i = i + 8

ghcnv4 = pd.read_fwf(GHCNDat,
                     colspecs=colspecs, names=names)

# load landmask
lndmsk = pd.read_stata(landmask)

# Load station metadata
stnMeta = pd.read_fwf(GHCNmeta, colspecs=[(0, 2), (0, 12), (12, 21), (21, 31),
                                          (31, 38), (38, 69)],
                      names=['country_code', 'station',
                             'lat', 'lon', 'elev', 'name'])

grid_size = 5
count = -90 + (grid_size / 2)
stnMeta['latgrid'] = 0

for x in range(-90, 90, 5):
    stnMeta['latgrid'][stnMeta['lat'].between(x, x + 5)] = count
    count = count + grid_size

count = -180 + (grid_size / 2)
stnMeta['longrid'] = 0

for x in range(-180, 180, 5):
    stnMeta['longrid'][stnMeta['lon'].between(x, x + 5)] = count
    count = count + grid_size

stnMeta['gridbox'] = stnMeta['latgrid'].map(str) + " lat " + stnMeta['longrid'].map(str) + " lon"

stnMetaGrid = stnMeta.merge(lndmsk, on='gridbox')

stnMetaGrid['grid_weight'] = nm.sin((stnMetaGrid['latgrid']+grid_size/2)*nm.pi/180) - nm.sin((stnMetaGrid['latgrid']-grid_size/2)*nm.pi/180)

stnMetaGrid['grid_weight'] = stnMetaGrid['grid_weight']*stnMetaGrid['land_percent']

ghcnv4NoNullYears = ghcnv4[ghcnv4.year.notnull()]

ghcnv4NoNullYears = ghcnv4NoNullYears.replace(-9999,None)
