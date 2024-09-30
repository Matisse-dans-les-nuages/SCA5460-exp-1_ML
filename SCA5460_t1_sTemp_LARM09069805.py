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
# lons = ds_i['lon']
# lats = ds_i['lat']
# time = ds_i['time']
# print(time)
#======================================================
#----------     FONCTIONS DU SCRIPT        ------------
#======================================================
# rain_occurence_count : Fonction du compte d'occurence maximales de pluies
#                        Garde en mémoire le plus grand compte atteint, et renvoie cette valeur
def rain_occurence_count(array):
    max_count = 0
    count = 0
    for val in array.values:
        if val > 0:
            count+=1
        elif val == 0:
            if count > max_count:
                max_count = count
            count = 0
    return max_count

# move_coordinate : Fonction de déplacement des coordonnées géographiques
#                   pour une distance en km et des résultats en degrés décimaux.
#                   Prend en params la distance voulue, la direction, et la position actuelle,
#                   et renvoie un tuple de la position modifiée, en degrés décimaux. (lat, lon)

def move_coordinate(dist, dir, current_lat, current_lon):
    i=["N","S","E","O"].index(dir.upper())
    s=(-1)**i
    e=(2%(i+1))/2
    move = ((s*(dist))/(111.32*(math.degrees(math.cos(current_lat))**e)))

    return (current_lat+((1-e)*move),
            current_lon+(e*move))

# local_time : Fonction qui prend le temps UTC et la longitude
#              et la traduit en heure locale. Seule l'heure est conservée ici,
#              puisque les données sont aux 3h justes.
def local_time(timeUTC, lon):
    h_rad = (math.pi/12)*(timeUTC-12+(lon/15))
    h_decim = (h_rad/(2*math.pi))*24
    return (int(h_decim) if h_decim > 0 else int(24+h_decim))


#======================================================
#---------- ANALYSE DES SÉRIES TEMPORELLES ------------
#======================================================
# 1. Variables géographiques:
#======================================================

# var = [lat,latUnit,lon,lonUnit,nom] ==> référencé par [0,1,2,3,4]
montreal = [45.5,"°N",-73.5,"°W","Montréal"] #Métropole du Québec
kualaLumpur = [3.1,"°N",101.6,"°E","Kuala Lumpur"] #Capitale de la Malaisie
pointOcean = [5,"°N",106,"°E","Point Océanique"] #Point Océanique près de la Malaisie
oulanBator = [47.9,"°N", 106.9,"°E","Oulan-Bator"] #Capitale de la Mongolie

#Liste des variables géographiques pour création des plots en boucle
geoVar=[montreal,kualaLumpur,pointOcean,oulanBator]

#======================================================
# 2. graphique de la variation du taux de précipitation
#    en fonction du temps
#======================================================
# !!!- Retirer les commentaires pour faire fonctionner la section -!!!

#Création des figures
for var in geoVar:
    precipitation.sel(
        time=slice('2019-11-01','2019-11-30')).sel(lat=var[0],lon=var[2],method='nearest').plot()
    plt.title(
        f"Précipitations du mois de novembre 2019\n"
        f"Localisation : {var[4]}, {var[0]}{var[1]},{var[2]}{var[3]}",
        fontsize=14)
    plt.xlabel("Jours, novembre 2019",fontsize=12)
    plt.ylim(0,30)
    plt.xlim(dt.date(2019, 11, 1), dt.date(2019, 11, 30))
    plt.yticks(np.arange(0, 30, 5))
    plt.minorticks_on()
    plt.grid(True,which='major', axis='y', color='grey', linestyle='-', linewidth=1)
    plt.grid(True, which='minor', axis='y', color='grey', linestyle='--', linewidth=0.5)
    plt.ylabel("Accumulations de pluie [mm/3h]",fontsize=12)
    plt.savefig(f"./fig/{var[4]}_pluie_3h_novembre.png", dpi=300)
    plt.close()
#======================================================
# 3. Calculs de quantités pour chaque emplacement
#======================================================
# !!!- Retirer les commentaires pour faire fonctionner la section -!!!
#Noms des colonnes: variables géographiques
cols = list(var[4] for var in geoVar)
print(cols)
#Lignes: valeurs à calculer
index_values = [
    "TOT_ACC", # accumulation totale
    "NB_MESURES_POS", # nombre de mesures avec un taux de précipitation supérieure à 0 [mm/3h]
    "FREQ_PRECIP", # fréquence de précipitation
    "MOY_PRECIP", # précipitation moyenne
    "INT_MOY_PRECIP", # intensité de précipitation moyenne
    "MAX_DUREE", # durée maximale d'un évènement de précipitations
    "MAX_TAUX_PRECIP", # valeur maximale du taux de précipitation
    "PEARSON_CORR"] # coefficient de corrélation Pearson, séries temporelle à 50km NSEO

# # ======================================================
#accumulation totale:
TOT_ACC = [] # Liste des valeurs pour chaque variable géographique.
             # Les valeurs conservent l'ordre des colonnes avec l'utilisation d'une boucle uniforme
for var in geoVar:
    TOT_ACC.append(
        float( # Conversion de la valeur du xarray en Float
                precipitation.sel(lat=var[0],lon=var[2],method='nearest').sum()) # Calcul de la valeur
    )

print("TOT_ACC values: ",TOT_ACC)
# # ======================================================
# # nombre de mesures avec un taux de précipitation supérieure à 0 [mm/3h]
NB_MESURES_POS = []
for var in geoVar:
    #Sélection des valeurs non-nulles d'accumulations des dernières 3h
    #Ajout à la liste de valeurs
    NB_MESURES_POS.append(
        int(
            precipitation.where(precipitation>0).sel(lat=var[0],lon=var[2],method='nearest').count() )
    )
print("NB_MESURES_POS values : ",NB_MESURES_POS)

# # ======================================================
# # fréquence de précipitation
FREQ_PRECIP = [float(x/240) for x in NB_MESURES_POS]
print("FREQ_PRECIP values : ",FREQ_PRECIP)

# # ======================================================
# # précipitation moyenne
MOY_PRECIP = []
for var in geoVar:
    #Sélection des précipitations moyennes
    MOY_PRECIP.append(
        float( # Conversion de la valeur du xarray en Float
                precipitation.sel(lat=var[0],lon=var[2],method='nearest').mean()) # Calcul de la valeur
    )
print("MOY_PRECIP values : ",MOY_PRECIP)

# # ======================================================
# # précipitation moyenne
INT_MOY_PRECIP = []
for var in geoVar:
    INT_MOY_PRECIP.append(
        float( # Conversion de la valeur du xarray en Float
                precipitation.where(precipitation>0).sel(lat=var[0],lon=var[2],method='nearest').mean()) # Calcul de la valeur
    )
print("INT_MOY_PRECIP values : ",INT_MOY_PRECIP)

# # ======================================================
# durée maximale d'un évènement de précipitations
MAX_DUREE = []
for var in geoVar:
    # Calcul du nombre maximum d'occurences d'évènement de pluie consécutifs
    # Avec la fonction du compte d'occurence consécutives définie en début de code
    # Multiplication par 3, comme chaque période concerne 3h de pluie
    MAX_DUREE.append(rain_occurence_count(precipitation.sel(lat=var[0],lon=var[2],method='nearest'))*3)

print("MAX_DUREE values : ",MAX_DUREE)

# # ======================================================
# valeur maximale du taux de précipitation
MAX_TAUX_PRECIP = []

for var in geoVar:
    # Sélection de la valeur maximale de chaque array
    MAX_TAUX_PRECIP.append(float(
        precipitation.sel(lat=var[0],lon=var[2],method='nearest').values.max())
    )

print("MAX_TAUX_PRECIP values : ",MAX_TAUX_PRECIP)

# # ======================================================
# coefficient de corrélation Pearson, séries temporelle à 50km N,S,E,O
PEARSON_CORR = {"Montréal":[],"Kuala Lumpur":[],"Point Océanique":[],"Oulan-Bator":[]}
DIRECTION = ["N","S","E","O"]
distance = 50 # km
for var in geoVar:
    for dir in DIRECTION:
        point_loc = move_coordinate(distance,dir,var[0],var[2])
        # print(var, dir, point_loc)
        var_coeff = xr.corr(
            precipitation.sel(
                time=slice('2019-11-01', '2019-11-30')).sel(
                    lat=var[0], lon=var[2],method='nearest'),
            precipitation.sel(
                time=slice('2019-11-01','2019-11-30')).sel(
                    lat=point_loc[0],lon=point_loc[1],method='nearest')
        )
        PEARSON_CORR[var[4]].append((dir,point_loc,float(var_coeff)))

# print(PEARSON_CORR)

q3_dataframe = pd.DataFrame(
    data=[TOT_ACC, NB_MESURES_POS, FREQ_PRECIP, MOY_PRECIP, INT_MOY_PRECIP, MAX_DUREE, MAX_TAUX_PRECIP,
             [PEARSON_CORR[var[4]][0][2] for var in geoVar], [PEARSON_CORR[var[4]][1][2] for var in geoVar],
             [PEARSON_CORR[var[4]][2][2] for var in geoVar], [PEARSON_CORR[var[4]][3][2] for var in geoVar]
          ],
    index=["TOT_ACC", "NB_MESURES_POS", "FREQ_PRECIP", "MOY_PRECIP", "INT_MOY_PRECIP", "MAX_DUREE", "MAX_TAUX_PRECIP",
            "PEARSON_CORR N", "PEARSON_CORR S", "PEARSON_CORR E", "PEARSON_CORR O"
           ],
    columns = [var[4] for var in geoVar])
q3_dataframe.to_csv("./data/q3_dataframe.csv")

#======================================================
# 3f. Scatterplot de la variation du taux de précipitation
#    en fonction du temps pour chaque emplacement et des points
#    situés à 50 km NSEO
#======================================================
# # !!!- Retirer les commentaires pour faire fonctionner la section -!!!
#
# # #Création des figures

for var in geoVar:
    plt.figure(figsize=(8, 4))
    #Emplacement géographique initial
    var_pcpn = precipitation.sel(time=slice('2019-11-01', '2019-11-30')
                                 ).sel(lat=var[0], lon=var[2], method='nearest')
    var_pcpn.where(var_pcpn > 0.5, drop=True
                   ).plot.scatter(label=f"{var[4]}", s=100, alpha=1, linewidth=0, marker="x", color="black")
    #Points à 50km NSEO
    for dir in DIRECTION:
        point_loc = move_coordinate(distance, dir, var[0], var[2])
        loc_pcpn = precipitation.sel(time=slice('2019-11-01', '2019-11-30')
                    ).sel(lat=point_loc[0], lon=point_loc[1], method='nearest')
        loc_pcpn.where(loc_pcpn > 0.5, drop=True
               ).plot.scatter(label = f"50 [km] {dir}", s=50, alpha=0.5, linewidth=0, marker="o")


    #Configuration de la figure:
    plt.title(
        f"Précipitations du mois de novembre 2019\n"
        f"Localisation : {var[4]}, {var[0]}{var[1]},{var[2]}{var[3]}\n"
        f"Comparé à 4 points à 50 km N, S, E et O",
        fontsize=12)
    plt.xlabel("Jours, novembre 2019",fontsize=12)
    plt.ylabel("Accumulations de pluie [mm/3h]", fontsize=12)
    plt.ylim(2,30)
    plt.xlim(dt.date(2019, 11, 1), dt.date(2019, 11, 30))
    plt.yticks(np.arange(0, 30, 5))
    plt.minorticks_on()
    plt.grid(True,which='major', axis='y', color='grey', linestyle='-', linewidth=1)
    plt.grid(True, which='minor', axis='y', color='grey', linestyle='--', linewidth=0.5)
    plt.ylabel("Accumulations de pluie [mm/3h]",fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"./fig/{var[4]}_pluie_scatterNSEO_novembre.png", dpi=300)
    plt.show()
    # plt.close()

#======================================================
# 4.    Graphique du cycle journalier de précipitation
#       3h, 6h ,9h et 12h pour chaque emplacement
#       Normalisé à l'heure locale
#======================================================
local_hours = [0,3,6,9,12,15,18,21]
for var in geoVar:
    mean_pcpn = []
    lon=var[2]
    for hour in local_hours:
        location_UTC_hour_mean = precipitation.sel(time=slice('2019-11-01','2019-11-30')
                                        ).sel(lat=var[0],lon=var[2],method='nearest'
                                        ).where(precipitation['time'].dt.hour==hour, drop=True).mean()
        mean_pcpn.append([
            local_time(hour,lon),
            float(location_UTC_hour_mean)]
        )


    plt.scatter([h[0] for h in mean_pcpn],
                [h[1] for h in mean_pcpn],
                label = var[4],
                marker="+",
                s=300,
                color='black')
    plt.title(f"Précipitations moyennes\naux heures locales de {var[4]}")
    plt.xlabel("Heures locales\nrelatives aux heures UTC")
    plt.ylabel(r"Précipitations moyennes [mm 3$h^{-1}$]")
    plt.ylim(0,5)
    plt.yticks(np.arange(0, 5.5, 0.5))
    plt.minorticks_on()
    plt.grid(True,which='major', axis='y', color='grey', linestyle='-', linewidth=1)
    plt.grid(True, which='minor', axis='y', color='grey', linestyle='--', linewidth=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.savefig(f"./fig/{var[4]}_Hlocale_pluie_moyenne_v2.png", dpi=300)
    plt.close()






