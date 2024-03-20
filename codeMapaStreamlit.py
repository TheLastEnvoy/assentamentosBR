import streamlit as st
import geopandas as gpd
import folium
import shutil
import os
import urllib.request
import zipfile

# Função para baixar e extrair o arquivo ZIP
def download_and_extract_zipfile(url, output_dir):
    # Baixa o arquivo ZIP
    urllib.request.urlretrieve(url, 'temp.zip')

    # Extrai o arquivo ZIP
    with zipfile.ZipFile('temp.zip', 'r') as zip_ref:
        zip_ref.extractall(output_dir)

# URLs dos arquivos shapefile no GitHub
bandeirantes_url = 'https://github.com/TheLastEnvoy/mapaStreamlit/raw/main/bandeirantesDashboard.zip'
perimetro_url = 'https://github.com/TheLastEnvoy/mapaStreamlit/raw/main/perimetroBandeirantes.zip'

output_dir_bandeirantes = 'temp/bandeirantesDashboard'
output_dir_perimetro = 'temp/perimetroBandeirantes'

# Cria os diretórios de saída se não existirem
os.makedirs(output_dir_bandeirantes, exist_ok=True)
os.makedirs(output_dir_perimetro, exist_ok=True)

# Baixa e extrai os arquivos ZIP
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
