import pandas as pd

from bokeh.layouts import gridplot, row, column
from bokeh.plotting import figure, show, ColumnDataSource
from bokeh.models import (HoverTool, CustomJS, Select, Div,
                          CustomJSTickFormatter, ColorPicker)


df = pd.read_csv("data/mkt-frequentation-niveau-freq-max-ligne.csv", sep=";") 
df = df.sort_values("Tranche_horaire")
df.fillna(0, inplace=True)
df.rename(columns={"Fréquentation": "freq"}, inplace=True)
df = df.pivot(index="Tranche_horaire", columns=["Jour_semaine", "Ligne"], values=["Niveau_fréquentation", "freq"])


category_default = "Ligne a"
unique_categories = list(df["Niveau_fréquentation"].columns.levels[1])
#Création d'une liste de graphiques et de la liste correspondante de leurs callbacks.
liste_plot = []
liste_callback = []
liste_picker = []

for periode in ["Lundi-vendredi", "Samedi", "Dimanche"]:  
    """
    Creation de graphiques du niveau de
    fréquentaion en fonction de chaque periode
    """
    
    ligne_data = df["Niveau_fréquentation"][periode].to_dict("list")  
    freq_data = df["freq"][periode].to_dict("list")
    #Creation d'un ColumnDataSource associé une periode
    DATA_SOURCE = ColumnDataSource({
        "Tranche_horaire": df.index,   
        "Ligne": ligne_data[category_default],
        "Frequence": freq_data[category_default],
        "nom" : pd.DataFrame({'nom' : [category_default]*len(freq_data[category_default])})
    })
    #Creation du graphique pour la periode
    plot_dpt = figure(title="Niveau de fréquentation du : "+periode, y_range=[x for x in df.index], 
                      x_range=["Faible", "Moyenne", "Haute"], 
                      width=500, height=700, tools="save")
    #Format du titre
    plot_dpt.title.align = "center"
    plot_dpt.title.text_color = "olive"
    plot_dpt.title.text_font_size = "15px"
    plot_dpt.title.background_fill_color = "#F5F5DC"
    
    barre = plot_dpt.hbar('Tranche_horaire', right ='Ligne', source = DATA_SOURCE,
              width=0.8, color='navy', alpha=0.4, height = 0.8)
    
    picker = ColorPicker(title="Couleur de remplissage",color=barre.glyph.fill_color)
    picker.js_link('color', barre.glyph, 'fill_color')
    
    #Mise en forme du graphique
    plot_dpt.xgrid.band_fill_color = "olive"
    plot_dpt.xgrid.band_fill_alpha = 0.1
    plot_dpt.ygrid.grid_line_alpha = 0
    #Suppression du logo BOKEH
    plot_dpt.toolbar.logo = None
    #Creation de l'outil de survole 
    outilsurvol = HoverTool(
        tooltips=[ ("Horaire", "@Tranche_horaire"),
              ("Fréquence", "@Frequence"),] ,
        formatters={ '@Horaire': 'printf',
                '@Fréquence': 'printf',}
        )

    plot_dpt.add_tools(outilsurvol)
    #Creation de l'outil interactif de selection de ligne
    select = Select(title='Choix de la ligne', value=category_default, options=unique_categories)
    #Creation de l'interaction avec le callback
    callback = CustomJS(
        args={"subset_data": [ligne_data, freq_data], "source": DATA_SOURCE},
        code="""
            source.data['Ligne'] = subset_data[0][cb_obj.value];
            source.data['Frequence'] = subset_data[1][cb_obj.value];
            source.change.emit();
        """)
    #Met a jour la valeur de la ligne de BUS/Metro
    select.js_on_change("value", callback)
    #Conserve le label de l'axe des ordonnées uniquement sur le 1er graphique
    if periode != "Lundi-vendredi":
        plot_dpt.yaxis.formatter = CustomJSTickFormatter(code=""" return '' """)
        plot_dpt.xaxis.axis_label = ""
    else:
        plot_dpt.yaxis.axis_label = "Horaire"
        plot_dpt.yaxis.major_label_text_color = "orange"
    
    plot_dpt.xaxis.axis_label = "Niveau de fréquentation"
    #Ajoute le graphique créé pour la periode à la liste de graphique
    liste_plot.append(plot_dpt)
    #Ajoute le callback associé au graphique
    liste_callback.append(row(select, picker))


div = Div(text="""
    <html lang="fr">
<body>
    <h1>L'intérêt d'un graphique de l'affluence des transports à Rennes</h1>

    <p>Ces 3 graphiques permettent de visualiser simultanément le niveau de fréquentation (faible, moyen ou fort) des bus et des lignes de métro à Rennes durant une journée en semaine et en week-end, ils permettent notamment :</p>

    <ol>
        <li><strong>Analyse de la Charge de Transport :</strong> Ce type de graphique permet de comprendre et d'analyser la charge de transport dans la ville à différents moments de la journée. Il permet d'identifier les heures de pointe et les heures creuses, ce qui est essentiel pour la planification des horaires et des capacités de transport.</li>
        
        <li><strong>Optimisation des Services de Transport :</strong> En comprenant les variations de fréquentation tout au long de la journée, les autorités de transport peuvent ajuster les fréquences de bus et de métro pour répondre à la demande. Par exemple, augmenter le nombre de véhicules pendant les heures de pointe pour améliorer l'efficacité du système.</li>
        
        <li><strong>Prise de Décision Stratégique :</strong> Les données de fréquentation visualisées sous forme de graphique aident les décideurs à prendre des décisions stratégiques concernant les investissements dans les infrastructures de transport. Par exemple, l'expansion de certaines lignes en fonction des zones de forte fréquentation.</li>
        
        <li><strong>Évaluation de la Satisfaction des Usagers :</strong> La fréquentation des transports en commun est souvent liée à la satisfaction des usagers. En visualisant les niveaux de fréquentation, il est possible de mieux comprendre les besoins et les préférences des passagers, ce qui peut conduire à des améliorations du service pour une meilleure expérience utilisateur.</li>
        
        <li><strong>Surveillance et Gestion des Événements Spéciaux :</strong> Ces graphiques sont utiles lors d'événements spéciaux ou de situations particulières (grèves, festivals, etc.) qui peuvent affecter la demande de transport en commun. La surveillance en temps réel des niveaux de fréquentation permet une gestion proactive de ces situations.</li>
    </ol>
</body>
</html>
""")

layout_frequentation = gridplot([liste_callback, liste_plot], 
                                sizing_mode="stretch_width")

layout_page_frequentation = column(layout_frequentation, div)