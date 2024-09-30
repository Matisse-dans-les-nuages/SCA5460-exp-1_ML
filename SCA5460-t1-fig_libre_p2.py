from shapely.geometry import Point
import cartogram
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import geoplot.crs as gcrs
from shapely.geometry import Polygon
import geoplot as gplt

# Charger les données de précipitations depuis le fichier CSV
csv_path = './data/pcpn_total_nov.csv'
df = pd.read_csv(csv_path)

# Filtre des latitudes non-désirées
df = df[(df['lat'] <= 60) & (df['lat'] >= -60)]

# GeoDataFrame à partir des points lat/lon du CSV
geometry = [Point(xy) for xy in zip(df['lon'], df['lat'])]
precip_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")  # Assigner le CRS EPSG:4326

# Frontières des pays (depuis un fichier shapefile fournit dans la documentation geopandas)
world = gpd.read_file('./ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp')

# Vérification que les CRS sont les mêmes
if precip_gdf.crs != world.crs:
    precip_gdf = precip_gdf.to_crs(world.crs)

# Le spatial join associe les valeurs à un pays si celles-ci sont à l'intérieur du pays
pcpn_joint_pays = gpd.sjoin(precip_gdf, world, how='left', predicate='within')

# Somme totale des précipitations dans chaque pays
pcpn_par_pays = pcpn_joint_pays.groupby('NAME')['precipitationCal'].sum().reset_index()

# Merge des données de pcpn avec les polygones des pays dans "World"
world = world.set_index('NAME').join(pcpn_par_pays.set_index('NAME'))

# On enlève les NaN
world['precipitationCal'] = world['precipitationCal'].fillna(0)

# world_exploded est une solution pour éviter d'avoir
# autre chose que des polygones simples dans nos formes, avant de créer le cartogramme
world_exploded = world.explode(ignore_index=True)

# Création du cartogramme avec geoplot
fig, ax = plt.subplots(figsize=(30, 20))

# Carte du monde, en gris pâle, avec les pays en format "original"
world.plot(
    ax=ax,
    color='lightgrey',
    edgecolor='white',
    linewidth=0.5
)

gplt.cartogram(
    world_exploded,
    scale='precipitationCal',  # L'échelle utilisée pour les données est celle des pcpn
    hue='precipitationCal',
    cmap='YlGnBu',
    linewidth=1,
    edgecolor='black',
    ax=ax,
    legend=True,
    legend_var="hue", # Les couleurs sont données en fonction de hue, qui suit les précipitations
    legend_kwargs={
        'shrink': 0.5,
        'orientation': 'vertical',
        'pad': 0.02,
        'aspect': 30
    }
)

# Titre de la barre de couleur
cbar = ax.get_figure().get_axes()[-1]
cbar.set_ylabel('Précipitations totales [mm]', fontsize=15)

# Titre de l'image
ax.set_title('Cartogramme des précipitations totales par pays\nen novembre 2019')

# Afficher le résultat
# Vu le temps de chargement de ce fichier, plutôt que de le sauvegarder ici,
# j'ai utilisé la fonciton "save" de la fenêtre matplotlib lorsque j'étais satisfait du résultat.
plt.show()