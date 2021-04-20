import pandas as pd

GHCNDat = "C:/Users/ALAJON/Desktop/Climate Science/GHCNV4 Analysis/ghcnm.tavg.v4.0.1.20210416.qcu.dat"
GHCNmeta = "C:/Users/ALAJON/Desktop/Climate Science/GHCNV4_Analysis/ghcnm.tavg.v4.0.1.20210416.qcu.inv"
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

# Load station metadata
stnMeta = pd.read_fwf(GHCNmeta, colspecs=[(0, 2), (0, 12), (12, 21), (21, 31),
                                       (31, 38), (38, 69)],
                 names=['country_code', 'station',
                        'lat', 'lon', 'elev', 'name'])
print(stnMeta)