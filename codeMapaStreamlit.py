import streamlit as st
import geopandas as gpd
import folium
import requests
import zipfile
import io
import shutil

def download_and_extract_zipfile(url, output_dir):
    # Baixa o arquivo ZIP
    with requests.get(url, stream=True) as r:
        with open('temp.zip', 'wb') as f:
            shutil.copyfileobj(r.raw, f)
    
    # Extrai o arquivo ZIP
    with zipfile.ZipFile('temp.zip', 'r') as zip_ref:
        zip_ref.extractall(output_dir)

# URLs dos arquivos shapefile no GitHub
bandeirantes_url = 'https://github.com/TheLastEnvoy/mapaStreamlit/raw/main/bandeirantesDashboard.zip'
perimetro_url = 'https://github.com/TheLastEnvoy/mapaStreamlit/raw/main/perimetroBandeirantes.zip'

output_dir_bandeirantes = 'temp/bandeirantesDashboard'
output_dir_perimetro = 'temp/perimetroBandeirantes'

download_and_extract_zipfile(bandeirantes_url, output_dir_bandeirantes)
download_and_extract_zipfile(perimetro_url, output_dir_perimetro)

# Função para carregar e exibir o mapa a partir de um arquivo shapefile
def show_map(shapefile_path):
    # Carrega o arquivo shapefile
    gdf = gpd.read_file(shapefile_path)

    # Cria um mapa básico com o Folium
    m = folium.Map(location=[-25.4284, -49.2733], zoom_start=12)

    # Adiciona as geometrias do shapefile ao mapa
    for idx, row in gdf.iterrows():
        folium.GeoJson(row['geometry']).add_to(m)

    # Exibe o mapa no Streamlit
    st.write(m)

# Título da página
st.title('Mapa Interativo')

# Seção para exibir o mapa
st.header('Mapa de Bandeirantes')
show_map(output_dir_bandeirantes)

st.header('Perímetro de Bandeirantes')
show_map(output_dir_perimetro)
