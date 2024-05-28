import streamlit as st
import pandas as pandas
import plotly.express as pl

# Configurações gerais da página
projectTitle = "Top Hits Spotify 1998-2020"
st.set_page_config(
    page_title= projectTitle,
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
    )

# Estilização CSS 
with open('style.css', 'r') as fp:
    st.markdown(f"<style>{fp.read()}</style>", unsafe_allow_html=True)

# Carregamento, atribuição e tratamento de dados
dataset = pandas.read_csv('data/songs_normalize.csv')

# Sidebar (barra lateral)
with st.sidebar:
    st.title(projectTitle)
    
    artists = st.multiselect("#### Artistas:", sorted(set(dataset['artist'])), placeholder= 'All') # Definir o valor selecionado de artista
    artists = dataset['artist'] if not artists else artists # Definir artistas como todos caso não haja seleção do usuário
    
    genres = st.multiselect("#### Gêneros:", sorted(set(dataset['genre']), key=len), placeholder= 'All') # Definir o valor selecionado de artista
    genres = dataset['genre'] if not genres else genres # Definir generos como todos caso não haja seleção do usuário
    
    song = st.multiselect("#### Músicas:", sorted(set(dataset['song'])), placeholder= 'All') # Definir o valor selecionado de artista
    song = dataset['song'] if not song else song # Definir musicas como todas caso não haja seleção do usuário
    
    col1, col2 = st.columns(2)
    earliest_year, latest_year = dataset['year'].min(), dataset['year'].max()
    date_range = st.slider(label="#### Date range:", value=[earliest_year, latest_year], min_value=earliest_year, max_value=latest_year)
    min_tempo, max_tempo = dataset['tempo'].min(), dataset['tempo'].max()
    tempo_range = st.slider(label="#### Tempo range:", value=[min_tempo, max_tempo], min_value=min_tempo, max_value=max_tempo,step=float(10))

filtered_data = dataset[dataset['artist'].isin(artists) & 
                        dataset['song'].isin(song) &
                        dataset['year'].between(date_range[0], date_range[1], inclusive='both') &
                        dataset['genre'].isin(genres) &
                        dataset['tempo'].between(tempo_range[0], tempo_range[1], inclusive='both')
                        ]

artist_popularity = filtered_data.groupby('artist')['popularity'].sum()

top_artists = 10
# Sort the artists by their total popularity in descending order and get the top 10
top_10_artists = artist_popularity.sort_values(ascending=False).head(top_artists)

# Filter the DataFrame to include only the top 10 artists
top_10_data = filtered_data[filtered_data['artist'].isin(top_10_artists.index)]

def Scatter(xaxis, yaxis, title):
    if(yaxis == 'duration_ms'):
        filtered_data[yaxis] /= 1000
    scatter = pl.scatter(filtered_data, x = xaxis, y = yaxis, title = title, labels={"duration_ms": "Duração (segundos)",
                                                                                     "danceability": "Dançabilidade",
                                                                                     "energy": "Energia",
                                                                                     "loudness": "Volume",
                                                                                     "speachiness": "Falação"
                                                                                }, color=yaxis, color_continuous_scale='RdBu', hover_name='song', hover_data={'artist':True})
    scatter.update_layout(bargap=0.1)
    return scatter

def OrderedBar(xaxis, yaxis, title):
    OrderedBar = pl.bar(filtered_data.groupby(xaxis,as_index=False).sum().sort_values(by=yaxis,ascending=False).head(50), x = xaxis, y = yaxis, title = title, color='popularity', color_continuous_scale='RdBu')
    return OrderedBar

def PopularArtists(artists, songs, values, graph_type):
    if(graph_type == 'Sunburst'):
        PopularArtists = pl.sunburst(top_10_data, path=[artists, songs], values = values, width=500)
    else:
        PopularArtists = pl.treemap(top_10_data, path=[artists, songs], values = values, width=780)
        PopularArtists.update_traces(marker=dict(cornerradius=5))
    return PopularArtists

def TranslatedOption(option):
    if(option == 'Gênero'):
        return 'genre'
    elif(option == 'Duração'):
        return 'duration_ms'
    elif(option == 'Artista'):
        return 'artist'
    elif(option == 'Dançabilidade'):
        return 'danceability'
    elif(option == 'Energia'):
        return 'energy'
    elif(option == 'Volume'):
        return 'loudness'
    elif(option == 'Falação'):
        return 'speechiness'
    elif(option == 'Acústica'):
        return 'acousticness'
    elif(option == 'Instrumentalidade'):
        return 'instrumentalness'

col1, col2 = st.columns([3,1])


with col2:
    graph_type = st.selectbox(label = "Tipo de gráfico:", options=['Sunburst', 'Treemap'])

with col1:
    st.markdown("#### Dez artistas mais populares e suas músicas:")
    fig = PopularArtists('artist', 'song', 'popularity', graph_type)
    st.plotly_chart(fig)


col1, col2 = st.columns([3,1])
with col2:
    barParameter = st.selectbox(options=['Duração', 'Dançabilidade', 'Energia', 'Volume', 'Falação', 'Acústica'], label="Parâmetro")

with col1:
    st.markdown('#### Perfil das músicas ao longo dos anos:')
    fig = Scatter('year', TranslatedOption(barParameter), "")
    st.plotly_chart(fig)

col1, col2 = st.columns([3,1])
with col2:
    profile_x_axis = st.selectbox(options=['Energia', 'Dançabilidade', 'Acústica'], label="Eixo X")
    profile_y_axis = st.selectbox(options=['Volume', 'Falação', 'Instrumentalidade'], label="Eixo X")
    
with col1:
    st.markdown('#### Correlação entre os perfis de cada música:')
    fig = Scatter(TranslatedOption(profile_x_axis), TranslatedOption(profile_y_axis), "")
    st.plotly_chart(fig)
    
st.markdown('#### Análise de popularidade:')

col1, col2 = st.columns([3,1])
with col2:
    barParameter = st.selectbox(options=['Gênero', 'Artista'], label="Parâmetro", )

with col1:
    fig = OrderedBar(TranslatedOption(barParameter), 'popularity', title='')
    st.plotly_chart(fig)

st.markdown('#### Dados:')
st.write(filtered_data)
