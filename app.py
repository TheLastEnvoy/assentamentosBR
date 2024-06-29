import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st

# Função para carregar shapefile
def load_shapefile(file_path):
    try:
        gdf = gpd.read_file(file_path)
        # Converter a coluna de área para numérica
        gdf['area_hecta'] = pd.to_numeric(gdf['area_hecta'], errors='coerce')
        return gdf
    except Exception as e:
        st.error(f"Erro ao carregar shapefile: {e}")
        return None

# Caminho para o shapefile no repositório
shapefile_path = "ASS_SO_1801.shp"

# Carregar shapefile
gdf = load_shapefile(shapefile_path)

# Verificar se o shapefile foi carregado com sucesso
if gdf is not None:
    # st.write(gdf.head())  # Removido para omitir a tabela de dados
    # st.write(f"Tipo de geometria: {gdf.geom_type.unique()}")  # Removido para omitir a tabela de dados
    # st.write(f"CRS: {gdf.crs}")  # Removido para omitir a tabela de dados
    
    # Verificar se o CRS é WGS84 (EPSG:4326), caso contrário, reprojetar
    if gdf.crs != "EPSG:4326":
        try:
            gdf = gdf.to_crs("EPSG:4326")
            # st.write(f"Reprojetado para: {gdf.crs}")  # Removido para omitir a tabela de dados
        except Exception as e:
            st.error(f"Erro ao reprojetar para EPSG:4326: {e}")
            st.stop()

    # Verificar se o GeoDataFrame tem geometria válida
    if gdf.geometry.is_valid.all():
        st.title("Mapa interativo com os projetos de assentamento no Paraná")
        st.write("As informações exibidas aqui já são públicas")

        # Botão para escolher município
        select_municipio = st.selectbox("Escolha um município para visualizar no mapa:", ["Todos"] + gdf["municipio"].unique().tolist())

        if select_municipio != "Todos":
            # Filtrar GeoDataFrame pelo município selecionado
            filtered_gdf = gdf[gdf["municipio"] == select_municipio]
        else:
            filtered_gdf = gdf  # Mostrar todos os municípios

        # Criar mapa com Folium
        centroid = filtered_gdf.geometry.centroid
        m = folium.Map(location=[centroid.y.mean(), centroid.x.mean()], zoom_start=8)

        # Adicionar shapefile ao mapa com tooltips personalizados
        for idx, row in filtered_gdf.iterrows():
            tooltip = f"<b>{row['nome_proje']} (Assentamento)</b><br>" \
                      f"Área: {row['area_hecta']} hectares<br>" \
                      f"Lotes: {row['capacidade']}"
            folium.GeoJson(row['geometry'],
                           tooltip=tooltip,
                           ).add_to(m)

        # Exibir mapa no Streamlit
        folium_static(m)
    else:
        st.error("O shapefile contém geometrias inválidas.")
else:
    st.error("Não foi possível carregar o shapefile.")
