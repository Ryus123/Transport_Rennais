import pandas as pd
from bokeh.plotting import figure, ColumnDataSource, show 
from bokeh.models import (Slider, Button, HoverTool, Label, Div)
from bokeh.palettes import Plasma256
from bokeh.layouts import layout
from bokeh.io import curdoc


def get_nb_arret(ligne, horaire):
    cle = ligne, horaire
    return len(set(nb_arret[cle]))

def animate_update():
    """Creation de l'animation
    Cette fonction parcours l'ensemble
    des tranche horaire possible en booucle"""
    if (slider.value+1) >= len(tranche_horaire):
        hor = tranche_horaire[0]
    else:
        hor = tranche_horaire[slider.value + 1]
    
    slider.value = tranche_horaire.index(hor)

def slider_update(attrname, old, new):
    """Mise a jour des données
    Cette fonction effectue pour chaque tranche
    horaire, la mise à jour du ColumnDataSource
    pour qu'il ait les données correspondante
    """
    if (slider.value) >= len(tranche_horaire):
        hor = tranche_horaire[0]
    else:
        hor = tranche_horaire[slider.value]       
    label.text = str(hor[:5])
    DATA_SOURCE.data = data[hor]

def animate():
    """Definition des interaction
    Cette fonction permet de lancer
    l'animation quand l'utilisateur
    intéragit avec les boutons"""
    global callback_id
    if button.label == '► Play':
        button.label = '■ Stop'
        callback_id = curdoc().add_periodic_callback(animate_update, 300)
    else:
        button.label = '► Play'
        curdoc().remove_periodic_callback(callback_id)
        
        
data_chiffre = pd.read_csv("data/fev_chiffre_frequentation_ligne_star.csv", sep=";", decimal=",") 
data_chiffre.drop(columns=["DateFreq", "Timeo", "identifiantLigne", "Sens"], inplace=True)
tranche_horaire = [horaire for horaire in data_chiffre.TrancheHoraire15mn.sort_values().unique()]
liste_commune = [commune for commune in data_chiffre.NomCommune.unique()]

#Nombre d'arret en 15 minutes pour chaque ligne
nb_arret = data_chiffre.groupby(["NomCourtLigne", "TrancheHoraire15mn"]).NomArret.unique().to_dict()
data_chiffre["Nb_arret_TrancheHoraire15mn"] = data_chiffre[["NomCourtLigne", "TrancheHoraire15mn"]].apply(lambda x: get_nb_arret(x.NomCourtLigne , x.TrancheHoraire15mn ), axis=1)
data_chiffre.drop(columns=["NomArret"], inplace=True)
#Cacul la fréquentation moyenne par ligne, tranche horaire et commune
data_chiffre = data_chiffre.groupby(["TrancheHoraire15mn", "NomCourtLigne", "NomCommune"]).mean()
#Conserve uniquement les données avec des informations completes
#Omission de la ligne a car elle contient des valeurs trop élevés pour être sur le meme graphique
data_chiffre = data_chiffre.query("NomCourtLigne!='9999' and NomCourtLigne!='a' and NomCommune!='Non identifiée'")
#Creation d'une dataframe attribuant a chaque commune une couleur dans la palette Plasma256
#de sort a ce que les couleurs soient les plus differentes les unes des autres
indice_palette =  [(int(256/len(liste_commune))*i) for i in range(0,len(liste_commune))]
palette_commune = [Plasma256[i] for i in indice_palette]
data_couleur = pd.DataFrame.from_dict({'NomCommune': liste_commune, 'couleur': palette_commune})

data = {}

for hor in tranche_horaire:
    """Creation d'un dictionnaire de données
    (format dictionnaire) pour chaque tranches 
    horaire
    """
    df_hor = data_chiffre.iloc[data_chiffre.index.get_level_values('TrancheHoraire15mn') == hor]
    df_hor = df_hor.reset_index()  
    df_hor = df_hor.merge(data_couleur, on='NomCommune', how='left')
    data[hor] = df_hor.to_dict('list')

#Creation d'un objet ColumnDataSource pour la 1er tranche horaire (indice 0)
DATA_SOURCE = ColumnDataSource(data=data[tranche_horaire[0]])

gap_plot = figure(title='Fréquentation moyenne des lignes de bus sur 24H, sur des intervalles de 15 minutes',
                  sizing_mode="stretch_width", y_range=(0,75), x_range=(-3,25),
                  tools='save, wheel_zoom, pan, reset')
#Format du titre
gap_plot.title.align = "center"
gap_plot.title.text_color = "olive"
gap_plot.title.text_font_size = "25px"
gap_plot.title.background_fill_color = "#F5F5DC"
#Format des axes
gap_plot.yaxis.axis_label = "Nombre d'arrêt par tranche horaire"
gap_plot.xaxis.axis_label = "Fréquentation moyenne sur la ligne"
#Suppression du logo BOKEH
gap_plot.toolbar.logo = None
#Creation du texte à afficher sur le graphique
label = Label(x=-2.5, y=10, text=str(tranche_horaire[0][:5]), 
              text_font_size='80px', text_color='#eeeeee',
              text_alpha=0.8)
#Ajout du text sur le graphique
gap_plot.add_layout(label)
#Creation du nuage de point pour la tranche horaire 
#associé au ColumnDataSource
gap_plot.circle(
    x='Frequentation',
    y='Nb_arret_TrancheHoraire15mn',
    size='Nb_arret_TrancheHoraire15mn',
    source=DATA_SOURCE,
    fill_color='couleur',
    fill_alpha=0.8,
    line_color='#7c7e71',
    line_width=0.5,
    line_alpha=0.5,
)
#Création de l'outils de survol
outilsurvol = HoverTool(
    tooltips=[  ("Ligne", "@NomCourtLigne"),
                ("Commune", "@NomCommune"),
                ("Horaire", "@TrancheHoraire15mn"),
            ] ,
    
    formatters={'@Ligne': 'printf',
                '@Commune': 'printf', 
                '@Horaire': 'printf', 
                } 
    )
#Ajout de l'outils de survol au graphique
gap_plot.add_tools(outilsurvol)
#Creation du selecteur de la tranche horaire
slider = Slider(start=0, end=len(tranche_horaire), value=0, 
                step=1, title="Tranche horaire")
#Definie la nouvelle tranche horaire
slider.on_change('value', slider_update)

callback_id = None

#Creation du bouton play pour le lancement de l'animation
button = Button(label='► Play', width=60)
button.on_event('button_click', animate)

commentaire = Div(text="""
<p><b>Instruction :</b></p>                    
<p>En cliquant sur le bouton [ ► Play ], vous pourrez observer une animation illustrant\
l'évolution de la fréquentation des lignes de bus par commune, toutes les 15 minutes.\
Le bouton [ ■ Stop ] permet d'arrêter l'animation. En survolant un point, vous pourrez également retrouver les caractéristiques de celui-ci.</p>
<p><b>REMARQUE : </b>Chaque couleur  représente une commune différente que l'on peut identifier en survolant le point sur le graphique.</p>""")

layout_gap = layout([ [commentaire], [gap_plot],
                  [slider, button], ], 
                  sizing_mode='scale_width')