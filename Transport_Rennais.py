#!/usr/bin/python3

"""
    Ce scripte présente un dashbord
    sur l'utilisation des transports
    à Rennes et ses alentours
    à partir de la librairie BOKEH 3.3.3

    Usage
    -----
    python -m Transport_Rennais.py (pour lancer le script et avoir la sorti html)
    ou pour la version dynamique
    bokeh serve --show Transport_Rennais.py (pour lancer le serveur en local)
"""

__authors__ = ("DELAR Emmarius", "KENANG KENANG Kevin")
__date__ = "2024-04-21"
__version__ = "1.0.0"


from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.plotting import show
from bokeh.models import Tabs, TabPanel, Div
from bokeh.client import push_session

from velos import layout_velo
from carte_metro_bus import layout_carte
from gapminder_chiffre_frequentation import layout_gap
from graphique_frequentation import layout_page_frequentation


# En-tête
en_tete = """<h2>Ce projet vous est présenté par DELAR Emmarius et KENANG KENANG Kevin.</h2>
<p>Ce tableau de bord interactif offre une analyse approfondie sur l'utilisation des lignes de métro, de bus et des vélos STAR dans la ville de Rennes, permettant ainsi aux utilisateurs Rennais d'optimiser leurs déplacements.
Notre application a pour but de permettre à ses utilisateurs de comparer le niveau de fréquentation des différentes lignes à des horaires données, visualiser en temps réel la disponibilité des vélos STAR et l'horaire des 
prochains passage du métro de la ligne a et de certaines lignes de bus. Enfin, pour une analyse encore plus fine, une visualisation dynamique de la frequentation par interval de 15 minutes est proposé en dernière pages.</p>"""
title = Div(text=en_tete)

# Onglet 1 
tab1 = TabPanel(child=layout_page_frequentation, title="Frequentation des lignes du reseaux STAR")
# Onglet 2
tab2 = TabPanel(child=layout_carte, title="Carte des principales lignes du réseau STAR")
# Onglet 3 
tab3 = TabPanel(child=layout_velo, title="Disponibilité des vélos STAR sur Rennes")
# Onglet 4
tab4 = TabPanel(child=layout_gap, title="Frequentation des lignes du réseau par tranche horaire")

tabs = Tabs(tabs = [tab1, tab2, tab3, tab4])

layout = column(title, tabs)

#Sortie HTML
show(layout)
#Creation du server pour la page web avec interaction
curdoc().title = "Transport à Rennes métropole"
curdoc().add_root(layout)