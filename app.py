import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st
import branca.colormap as cm

# Função para carregar shapefile
def load_shapefile(file_path):
    try:
        gdf = gpd.read_file(file_path)
        # Converter a coluna de área para numérica
        gdf['area_hecta'] = pd.to_numeric(gdf['area_hecta'], errors='coerce')
        st.write(gdf.head())  # Mostrar as primeiras linhas do GeoDataFrame para depuração
        st.write(f"Tipo de geometria: {gdf.geom_type.unique()}")  # Mostrar os tipos de geometria
        st.write(f"CRS: {gdf.crs}")  # Mostrar o sistema de coordenadas
        return gdf
    except Exception as e:
        st.error(f"Erro ao carregar shapefile: {e}")
        return None

# Caminho para o shapefile e o projeto .qgz no repositório
shapefile_path = "ASS_SO_1801.shp"
project_path = "pas_ted.qgz"

# Carregar shapefile
gdf = load_shapefile(shapefile_path)

# Verificar se o shapefile foi carregado com sucesso
if gdf is not None:
    # Verificar se o CRS é WGS84 (EPSG:4326), caso contrário, reprojetar
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")
        st.write(f"Reprojetado para: {gdf.crs}")
    
    # Verificar se o GeoDataFrame tem geometria válida
    if gdf.geometry.is_valid.all():
        # Adicionar opções de seleção no sidebar
        st.sidebar.title("Opções de Visualização")
        municipios = gdf["municipio"].unique().tolist()
        selected_municipios = st.sidebar.multiselect("Selecione os municípios:", municipios, default=municipios)
        color_by_area = st.sidebar.checkbox("Colorir por área", value=True)

        # Filtrar GeoDataFrame pelos municípios selecionados
        filtered_gdf = gdf[gdf["municipio"].isin(selected_municipios)]

        # Criar mapa com Folium
        centroid = filtered_gdf.geometry.centroid
        m = folium.Map(location=[centroid.y.mean(), centroid.x.mean()], zoom_start=8)

        if color_by_area:
            # Criar um colormap baseado na área
            min_area = filtered_gdf["area_hecta"].min()
            max_area = filtered_gdf["area_hecta"].max()
            colormap = cm.linear.YlGnBu_09.scale(min_area, max_area)

            # Adicionar shapefile ao mapa com cores baseadas na área
            for _, row in filtered_gdf.iterrows():
                color = colormap(row["area_hecta"])
                folium.GeoJson(row['geometry'],
                               style_function=lambda x, color=color: {'fillColor': color, 'color': 'black', 'weight': 1},
                               popup=folium.Popup(f"{row['municipio']}: {row['area_hecta']} hectares", parse_html=True)
                               ).add_to(m)

            colormap.caption = "Área em hectares"
            m.add_child(colormap)
        else:
            # Adicionar shapefile ao mapa sem colorir por área
            for _, row in filtered_gdf.iterrows():
                folium.GeoJson(row['geometry'],
                               popup=folium.Popup(f"{row['municipio']}: {row['area_hecta']} hectares", parse_html=True)
                               ).add_to(m)

        # Configurar Streamlit
        st.title("Mapa Interativo com Shapefile e QGIS")
        st.write("Este mapa interativo exibe dados de um shapefile e um projeto QGIS.")

        # Exibir mapa no Streamlit
        folium_static(m)
    else:
        st.error("O shapefile contém geometrias inválidas.")
else:
    st.error("Não foi possível carregar o shapefile.")
