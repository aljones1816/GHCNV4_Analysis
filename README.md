# GHCNV4_Analysis

This simple program will take the GHCN V4 QCU (quality controlled unadjusted, or raw) monthly station data and generate a global, land-only mean temperature anomaly series using gridded anomalies.

A comparison between SimpleTemp and other global temperature datasets from organizations like NASA and the UK's Met Office can be seen [here](https://i.imgur.com/TbtHeLB.png).

## Setup
Analysis uses the GHCNV4 monthly unadjusted station data. The script should now automatically download the dataset needed, but users can also access it [here](https://www.ncdc.noaa.gov/data-access/land-based-station-data/land-based-datasets/global-historical-climatology-network-monthly-version-4).

Users will also need a land mask file, the one I used is [here](https://drive.google.com/file/d/1nSDlTfMbyquCQflAvScLM6K4dvgQ7JBj/view?usp=sharing).

## To run the analysis

1. Download the required datasets from GHCN/Dropbox
2. Run ```pip3 install -r requirements.txt``` to install necessary dependencies
4. Run the analysis.py script

It is recommended that you run this code in a virtual environment to keep dependency management straightforward.

## Overview
This dataset is a global land average. The method I used is extremely simple (so I've called the dataset simpleTemp), and applies no adjustments or corrections to the raw data whatsoever. The basic outline is as follows:

- The stations are averaged into 5x5 grids. This is because some areas of the globe have a higher station density than others, so those areas will be unequally weighted if the stations are simply averaged individually.
- The grid boxes are spatially weighted, since boxes nearer the poles are smaller than boxes nearer the equator, and some boxes are partially covered by ocean (this is only meant to be land temperature).
- The series represents the average of the monthly anomalies. This is because stations can be moved over time, or come on and offline, so the anomalies prevents spurious trends from being introduced into the data.

Importantly, I have omitted any additional processing steps (adjustments), including:

- There is no correction made for time of observation bias. This produces a very small bias for the whole globe, but is significant for regional changes, particularly in the contiguous US, where the station network is particularly dense and transient.
- There is no homogenization applied. This means that urbanization bias and station moves are not accounted for. This, again, only produces a slight bias for the global mean trend, but can be significant at the regional level.
- There is no spatial interpolation for grid boxes that have no stations - these cells are simply absent from the dataset. As a result, the polar regions are under-sampled, and because the Arctic is one of the fastest warming regions on Earth, this produces a negative bias in the global trend. This approach is similar to that used by HadCRUT in versions below 5, and consequently my analysis is most similar to HadCRUT.

