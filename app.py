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
    
    st.title("Mapa interativo com os projetos de assentamento de reforma agrária no Brasil")
    st.write("(As informações exibidas neste site são públicas)")

    # Criar um mapa inicial centrado em uma coordenada padrão
    m = folium.Map(location=[-24.0, -51.0], zoom_start=7)

    # Verificar se há filtros selecionados
    filters = {}

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
        'data_obten': 'Data de obtenção do imóvel',
        'area_hecta': 'Área máxima (hectares)'
    }

    # Opções para seleção de lotes, famílias beneficiárias e área máxima
    options_lotes = [None, 10, 50, 100, 300, 500, 800, 1200, 2000, 5000, 10000, 15000]
    options_familias = options_lotes  # Usando as mesmas opções de lotes para famílias beneficiárias
    options_area_hecta = [None, 500, 1000, 5000, 10000, 30000, 50000, 100000, 200000]

    # Definir Paraná como o estado inicialmente selecionado
    selected_state = 'PARANÁ'

    # Cria os selectboxes apenas para as colunas que existem no DataFrame
    for col, display_name in filter_columns.items():
        if col in gdf.columns:
            if col == 'uf':
                options = [''] + gdf[col].dropna().unique().tolist()
                default_index = options.index(selected_state) if selected_state in options else 0
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options, index=default_index)
            elif col in ['capacidade', 'num_famili']:
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options_lotes, format_func=lambda x: 'Nenhum' if x is None else str(x))
            elif col == 'area_hecta':
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options_area_hecta, format_func=lambda x: 'Nenhum' if x is None else str(x))
            else:
                unique_values = [""] + gdf[col].dropna().unique().tolist()
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", unique_values, format_func=lambda x: 'Nenhum' if x == "" else str(x))

    filtered_gdf = gdf.copy()
    for col, value in filters.items():
        if value is not None and value != "":
            if col == 'area_hecta':
                filtered_gdf = filtered_gdf[filtered_gdf['area_hecta'] <= value]
            elif col == 'capacidade' or col == 'num_famili':
                filtered_gdf = filtered_gdf[filtered_gdf[col] == value]
            elif col == 'uf' and value != "":
                filtered_gdf = filtered_gdf[filtered_gdf[col] == value]

    # Adicionar polígonos filtrados ao mapa com tooltips personalizados
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

    # Exibir mapa no Streamlit novamente para refletir as mudanças
    folium_static(m)

else:
    st.error("Não foi possível carregar o shapefile.")
