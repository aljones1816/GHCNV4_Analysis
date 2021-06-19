# -*- coding: utf-8 -*-
"""
Created on Mon Jun 14 10:50:39 2021

@author: ALAJON
"""

import urllib.request
import tarfile

ghcnurl = 'https://www1.ncdc.noaa.gov/pub/data/ghcn/v4/ghcnm.tavg.latest.qcu.tar.gz'
target_path = 'C:/Users/ALAJON/Desktop/Climate Science/GHCNV4 Data'

ftpstream = urllib.request.urlopen(ghcnurl)
ghcnurl = tarfile.open(fileobj=ftpstream, mode="r|gz")
ghcnurl.extractall()