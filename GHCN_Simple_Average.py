import matplotlib.pyplot as plt
import pandas as pd

GHCNDat = "C:/Users/ALAJON/Desktop/Climate Science/GHCNV4 Data/ghcnm.tavg.v4.0.1.20210416.qcu.dat"
GHCNmeta = "C:/Users/ALAJON/Desktop/Climate Science/GHCNV4 Data/ghcnm.tavg.v4.0.1.20210416.qcu.inv"
landmask = "C:/Users/ALAJON/Desktop/Climate Science/GHCNV4 Data/landmask.dta"

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

ghcnv4 = pd.read_fwf(GHCNDat,
                     colspecs=colspecs, names=names)

ghcnv4NoNullYears = ghcnv4[ghcnv4.year.notnull()]
ghcnv4NoNullYears = ghcnv4NoNullYears[~ghcnv4NoNullYears.eq(-9999).any(1)]
ghcnv4NoNullYears = ghcnv4NoNullYears[~ghcnv4NoNullYears.eq(None).any(1)]

for m in range(1, 13):
    ghcnv4NoNullYears['VALUE' + str(m)] = ghcnv4NoNullYears['VALUE' + str(m)] / 100

months = ['VALUE1', 'VALUE2', 'VALUE3', 'VALUE4', 'VALUE5', 'VALUE6',
          'VALUE7', 'VALUE8', 'VALUE9', 'VALUE10', 'VALUE11', 'VALUE12']

ghcnv4NoNullYears['average'] = ghcnv4NoNullYears[months].mean(axis=1)

rawAbs = ghcnv4NoNullYears.groupby('year').mean('average').reset_index()
rawAbs = rawAbs[rawAbs['year'].between(1900, 2020)]

# plot temperature record
plt.plot(rawAbs['year'], rawAbs['average'])
plt.show()
