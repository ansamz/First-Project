import streamlit as st
from plotly.subplots import make_subplots
from urllib.request import urlopen
import plotly.graph_objects as go
import plotly.express as px
import plotly.io as pio
import pandas as pd
import numpy as np
import json
import geojson
from copy import deepcopy

with open('../data/georef-switzerland-kanton.geojson') as f:
    gs = json.load(f)

ren_en_df = pd.read_csv("../data/renewable_power_plants_CH.csv")
ren_en_df.head()

st.markdown("<h1 style='text-align: center; color: red;'>Electricity production plants in Switzerland</h1>", unsafe_allow_html=True)
#st.title("Electricity production plants in Switzerland")
st.header("Data Exploration")

if st.checkbox("Check the box if you are interested in the table"):
    st.subheader("This is my dataset:")
    st.dataframe(data=ren_en_df)

left_column,  right_column = st.columns([2, 1])
sources = ["All"]+["Map", "Graph"]
source = left_column.selectbox("Choose a Visual", sources)

show_labels = right_column.radio(
    label='Show Pie charts labels', options=['Yes', 'No'])

cantons_dict = {'TG':'Thurgau', 'GR':'Graubünden', 'LU':'Luzern', 'BE':'Bern', 'VS':'Valais',
                'BL':'Basel-Landschaft', 'SO':'Solothurn', 'VD':'Vaud', 'SH':'Schaffhausen', 'ZH':'Zürich',
                'AG':'Aargau', 'UR':'Uri', 'NE':'Neuchâtel', 'TI':'Ticino', 'SG':'St. Gallen', 'GE':'Genève',
                'GL':'Glarus', 'JU':'Jura', 'ZG':'Zug', 'OW':'Obwalden', 'FR':'Fribourg', 'SZ':'Schwyz',
                'AR':'Appenzell Ausserrhoden', 'AI':'Appenzell Innerrhoden', 'NW':'Nidwalden', 'BS':'Basel-Stadt'}

ren_en_df["canton_name"] = ren_en_df["canton"].map(cantons_dict)

canton_sources = ren_en_df.groupby("canton_name").size().reset_index(name="count")
canton_sources.head()

st.header("Number of energy sources per canton")
fig4 = px.choropleth_mapbox(canton_sources, geojson=gs, color="count",
                           locations="canton_name", featureidkey="properties.kan_name",
                           center={"lat": 46.818, "lon": 8.2275}, #swiss longitude and latitude
                           mapbox_style="carto-positron", zoom=7, opacity=0.8, width=900, height=500,
                           labels={"canton_name":"Canton",
                           "count":"Number of Sources"},
                           title="<b>Clean Energy Sources per Canton</b>",
                           color_continuous_scale="Viridis",)
fig4.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, hoverlabel={"bgcolor":"white", "font_size":12, "font_family":"Sans"})
if source == "All" or source == "Map":
    st.plotly_chart(fig4)

ren_en_df['commissioning_date'] = pd.to_datetime(ren_en_df['commissioning_date'])
ren_en_df['year'] = pd.DatetimeIndex(ren_en_df['commissioning_date']).year
plants_num = ren_en_df.groupby('energy_source_level_2').count().reset_index()

st.header("Percentage of Swiss power plants")
fig6 = px.pie(plants_num, values='company', names='energy_source_level_2', title='Composition of Swiss power plants', color_discrete_sequence=px.colors.sequential.RdBu, width=400, height=400)
if show_labels == "Yes":
    fig6.update_traces(textposition='inside', textinfo='percent+label')
fig6.update_traces(hole=.4, hoverinfo="label+percent+name")
fig6.update_layout(margin=dict(t=20, b=20, l=20, r=20))
if source == "All" or source == "Graph":
    st.plotly_chart(fig6)

st.header("Development of Sources of energy through the years")
new = ren_en_df.groupby(['year', 'energy_source_level_2']).count().reset_index()
fig7 = px.line(new, x='year', y='company', color='energy_source_level_2', markers=True, title='Different industry developements over the years',
              labels={
                     "year": "Year",
                     "company": "Number of plants",
                     "energy_source_level_2": "Sources of Energy"
                 },
                width= 1000,
                height=1000
              )
fig7.update_yaxes(tickvals=np.arange(0, 4000, 100))
if source == "All" or source == "Graph":
    st.plotly_chart(fig7)

st.header("Sources and size of Energy according to location")
fig8 = px.scatter_mapbox(ren_en_df, lat='lat', lon='lon', color='energy_source_level_2', size='electrical_capacity', hover_data=['company', 'energy_source_level_2', 'electrical_capacity'],
                          zoom=7.5, height=700,
                        labels={"energy_source_level_2": "Sources of Energy"}
                        )
fig8.update_layout(mapbox_style="open-street-map")
fig8.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
if source == "All" or source == "Map":
    st.plotly_chart(fig8)