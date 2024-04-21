from bokeh.layouts import column
from bokeh.plotting import figure, show, ColumnDataSource, output_file
from bokeh.models import HoverTool, Div
from math import pi
import requests
import json
import pandas as pd


## Récupération des données en API directement sur le site en sélectionnant uniquement les données qui nous intéresse

url = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/etat-des-stations-le-velo-star-en-temps-reel/records?select=nom%2C%20coordonnees%2C%20nombreemplacementsactuels%2C%20nombrevelosdisponibles%2C%20lastupdate&limit=-1"

http_headers = {'User-Agent': "Mozilla/5.0"}
contenu_brut = requests.get(url, headers=http_headers)
contenu_json = contenu_brut.json()
d= {"nom": [],
    "capacite_velos": [],
    "velos_disponibles":[],
    "date": [],
    "lon":[],
    "lat": []}

for velo in contenu_json["results"]:
    d['nom'].append(velo["nom"])
    d["capacite_velos"].append(velo["nombreemplacementsactuels"])
    d["velos_disponibles"].append(velo["nombrevelosdisponibles"])
    d["date"].append(velo["lastupdate"])
    d["lon"].append(velo["coordonnees"]["lon"])
    d["lat"].append(velo["coordonnees"]["lat"])
df_velo = pd.DataFrame(data=d)
##  df_velo contient, sous forme de data frame, les données qui seront utilisées


## Création du diagramme en bar "fusiooné" représentant la proportion des vélos disponibles et la capacité de la station
dt_source = ColumnDataSource(df_velo)

p = figure(x_range=df_velo['nom'],  sizing_mode="stretch_width", 
           tools="", title= "Disponibilité des velos en fonction de la capacité initiale de la station",
           y_axis_label="Vélos disponibles")

p.vbar(x="nom", top="capacite_velos", width=0.9, color="blue", alpha=1, legend_label="capacité de la station", source=dt_source)
p.vbar(x="nom", top="velos_disponibles", width=0.9, color="red", alpha=0.5, legend_label="vélos disponibles", source=dt_source) 
popup = HoverTool(tooltips=[("Quartier:","@nom"), ("Capcité initiale:", "@capacite_velos"), ("Vélos disponibles: ","@velos_disponibles")]) # Création du popup avec les informations à présenter
p.add_tools(popup)


p.xaxis.major_label_orientation = pi/2   # rotation des nom en abscisse de 90°
p.legend.location = "top_left"           # Insertion de la légende en haut et gauche

# Insertion des textes présentant et expliquant notre graphique
div = Div(text="""
<html lang="fr">
<head>
    <title>Rapport sur l'utilisation des stations de vélos à Rennes</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 20px;
            padding: 20px;
            background-color: #f9f9f9;
            color: #333;
        }
        h1 {
            color: #007bff;
            text-align: center;
        }
        p {
            text-align: justify;
            margin-bottom: 20px;
        }
        .important {
            font-weight: bold;
            color: #dc3545;
        }
    </style>
</head>
<body>
    <h1>Analyse de l'utilisation des stations de vélos à Rennes</h1>
    <p>Cette page présente une analyse détaillée sur l'utilisation des stations de vélos à Rennes, mettant en lumière les informations clés sur la disponibilité des vélos et la capacité initiale des stations.</p>
    
    <p>Les données sont mises à jour toutes les 3 à 4 minutes pour assurer une précision maximale, offrant ainsi aux utilisateurs la possibilité de connaître en temps réel la disponibilité des vélos dans chaque station.</p>
    
    <p>Cette visualisation permet d'améliorer l'expérience des utilisateurs en leur fournissant des informations utiles pour choisir une station de vélos disponible. Elle permet également d'identifier les quartiers de Rennes où la demande de vélos est souvent élevée par rapport à la capacité des stations.</p>
    
    <p class="important">Cela pourrait indiquer la nécessité d'ajuster les capacités de stockage ou d'installer de nouvelles stations dans ces zones pour répondre à la demande croissante.</p>
</body>
</html>
""")

p.toolbar.logo=None  # Suppression du logo bokeh

# Un peu de mise en forme
p.title.text_color = "olive"
p.title.text_font_size = "25px"
p.title.text_font_style = "italic"

layout_velo = column(p, div)  # Disposition des différents éléments