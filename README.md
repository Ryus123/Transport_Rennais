Ce tableau de bord interactif offre une analyse approfondie sur l'utilisation des lignes de métro, de bus et des vélos STAR dans la ville de Rennes, permettant ainsi aux utilisateurs Rennais d'optimiser leurs déplacements. Notre application a pour but de permettre à ses utilisateurs de comparer le niveau de fréquentation des différentes lignes à des horaires données, visualiser en temps réel la disponibilité des vélos STAR et l'horaire des prochains passage du métro de la ligne a et de certaines lignes de bus. Enfin, pour une analyse encore plus fine, une visualisation dynamique de la frequentation par interval de 15 minutes est proposé en dernière pages.


Guide rapide
========

#. Avant d'exécuter le scripte assurez-vous d'avoir installer la bonne version de chaque librairie (en particulier bokeh) avec la commande : pip install -r requirements.txt

#. Le dashboard est disponible en version statique avec une sortie html et en version dynamique avec la création d'un serveur localhost temporaire (cela affecte uniquement la visualisation du graphique en dernière page). Chacune des sorties s'obtient avec une commande spécifique à exécuter dans un terminal ouvert à l'emplacement du dossier : 
    a - Pour la sortie html : lancer la commande " python Transport_Rennais.py "
    b - Pour le serveur localhost : lancer la commande " bokeh serve --show Transport_Rennais.py "

Remarque : Une fois le serveur créé, il reste actif 30 minutes.


Architecture du projet
========

Le projet est organisé en 5 scripts par soucis de clarté du code : 
    #. graphique_frequentation.py : Correspond aux graphiques de la 1er page "Frequentation des lignes du réseaux STAR" 
    #. carte_metro_bus.py : Correspond a la carte de la 2nd page "Carte des principales lignes du réseau STAR" 
    #. velos.py : Correspond au graphique de la 3e page "Disponibilité des velos STAR sur Rennes" 
    #. gapminder_chiffre_frequentation.py : Correspond au graphiques dynamique de la 4ème page "Frequentation des lignes du réseau par tranche horaire" 
    #. Transport_Rennais.py : Correspond au script qui formate la page Bokeh en regroupant l'ensemble des autres scripts.