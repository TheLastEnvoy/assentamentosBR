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
shapefile_path = "pasbr4.shp"

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

    # Verificar e filtrar geometrias inválidas ou nulas
    invalid_gdf = gdf[~gdf.geometry.is_valid | gdf.geometry.isna()]
    gdf = gdf[gdf.geometry.is_valid & gdf.geometry.notna()]

    if not gdf.empty:
        st.title("Mapa interativo com os projetos de assentamento no Paraná")
        st.write("(As informações exibidas neste site são públicas)")

        # Exibir geometrias inválidas, se existirem
        if not invalid_gdf.empty:
            st.write("Geometrias inválidas ou vazias encontradas no shapefile:")
            st.write(invalid_gdf)
        
        # Botão para escolher município
        select_municipio = st.selectbox("Escolha um município para visualizar no mapa:", ["Todos"] + gdf["municipio"].unique().tolist())

        if select_municipio != "Todos":
            # Filtrar GeoDataFrame pelo município selecionado
            filtered_gdf = gdf[gdf["municipio"] == select_municipio]
        else:
            filtered_gdf = gdf  # Mostrar todos os municípios

        # Verificar novamente se o GeoDataFrame filtrado tem geometria válida e não nula
        filtered_gdf = filtered_gdf[filtered_gdf.geometry.is_valid & filtered_gdf.geometry.notna()]
        if not filtered_gdf.empty:
            # Calcular centroides
            filtered_gdf['centroid'] = filtered_gdf.geometry.centroid

            # Verificar NaNs nos centroides
            if filtered_gdf['centroid'].isna().any():
                st.error("O shapefile filtrado contém centroides inválidos ou vazios.")
                st.stop()

            # Obter coordenadas médias dos centroides
            centroid_y_mean = filtered_gdf['centroid'].y.mean()
            centroid_x_mean = filtered_gdf['centroid'].x.mean()

            # Verificar se as coordenadas médias são válidas
            if pd.isna(centroid_y_mean) ou pd.isna(centroid_x_mean):
                st.error("As coordenadas médias dos centroides são inválidas (contêm NaNs).")
                st.stop()

            # Criar mapa com Folium
            m = folium.Map(location=[centroid_y_mean, centroid_x_mean], zoom_start=8)

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
            st.error("O shapefile filtrado contém geometrias inválidas ou vazias.")
    else:
        st.error("O shapefile contém geometrias inválidas ou vazias.")
else:
    st.error("Não foi possível carregar o shapefile.")
