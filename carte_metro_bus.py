import requests
import numpy as np
import pandas as pd
from datetime import date, datetime

from bokeh.plotting import figure, ColumnDataSource, show
from bokeh.models import HoverTool, Div
from bokeh.layouts import layout
from bokeh.palettes import Sunset6


def coor_wgs84_to_web_mercator(lon, lat):
    """Converts decimal longitude/latitude
    to Web Mercator format
    """
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)


def frequentation_date(date:datetime, nom_ligne):
    """Pour une heure de départ retourne
    le niveau de fréquentation associées
    ou la valeur "Non mesurée" si les 
    horaires ne correspondent pas
    """
    frequentation = "Non mesurée"
    requete = "Ligne=='"+nom_ligne+"'"
    df = data_freq.query(requete)
    for ligne in range(0,len(df)):
        if (df.iloc[ligne, 2] <= date ) and (date < df.iloc[ligne+1, 2]):
            frequentation = df.iloc[ligne, 0]
            break
        
    return frequentation


def donnees_actuel_ligne(url:str):
    """Mise en forme des données API
    Cette fonction renvoie un dataframe
    contenant les informations associé
    à l'API d'une ligne du reseau STAR 
    """
    reponse = requests.get(url)
    contenue = reponse.json()
    passage_temps_reel = contenue["results"]
    data_passage = pd.DataFrame(passage_temps_reel)
    #Supprime les arrêts incohérent 
    data_passage.dropna(inplace=True)
    #Separe la colonne coordonnees en 2 colonne lat et lon
    data_passage["coordonnees"] = data_passage["coordonnees"].apply(lambda coord: coor_wgs84_to_web_mercator(coord['lon'], coord['lat']) )
    #Convertit les coordonnées en mercator
    data_passage["lon"] = data_passage["coordonnees"].apply(lambda coord: coord[0])
    data_passage["lat"] = data_passage["coordonnees"].apply(lambda coord: coord[1])
    #Supprime la colonne redendante
    data_passage.drop(columns=['coordonnees'], inplace=True)
    #Convertie la colonne depart en datetime
    data_passage["depart"] = pd.to_datetime(data_passage["depart"], format='%Y-%m-%dT%H:%M:%S+02:00')
    return data_passage

#### Rapatriement des données
#Requete limité à 100 element, on effectue donc une requete par ligne
URL_A = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/prochains-passages-des-lignes-de-metro-du-reseau-star-en-temps-reel/records?select=nomcourtligne%2C%20nomarret%2C%20coordonnees%2C%20depart%2C%20destination&limit=-1&timezone=Europe%2FParis&refine=precision%3A%22Temps%20r%C3%A9el%22"
URL_C4 = "https://data.explore.star.fr/api/explore/v2.1/catalog/datasets/tco-bus-circulation-passages-tr/records?select=nomcourtligne%2C%20destination%2C%20nomarret%2C%20coordonnees%2C%20depart&limit=-1&timezone=Europe%2FParis&refine=precision%3A%22Temps%20r%C3%A9el%22&refine=nomcourtligne%3A%22C4%22"
URL_C1 = "https://data.explore.star.fr/api/explore/v2.1/catalog/datasets/tco-bus-circulation-passages-tr/records?select=nomcourtligne%2C%20destination%2C%20nomarret%2C%20coordonnees%2C%20depart&limit=-1&timezone=Europe%2FParis&refine=precision%3A%22Temps%20r%C3%A9el%22&refine=nomcourtligne%3A%22C1%22"
URL_C3 = "https://data.explore.star.fr/api/explore/v2.1/catalog/datasets/tco-bus-circulation-passages-tr/records?select=nomcourtligne%2C%20destination%2C%20nomarret%2C%20coordonnees%2C%20depart&limit=-1&timezone=Europe%2FParis&refine=precision%3A%22Temps%20r%C3%A9el%22&refine=nomcourtligne%3A%22C3%22"
URL_C6 = "https://data.explore.star.fr/api/explore/v2.1/catalog/datasets/tco-bus-circulation-passages-tr/records?select=nomcourtligne%2C%20destination%2C%20nomarret%2C%20coordonnees%2C%20depart&limit=-1&timezone=Europe%2FParis&refine=precision%3A%22Temps%20r%C3%A9el%22&refine=nomcourtligne%3A%22C6%22"

liste_API = [URL_A, URL_C1, URL_C3, URL_C4, URL_C6]
nom_ligne = ["a", "C1", "C3", "C4", "C6"]

#### Rapatriement des informations de frequentation
data_freq = pd.read_csv("data/mkt-frequentation-niveau-freq-max-ligne.csv", sep=";") 
data_freq.query("Jour_semaine == 'Lundi-vendredi' and Ligne in ['Ligne a', 'C1',  'C3', 'C4', 'C6']", inplace=True)
#Utilisation du meme nom de ligne pour les 2 dataframe
data_freq.replace({'Ligne': {'Ligne a': 'a'}}, inplace=True)
data_freq = data_freq[["Tranche_horaire", "Fréquentation", "Ligne"]].sort_values("Tranche_horaire")

#### Creation de la date complete
today = str(date.today())
data_freq["date_horaire"] = data_freq["Tranche_horaire"].apply(lambda horaire: today+" "+horaire)
data_freq["date_horaire"] = pd.to_datetime(data_freq["date_horaire"], format='%Y-%m-%d %H:%M')
data_freq.drop(columns=['Tranche_horaire'], inplace=True)


#Concaténation des informations
DATA_LIGNES = pd.DataFrame()
for api in liste_API:
    """Concaténation des données de l'ensemble des lignes de bus et metro"""
    DATA_LIGNES = pd.concat([DATA_LIGNES, donnees_actuel_ligne(api)])

#### Associer à chaque horaire une colonne fréquentation
DATA_LIGNES["Frequentation"] = DATA_LIGNES.apply(lambda x: frequentation_date(x.depart, x.nomcourtligne), axis=1 )
# Attribution d'une couleur pour chaque ligne
data_couleur = pd.DataFrame.from_dict({'nomcourtligne': nom_ligne, 'couleur': Sunset6[0:5]})
DATA_LIGNES = DATA_LIGNES.merge(data_couleur, on='nomcourtligne', how='left')


titre = "Carte des principales lignes du réseau STAR"
#Creation du texte à afficher sur la page
commentaire1 = Div(text= "<p><b>Dernière mise à jour :</b> " + datetime.now().strftime("Le %d/%m/%Y à %H:%M")+"</p>" )
commentaire2 = Div(text= "<p><b>REMARQUE :</b> Les stations dotées de 2 quais voient leurs points de localisation superposés sur la carte.</p>" )
commentaire3 = Div(text= """
<p><b>INSTRUCTION :</b></p>
<p>En clicant sur une station, vous pourrez découvrir les horaires et niveaux de\
fréquentation pour les deux prochains passages dans une direction donnée. Vous avez également la possibilité de cliqué sur la légende pour masquer les stations liées à la ligne de bus et/ou de métro.</p>""",
                    width=250)


carte_metro = figure(x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom",
                     tools="wheel_zoom, pan, reset, tap", title=titre, 
                     height=600, width=1200 )
#Format du titre
carte_metro.title.align = "center"
carte_metro.title.text_color = "olive"
carte_metro.title.text_font_size = "25px"
carte_metro.title.background_fill_color = "#F5F5DC"
#Mise en place du fond de carte
carte_metro.add_tile("CartoDb Positron")


#### Représenter chaque arrêt de metro sur une carte

for nom in nom_ligne:
    #Creation d'un scatter pour chaque ligne
    requete = "nomcourtligne=='"+nom+"'"
    DATA_SOURCE = ColumnDataSource(DATA_LIGNES.query(requete))

    carte_metro.scatter(x="lon", y="lat", size=30, source=DATA_SOURCE,
                        fill_alpha=0.7, fill_color="couleur", selection_color="firebrick",                   
                        nonselection_fill_alpha=0.2, nonselection_fill_color="green",                   
                        nonselection_line_color="firebrick", nonselection_line_alpha=1.0,
                        legend_label=nom, muted_alpha=0)

#Faire disparaitre les lignes differentes de celle selectionné
carte_metro.legend.click_policy="mute"

#Suppression du cadrillage du graphique
carte_metro.xgrid.grid_line_color = None
carte_metro.ygrid.grid_line_color = None
#Suppression du logo BOKEH
carte_metro.toolbar.logo = None
#Creation de l'outils de suvole ave les informations
#de chaque station
outilsurvol = HoverTool(
    tooltips=[  ("Ligne", "@nomcourtligne"),
                ("Station", "@nomarret"),
                ("destination", "@destination"),
                ("depart", "@depart{%T}"),
                ("Frequentation", "@Frequentation"),
            ] ,
    
    formatters={'@Ligne': 'printf',
                '@Station': 'printf',
                '@destination': 'printf', 
                '@depart': 'datetime',
                '@Frequentation': 'printf',
                }
    )
#Ajout de l'outil au graphique
carte_metro.add_tools(outilsurvol)
#Mise en forme du texte et de la carte sur la page
layout_carte = layout([ [carte_metro, 
                         [commentaire3]
                         ],
                       
                       [commentaire1], 
                       [commentaire2],] )

#show(layout_carte)