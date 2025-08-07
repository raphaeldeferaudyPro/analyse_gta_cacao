##07/08/2025 12H00
##permet un affichage web comme la version 6 + import d'un format csv et non excel ce qui est beaucoup plus rapide

#on importe les bibliothèques
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
import plotly.graph_objs as go

#on ouvre le fichier excel, parse_dates =[0] indique à Python que la première colonne est une colonne de dates
fichier = "export_simplifie7.csv"
@st.cache_data
def charger_dataframe():
    df = pd.read_csv(fichier,parse_dates= [0])
    return df


df = charger_dataframe()

#on crée un tableau avec les noms des colonnes sur la première ligne
nom_colonnes = df.head(1)
#print(nom_colonnes)
nom_colonnes = nom_colonnes.drop('Date',axis=1)

#on ouvre un tableau contenant pour chaque variable : 
# son identifiant (entête colonne)
# sa désignation (ligne 0)
# le titre pour l'axe des ordonnées (ligne 1)
# le minimum de l'axe des ordonnées (ligne 2)
# le maximum de l'axe des ordonnées (ligne 3)

infos_variables = pd.read_excel('infos_variables.xlsx',engine='openpyxl',parse_dates= [0])

#on crée une liste avec les noms des colonnes, cela permettra ensuite de sélectionner la colonne avec un nom parlant (pression echappement plutôt que GTA.ME084)
liste_nom_colonnes = nom_colonnes.iloc[0].tolist()
liste_nom_colonnes = [x for x in liste_nom_colonnes if not pd.isna(x)] #on retire le titre de la date NaT


def trouver_colonne(valeur_cherchee: str, df):
    valeur_cherchee = valeur_cherchee.lower()
    return df.columns[(df.iloc[0].str.lower() == valeur_cherchee)][0]


#on supprime les lignes avec au moins un NA
df = df.dropna(how="any") 

#on remplace les valeurs "NS" par NA
df = df.replace("NS", pd.NA) 

#on isole la colonne de date pour éviter qu'elle ne soit écrasée en NaN
colonne_date = df["Date"]

#on supprime la colonne date dans le tableau df
df = df.drop('Date', axis=1)

#remplace les NA par NaN ce qui permet de tracer dans MatPlotlib
df= df.replace("NA", pd.NA).apply(pd.to_numeric, errors="coerce")

#on rajoute la colonne date au début du tableau df
df = pd.concat([colonne_date,df],axis=1)

#la colonne "Date" devient l'index du tableau
df = df.set_index("Date")
df = df.sort_index()

df = df.dropna()

#A partir de cette étape on dispose d'un tableau propre et exploitable


# Interface
st.title("GTA CACAO : visualisation des données")
#st.write("Sélectionnez une variable à tracer en fonction du temps :")

# Menu déroulant avec les noms de colonnes
colonne_choisie1 = st.selectbox("Sélectionnez une variable à tracer en fonction du temps :", liste_nom_colonnes)

#on récupère l'entête (GTA.MExxx) correspondant à la variable à tracer
entete1 = trouver_colonne(colonne_choisie1,nom_colonnes)

# Option pour activer une seconde courbe
afficher_deuxieme = st.checkbox("Afficher une deuxième courbe")

# Initialisation de la variable secondaire
colonne_choisie2 = None

if afficher_deuxieme:
    # Liste sans la variable principale
    autres_colonnes = [col for col in liste_nom_colonnes if col != colonne_choisie1]
    
    if autres_colonnes:
        colonne_choisie2 = st.selectbox("Sélectionner la seconde variable :", autres_colonnes)
    else:
        st.warning("Aucune autre variable disponible.")


#on récupère l'entête (GTA.MExxx) correspondant à la variable à tracer
if afficher_deuxieme and colonne_choisie2 and colonne_choisie2 != colonne_choisie1 :
    entete2 = trouver_colonne(colonne_choisie2,nom_colonnes)        

#Choix de la période temporelle
min_date = df.index.min().date()
max_date = df.index.max().date()
start_date, end_date = st.date_input("Choisir la période à afficher :",[min_date,max_date],min_value=min_date, max_value=max_date)

#Filtrage du tableau sur la période choisie
mask = (df.index.date >= start_date) & (df.index.date <= end_date)
df_filtered = df.loc[mask]

# Tracé du graphique
fig = go.Figure()

# Trace de la variable principale
fig.add_trace(go.Scatter(
    x=df_filtered.index,
    y=df_filtered[entete1],
    name=colonne_choisie1,
    yaxis="y1",
    mode='lines',
    line=dict(color="blue")
))

# Trace de la variable secondaire (si activée et différente)
if afficher_deuxieme and colonne_choisie2 != colonne_choisie1 :
    fig.add_trace(go.Scatter(
        x=df_filtered.index,
        y=df_filtered[entete2],
        name=colonne_choisie2,
        yaxis="y2",
        mode='lines',
        line=dict(color="red")
    ))

# Mise en page du graphique avec deux axes Y
fig.update_layout(
    title=f"Évolution de {colonne_choisie1}",
    xaxis=dict(title="Temps"),
    yaxis=dict(
        title=dict(
            text=infos_variables[entete1][1],
            font=dict(color="blue")
        ),
        tickfont=dict(color="blue"),
        range=[infos_variables[entete1][2],infos_variables[entete1][3]]
    ),
    yaxis2=dict(
        title=dict(
            text=infos_variables[entete2][1] if colonne_choisie2 else "",
            font=dict(color="red")
        ),    
        tickfont=dict(color="red"),
        overlaying="y",
        side="right",
        range=[infos_variables[entete2][2],infos_variables[entete2][3]] if colonne_choisie2 else [0,0]
    ),
    legend=dict(x=0, y=1.1, orientation="h"),
    margin=dict(l=50, r=50, t=60, b=40)
)

# Affichage du graphique dans Streamlit
st.plotly_chart(fig, use_container_width=True)

#fig = px.line(df_filtered,x=df_filtered.index,y= entete,title=f"{colonne_choisie} en fonction du temps",labels={entete: infos_variables[entete][1]},range_y=[infos_variables[entete][2],infos_variables[entete][3]])

#st.plotly_chart(fig,use_container_width=True)




