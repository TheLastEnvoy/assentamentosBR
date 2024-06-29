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
    st.write(gdf.head())  # Mostrar as primeiras linhas do GeoDataFrame para depuração
    st.write(f"Tipo de geometria: {gdf.geom_type.unique()}")  # Mostrar os tipos de geometria
    st.write(f"CRS: {gdf.crs}")  # Mostrar o sistema de coordenadas
    
    # Verificar se o CRS é WGS84 (EPSG:4326), caso contrário, reprojetar
    if gdf.crs != "EPSG:4326":
        try:
            gdf = gdf.to_crs("EPSG:4326")
            st.write(f"Reprojetado para: {gdf.crs}")
        except Exception as e:
            st.error(f"Erro ao reprojetar para EPSG:4326: {e}")
            st.stop()

    # Verificar se o GeoDataFrame tem geometria válida
    if gdf.geometry.is_valid.all():
        # Adicionar opções de seleção no sidebar
        st.sidebar.title("Opções de Visualização")
        municipios = gdf["municipio"].unique().tolist()
        selected_municipios = st.sidebar.multiselect("Selecione os municípios:", municipios, default=municipios)

        # Filtrar GeoDataFrame pelos municípios selecionados
        filtered_gdf = gdf[gdf["municipio"].isin(selected_municipios)]

        # Criar mapa com Folium
        centroid = filtered_gdf.geometry.centroid
        m = folium.Map(location=[centroid.y.mean(), centroid.x.mean()], zoom_start=8)

        # Adicionar shapefile ao mapa
        folium.GeoJson(filtered_gdf,
                       tooltip=folium.features.GeoJsonTooltip(fields=["municipio", "area_hecta"],
                                                             aliases=["Município", "Área (hectares)"],
                                                             labels=True,
                                                             sticky=False),
                       ).add_to(m)

        # Configurar Streamlit
        st.title("Mapa Interativo com Shapefile")
        st.write("Este mapa interativo exibe dados de um shapefile.")

        # Exibir mapa no Streamlit
        folium_static(m)
    else:
        st.error("O shapefile contém geometrias inválidas.")
else:
    st.error("Não foi possível carregar o shapefile.")
