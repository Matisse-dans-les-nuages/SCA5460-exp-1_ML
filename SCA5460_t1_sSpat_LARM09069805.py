# Packages a importer
import os
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys
import glob
import math
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import xarray as xr

# Repertoire ou le fichier se trouve
path_file='./data/imerg_pr_201911_3h.nc4'

# Pour lire le fichier
print('Reading file: ',path_file)
ds_i = xr.open_dataset(path_file)
ds_i.close()

#Déclaration des variables du fichier netCDF
precipitation = ds_i['precipitationCal']
lat = ds_i['lat']
lon = ds_i['lon']

#======================================================
#----------     FONCTIONS DU SCRIPT        ------------
#======================================================

#N/A pour ce script

#======================================================
#----------- ANALYSE DES CHAMPS SPATIALES -------------
#======================================================
# 1. Distribution spatiale des pcpn sur tout le globe
#======================================================
# On veut seulement le 1er novembre 2019 à 12 UTC des données
precipitation_nov1 = precipitation.sel(time='2019-11-01T12:00:00').where((lat <= 60 ) & (lat >= -60))

# On garde seulement les valeurs entre 0 et 20 mm
precipitation_filt = precipitation_nov1.where((precipitation_nov1 >= 0) & (precipitation_nov1 <= 20))
print(lon.shape, lat.shape, precipitation_filt.shape)
#choix de la projection. Ici, nous avons besoin de Lambert
fig, ax = plt.subplots(
    subplot_kw={'projection': ccrs.LambertCylindrical()},
    figsize=(12, 6))

# pcolormesh
mesh = ax.pcolormesh(
        lon,
            lat,
            precipitation_filt,
            cmap='bone_r',
            vmin=0,
            vmax=20,
            transform=ccrs.PlateCarree())

# Limites des côtes
ax.coastlines()

# Étiquettes de latitude et longitude sur les abcisses et ordonnés
ax.set_xticks(np.arange(-180, 181, 60), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree())

# Barre des couleurs
cbar = plt.colorbar(mesh, orientation='vertical', pad=0.02,shrink=0.7, aspect=15, ax=ax)
cbar.set_label(r'Taux de précipitation [mm 3$h^{-1}$]', fontsize=12)

# Titre au graphique et aux axes
ax.set_title("Distribution spatiale du taux de précipitation\nsur l'ensemble du globe\n1er novembre 2019 à 12 UTC",
             fontsize=14)
ax.set_ylabel("Latitudes [°]", fontsize=12)
ax.set_xlabel("Longitudes [°]", fontsize=12)

# Graphique
# plt.savefig(f"./fig/Globe_taux_pcpn_01-11-2019.png", dpi=300)
plt.show()

# #======================================================
# # 2. Histogramme des valeurs de pcpn sur tout le globe
# #======================================================

# Liste des valeurs de précipitation
precipitation_val = precipitation.values.flatten()

# Histogramme
plt.figure(figsize=(10, 6))
plt.grid(True,which='major', axis='y', color='black', linestyle='-', linewidth=0.5)
plt.grid(True, which='minor', axis='y', color='grey', linestyle='--', linewidth=0.25)

plt.hist(precipitation_val,
         bins=20,
         range=(0, np.nanmax(precipitation_val)),
         log=True,
         color='cornflowerblue',
         edgecolor='black'
         )

# Titre du graphique et des axes
plt.xlabel(r'Taux de précipitation [mm 3$h^{-1}$]', fontsize=12)
plt.ylabel('Nombre de valeurs ', fontsize=12)
plt.title('Histogramme des intensités de précipitation\n1er novembre 2019 à 12 UTC', fontsize=14)


# Graphique
# plt.savefig(f"./fig/Hist_nVal_taux_pcpn_moy_novembre.png", dpi=300)
plt.show()
# #======================================================
# # 3. Distribution spatiale des pcpn moyennes
# #    sur tout le globe
# #======================================================
# Faire la moyenne globale
# On garde seulement les valeurs entre 0 et 5 mm
precipitation_moy = precipitation.where((lat <= 60 ) & (lat >= -60)).mean(dim='time')
precipitation_moy_5mm=precipitation_moy.where((precipitation_moy >= 0) & (precipitation_moy <= 5) )

fig, ax = plt.subplots(
    subplot_kw={'projection': ccrs.LambertCylindrical()},
    figsize=(12, 6))

# Pcolormesh pour afficher les données de précipitation
mesh = ax.pcolormesh(
        lon,
            lat,
            precipitation_moy_5mm,
            cmap='bone_r',
            vmin=0,
            vmax=5,
            transform=ccrs.PlateCarree())

# Limites de côte
ax.coastlines()

# Ticks de latitude et longitude
ax.set_xticks(np.arange(-180, 181, 60), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(-90, 91, 30), crs=ccrs.PlateCarree())

cbar = plt.colorbar(mesh, orientation='vertical', pad=0.02,shrink=0.7, aspect=15, ax=ax)
cbar.set_label(r'Taux de précipitation moyen [mm 3$h^{-1}$]', fontsize=12)

# Titre du graphique et des axes
ax.set_title("Distribution spatiale du taux de précipitation moyens\nsur l'ensemble du globe\npour le mois de novembre 2019",
             fontsize=14)
ax.set_ylabel("Latitudes [°]", fontsize=12)
ax.set_xlabel("Longitudes [°]", fontsize=12)

# Graphique
# plt.savefig(f"./fig/Globe_taux_pcpn_moy_novembre.png", dpi=300)
plt.show()
#
# #======================================================
# # 4. Histogramme des valeurs de pcpn
# #    moyennées sur tout le globe
# #======================================================

# Liste des valeurs de précipitation
precipitation_val = precipitation_moy.values.flatten()

# Histogramme
plt.figure(figsize=(10, 6))
plt.grid(True,which='major', axis='y', color='black', linestyle='-', linewidth=0.5)
plt.grid(True, which='minor', axis='y', color='grey', linestyle='--', linewidth=0.25)

plt.hist(precipitation_val,
         bins=20,
         range=(0, np.nanmax(precipitation_val)),
         log=True,
         color='cornflowerblue',
         edgecolor='black'
         )

# Titre du graphique et des axes
plt.xlabel(r'Taux de précipitation moyen [mm 3$h^{-1}$]', fontsize=12)
plt.ylabel('Nombre de valeurs ', fontsize=12)
plt.title('Histogramme des intensités de précipitation moyennes\npour l\'ensemble du globe', fontsize=14)


# Graphique
# plt.savefig(f"./fig/Hist_nVal_taux_pcpn_moy_novembre.png", dpi=300)
plt.show()

# #======================================================
# # 5. Distribution spatiale des pcpn moyennes
# #    sur une région de 2° par 2° autour de Montréal
# #======================================================
mtl = [45.5,"°N",-73.5,"°W","Montréal"] #Métropole du Québec
# Détermination des latitudes et longitudes limites des figures
lat_min = mtl[0]-1
lat_max = mtl[0]+1
lon_min = mtl[2]-1
lon_max = mtl[2]+1

# Vérifications
precipitation_mtl = precipitation.sel(lat=slice(lat_min,lat_max), lon=slice(lon_min,lon_max)).mean(dim="time")
# print(precipitation_mtl.shape)
mtl_lat = precipitation_mtl['lat'].values
# print(mtl_lat.shape)
mtl_lon = precipitation_mtl['lon'].values
# print(mtl_lon.shape)

fig, ax = plt.subplots(
    subplot_kw={'projection': ccrs.Mercator()},
    figsize=(12, 6))

# Pcolormesh pour afficher les données
mesh = ax.pcolormesh(
            mtl_lon,
            mtl_lat,
            precipitation_mtl,
            cmap='bone_r',
            vmin=0,
            vmax=1,
            transform=ccrs.PlateCarree(),
            shading ='auto')

ax.set_xticks(np.arange(lon_min, lon_max + 0.5, 0.5), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(lat_min, lat_max + 0.5, 0.5), crs=ccrs.PlateCarree())
ax.set_ylabel("Latitudes [°] (projection Mercator)", fontsize=12)
ax.set_xlabel("Longitudes [°]\n(projection Mercator)", fontsize=12)

# Ticks de latitude et longitude

cbar = plt.colorbar(mesh, orientation='vertical', pad=0.05,shrink=0.8, aspect=20, ax=ax)
cbar.set_label(r'Taux de précipitation moyen [mm 3$h^{-1}$]', fontsize=12)
# Limites de côte
ax.coastlines()
# Titre
ax.set_title("Distribution spatiale du taux de précipitation moyens\nsur la région de Montréal, pour le mois de novembre 2019 (projection Mercator)",
             fontsize=14)

# Graphique
# plt.savefig(f"./fig/MTL_taux_pcpn_moy_novembre.png", dpi=300)
plt.show()

# #======================================================
# # 6. Distribution spatiale des pcpn moyennes
# #    sur une région de 2° par 2° autour de Montréal
# #    avec contourf plutôt que pcolormesh
# #======================================================

fig, ax = plt.subplots(subplot_kw={'projection': ccrs.Mercator()}, figsize=(6, 6))

# Définir l'étendue de la région sur la carte
ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

# Contourf pour afficher les données moyennées
contour = ax.contourf(
    mtl_lon,
    mtl_lat,
    precipitation_mtl,
    levels=np.linspace(0, 1, 11),  # Définir les niveaux de contours
    cmap='bone_r',
    transform=ccrs.PlateCarree()
)

# Limites de côte
ax.coastlines()

# Ticks de latitude et longitude
ax.set_xticks(np.arange(lon_min, lon_max + 0.5, 0.5), crs=ccrs.PlateCarree())
ax.set_yticks(np.arange(lat_min, lat_max + 0.5, 0.5), crs=ccrs.PlateCarree())

# contourf
cbar = plt.colorbar(contour, orientation='vertical', pad=0.05, shrink=0.8, aspect=20, ax=ax)
cbar.set_label(r'Taux de précipitation moyen [mm 3$h^{-1}$]', fontsize=12)

# Titre du graphique et des axes
ax.set_title("Distribution spatiale du taux de précipitation moyens\nsur la région de Montréal, pour le mois de novembre 2019",
             fontsize=14)
ax.set_ylabel("Latitudes [°] (projection Mercator)", fontsize=12)
ax.set_xlabel("Longitudes [°]\n(projection Mercator)", fontsize=12)

# Graphique
# plt.savefig(f"./fig/MTL_taux_pcpn_moy_novembre_v2.png", dpi=300)
plt.show()