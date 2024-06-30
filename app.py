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

# Função para formatar a área
def format_area(area):
    return f"{area:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")

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

        # Lista de colunas para filtros e seus nomes de exibição
        filter_columns = {
            'uf': 'Estado',
            'municipio': 'Município',
            'nome_proje': 'Assentamento',
            'cd_sipra': 'Código SIPRA',
            'capacidade': 'Lotes',
            'num_famili': 'Famílias beneficiárias',
            'fase': 'Fase',
            'data_de_cr': 'Data de criação',
            'forma_obte': 'Forma de obtenção do imóvel',
            'data_obten': 'Data de obtenção do imóvel'
        }

        # Cria os selectboxes apenas para as colunas que existem no DataFrame
        filters = {}
        for col, display_name in filter_columns.items():
            if col in gdf.columns:
                unique_values = [""] + gdf[col].dropna().unique().tolist()
                filters[col] = st.selectbox(f"Escolha {display_name}:", unique_values, key=col)

        # Adiciona o slider para a coluna 'area_hecta'
        if 'area_hecta' in gdf.columns:
            max_area = gdf['area_hecta'].max()
            area_hecta_value = st.slider(
                "Escolha a área máxima (hectares):",
                min_value=0.0, max_value=float(max_area), value=float(max_area),
                format_func=format_area
            )
            filters['area_hecta'] = area_hecta_value

        filtered_gdf = gdf.copy()
        for col, value in filters.items():
            if value and col != 'area_hecta':
                filtered_gdf = filtered_gdf[filtered_gdf[col] == value]
            elif col == 'area_hecta':
                filtered_gdf = filtered_gdf[filtered_gdf[col] <= value]

        # Criar um mapa inicial centrado em uma coordenada padrão
        m = folium.Map(location=[-24.0, -51.0], zoom_start=7)

        if any(filters.values()):
            if not filtered_gdf.empty:
                # Verificar novamente se o GeoDataFrame filtrado tem geometria válida e não nula
                filtered_gdf = filtered_gdf[filtered_gdf.geometry.is_valid & filtered_gdf.geometry.notna()]
                if not filtered_gdf.empty:
                    # Adicionar shapefile ao mapa com tooltips personalizados
                    for idx, row in filtered_gdf.iterrows():
                        area_formatted = format_area(row.get('area_hecta', 0))
                        tooltip = f"<b>{row.get('nome_proje', 'N/A')} (Assentamento)</b><br>" \
                                  f"Área: {area_formatted} hectares<br>" \
                                  f"Lotes: {row.get('capacidade', 'N/A')}<br>" \
                                  f"Famílias: {row.get('num_famili', 'N/A')}<br>" \
                                  f"Fase: {row.get('fase', 'N/A')}<br>" \
                                  f"Data de criação: {row.get('data_de_cr', 'N/A')}<br>" \
                                  f"Forma de obtenção: {row.get('forma_obte', 'N/A')}<br>" \
                                  f"Data de obtenção: {row.get('data_obten', 'N/A')}"
                        folium.GeoJson(row['geometry'],
                                       tooltip=tooltip,
                                       ).add_to(m)

        # Exibir mapa no Streamlit
        folium_static(m)
    else:
        st.error("O shapefile contém geometrias inválidas ou vazias.")
else:
    st.error("Não foi possível carregar o shapefile.")
