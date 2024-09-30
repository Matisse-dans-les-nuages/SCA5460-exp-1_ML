#===
#IMPORTS
#===
import os
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import Point
import cartopy.io.shapereader as shpreader
import sys
import glob
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import xarray as xr
import dask

# Repertoire ou le fichier se trouve
path_file='./data/imerg_pr_201911_3h.nc4'

# Pour lire le fichier
print('Reading file: ',path_file)
ds_i = xr.open_dataset(path_file, chunks={'time':24,"lat":180,'lon':360})
ds_i.close()

#Déclaration des variables du fichier netCDF
pcpn_array = ds_i['precipitationCal']
#
# DATA CARTE 1 (organisation des données)
# #Somme des pluies sur 30 jours
pcpn_total_nov = pcpn_array.sum(dim='time')
pcpn_total_nov_dasked = pcpn_total_nov.compute()
#
# sauvegarde en CSV pour lecture facilitée
df_total_nov = pcpn_total_nov_dasked.to_dataframe().reset_index()
df_total_nov.to_csv('./data/pcpn_total_nov.csv', index=False)
#




