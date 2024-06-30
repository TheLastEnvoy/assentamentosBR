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
        st.title("Mapa interativo com os projetos de assentamento de reforma agrária no Brasil")
        st.write("A exibição de todos os assentamentos do país leva cerca de 40s, seja paciente")
        st.write("(As informações exibidas neste site são públicas)")

        # Botões para escolher filtros
        filters = {
            'Estado': st.selectbox("Escolha um estado:", [""] + gdf["uf"].unique().tolist()),
            'Município': st.selectbox("Escolha um município:", [""] + gdf["municipio"].unique().tolist()),
            'Assentamento': st.selectbox("Escolha um assentamento:", [""] + gdf["nome_proje"].unique().tolist()),
            'Código SIPRA': st.selectbox("Escolha um código SIPRA:", [""] + gdf["cd_sipra"].unique().tolist()),
            'Área (hectares)': st.selectbox("Escolha uma área:", [""] + gdf["area_hecta"].unique().tolist()),
            'Lotes': st.selectbox("Escolha a capacidade (lotes):", [""] + gdf["capacidade"].unique().tolist()),
            'Fase': st.selectbox("Escolha uma fase:", [""] + gdf["Fase"].unique().tolist()),
            'Data de criação': st.selectbox("Escolha uma data de criação:", [""] + gdf["data_de_cr"].unique().tolist()),
            'Forma de obtenção do imóvel': st.selectbox("Escolha a forma de obtenção do imóvel:", [""] + gdf["forma_obten"].unique().tolist()),
            'Data de obtenção do imóvel': st.selectbox("Escolha uma data de obtenção do imóvel:", [""] + gdf["data_obten"].unique().tolist()),
        }

        filtered_gdf = gdf.copy()
        for column, value in filters.items():
            if value:
                if column == 'Estado':
                    filtered_gdf = filtered_gdf[filtered_gdf["uf"] == value]
                elif column == 'Município':
                    filtered_gdf = filtered_gdf[filtered_gdf["municipio"] == value]
                elif column == 'Assentamento':
                    filtered_gdf = filtered_gdf[filtered_gdf["nome_proje"] == value]
                elif column == 'Código SIPRA':
                    filtered_gdf = filtered_gdf[filtered_gdf["cd_sipra"] == value]
                elif column == 'Área (hectares)':
                    filtered_gdf = filtered_gdf[filtered_gdf["area_hecta"] == value]
                elif column == 'Lotes':
                    filtered_gdf = filtered_gdf[filtered_gdf["capacidade"] == value]
                elif column == 'Fase':
                    filtered_gdf = filtered_gdf[filtered_gdf["Fase"] == value]
                elif column == 'Data de criação':
                    filtered_gdf = filtered_gdf[filtered_gdf["data_de_cr"] == value]
                elif column == 'Forma de obtenção do imóvel':
                    filtered_gdf = filtered_gdf[filtered_gdf["forma_obten"] == value]
                elif column == 'Data de obtenção do imóvel':
                    filtered_gdf = filtered_gdf[filtered_gdf["data_obten"] == value]

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
                              f"Lotes: {row['capacidade']}<br>" \
                              f"Famílias: {row['num_famili']}<br>" \
                              f"Fase: {row['Fase']}<br>" \
                              f"Data de criação: {row['data_de_cr']}<br>" \
                              f"Forma de obtenção: {row['forma_obten']}<br>" \
                              f"Data de obtenção: {row['data_obten']}"
                    folium.GeoJson(row['geometry'],
                                   tooltip=tooltip,
                                   ).add_to(m)

        # Exibir mapa no Streamlit
        folium_static(m)
    else:
        st.error("O shapefile contém geometrias inválidas ou vazias.")
else:
    st.error("Não foi possível carregar o shapefile.")
