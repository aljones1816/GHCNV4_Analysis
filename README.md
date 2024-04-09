# GHCNV4_Analysis

This simple program will take the GHCN V4 QCU (quality controlled unadjusted, or raw) monthly station data and generate a global, land-only mean temperature anomaly series using gridded anomalies. The results are output to a csv file for further analysis.

A comparison between SimpleTemp and other global temperature datasets from organizations like NASA and the UK's Met Office can be seen [here](https://i.imgur.com/TbtHeLB.png).

## Setup

clone the repository

```bash
git clone https://github.com/aljones1816/GHCNV4_Analysis.git

cd GHCNV4_Analysis
```

Set up and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies

```bash
pip3 install -r requirements.txt
```

## To run the analysis

```bash
python3 main.py
```

## Overview

This dataset is a global land average. The method I used is extremely simple (so I've called the dataset simpleTemp), and applies no adjustments or corrections to the raw data whatsoever. The basic outline is as follows:

- The stations are averaged into 5x5 grids. This is because some areas of the globe have a higher station density than others, so those areas will be unequally weighted if the stations are simply averaged individually.
- The grid boxes are spatially weighted, since boxes nearer the poles are smaller than boxes nearer the equator, and some boxes are partially covered by ocean (this is only meant to be land temperature).
- The series represents the average of the monthly anomalies. This is because stations can be moved over time, or come on and offline, so the anomalies prevents spurious trends from being introduced into the data.

Importantly, I have omitted any additional processing steps (adjustments), including:

- There is no correction made for time of observation bias. This produces a very small bias for the whole globe, but is significant for regional changes, particularly in the contiguous US, where the station network is particularly dense and transient.
- There is no homogenization applied. This means that urbanization bias and station moves are not accounted for. This, again, only produces a slight bias for the global mean trend, but can be significant at the regional level.
- There is no spatial interpolation for grid boxes that have no stations - these cells are simply absent from the dataset. As a result, the polar regions are under-sampled, and because the Arctic is one of the fastest warming regions on Earth, this produces a negative bias in the global trend. This approach is similar to that used by HadCRUT in versions below 5, and consequently my analysis is most similar to HadCRUT.
