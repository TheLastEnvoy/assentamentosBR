import streamlit as st
import geopandas as gpd
import folium
import requests
import zipfile
import io

def download_and_extract_zipfile(url, output_dir):
    response = requests.get(url)
    with open('temp.zip', 'wb') as f:
        f.write(response.content)
    with zipfile.ZipFile('temp.zip', 'r') as zip_ref:
        zip_ref.extractall(output_dir)

# URLs dos arquivos shapefile no GitHub (com permalinks)
bandeirantes_url = 'https://github.com/TheLastEnvoy/mapaStreamlit/blob/fe7d2326ffcc4fcc99432e75de67ca40e7680b74/shpsBandeirantes.zip'
perimetro_url = 'https://github.com/TheLastEnvoy/mapaStreamlit/blob/aa9c6d7c981387ed29f6c5a73e5af4c6c9cd0c0c/shpsPerimetro.zip'

output_dir_bandeirantes = 'temp/bandeirantes'
output_dir_perimetro = 'temp/perimetro'

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
