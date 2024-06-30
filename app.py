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
shapefile_path = "pasbr6.shp"

# Carregar shapefile
gdf = load_shapefile(shapefile_path)

# Verificar se o shapefile foi carregado com sucesso
if gdf is not None:
    # Verificar se o CRS é WGS84 (EPSG:4326), caso contrário, reprojetar
    if gdf.crs != "EPSG:4326":
        try:
            gdf = gdf.to_crs("EPSG:4326")
        except Exception as e:
            st.error(f"Erro ao reprojetar para EPSG:4326: {e}")
            st.stop()

    # Remover geometrias inválidas e nulas
    gdf = gdf[gdf.geometry.is_valid & gdf.geometry.notna()]
    if not gdf.empty:
        st.title("Mapa interativo com os projetos de assentamento no Paraná")
        st.write("(As informações exibidas neste site são públicas)")

        # Botão para escolher estado e município
        select_uf = st.selectbox("Escolha um estado para visualizar no mapa:", [""] + ["Todos"] + gdf["uf"].unique().tolist(), index=0)
        filtered_gdf = pd.DataFrame()

        if select_uf == "Todos":
            filtered_gdf = gdf
        elif select_uf:
            filtered_gdf = gdf[gdf["uf"] == select_uf]

        if not filtered_gdf.empty:
            select_municipio = st.selectbox("Escolha um município para visualizar no mapa:", [""] + ["Todos"] + filtered_gdf["municipio"].unique().tolist(), index=0)
            if select_municipio == "Todos":
                filtered_gdf = filtered_gdf
            elif select_municipio:
                # Filtrar GeoDataFrame pelo município selecionado
                filtered_gdf = filtered_gdf[filtered_gdf["municipio"] == select_municipio]

        # Criar um mapa inicial centrado em uma coordenada padrão
        m = folium.Map(location=[-24.0, -51.0], zoom_start=7)

        if not filtered_gdf.empty:
            # Verificar novamente se o GeoDataFrame filtrado tem geometria válida e não nula
            filtered_gdf = filtered_gdf[filtered_gdf.geometry.is_valid & filtered_gdf.geometry.notna()]
            if not filtered_gdf.empty:
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
        st.error("O shapefile contém geometrias inválidas ou vazias.")
else:
    st.error("Não foi possível carregar o shapefile.")
