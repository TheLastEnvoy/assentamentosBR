import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st

# Função para carregar shapefile
def load_shapefile(file_path):
    try:
        gdf = gpd.read_file(file_path)
        # Converter as colunas de área para numérica
        gdf['area_hecta'] = pd.to_numeric(gdf['area_hecta'], errors='coerce')
        gdf['area2'] = pd.to_numeric(gdf['area2'], errors='coerce')
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
        'uf': 'um estado',
        'municipio': 'um município',
        'nome_proje': 'um assentamento',
        'cd_sipra': 'um código SIPRA',
        'capacidade': 'o total de lotes',
        'num_famili': 'a quantidade de famílias beneficiárias',
        'fase': 'uma fase de consolidação',
        'data_de_cr': 'a data de criação',
        'forma_obte': 'a forma de obtenção do imóvel',
        'data_obten': 'a data de obtenção do imóvel',
        'area_hecta_min': 'a área mínima (hectares) segundo dados do INCRA',
        'area_hecta': 'a área máxima (hectares) segundo dados do INCRA',
        'area2_min': 'a área mínima (hectares) segundo polígono',
        'area2': 'a área máxima (hectares) segundo polígono'
    }

    # Opções para seleção de lotes, famílias beneficiárias e áreas
    options_lotes = [10, 50, 100, 300, 500, 800, 1200, 2000, 5000, 10000, 15000, 20000]
    options_familias = options_lotes  # Usando as mesmas opções de lotes para famílias beneficiárias
    options_area_hecta = [500, 1000, 5000, 10000, 30000, 50000, 100000, 200000, 400000, 600000]

    # Definir Paraná como o estado inicialmente selecionado
    selected_state = 'PARANÁ'

    # Cria os selectboxes apenas para as colunas que existem no DataFrame
    for col, display_name in filter_columns.items():
        if col in gdf.columns or col in ['area_hecta_min', 'area2_min']:
            if col == 'uf':
                options = [''] + sorted(gdf[col].dropna().unique().tolist())
                default_index = options.index(selected_state) if selected_state in options else 0
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options, index=default_index)
            elif col in ['capacidade', 'num_famili']:
                options = [None] + sorted(options_lotes)
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options, format_func=lambda x: 'Nenhum' if x is None else str(x))
            elif col in ['area_hecta', 'area_hecta_min', 'area2', 'area2_min']:
                options = [None] + sorted(options_area_hecta)
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options, format_func=lambda x: 'Nenhum' if x is None else str(x))
            elif col == 'data_de_cr':
                filters[col] = st.sidebar.date_input(f"Escolha {display_name}:", min_value=pd.to_datetime("1970-01-01"), max_value=pd.to_datetime("2034-12-31"))
            else:
                unique_values = [""] + sorted(gdf[col].dropna().unique().tolist())
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", unique_values, format_func=lambda x: 'Nenhum' if x == "" else str(x))

    filtered_gdf = gdf.copy()
    for col, value in filters.items():
        if value is not None and value != "":
            if col == 'area_hecta':
                filtered_gdf = filtered_gdf[filtered_gdf['area_hecta'] <= value]
            elif col == 'area_hecta_min':
                filtered_gdf = filtered_gdf[filtered_gdf['area_hecta'] >= value]
            elif col == 'area2':
                filtered_gdf = filtered_gdf[filtered_gdf['area2'] <= value]
            elif col == 'area2_min':
                filtered_gdf = filtered_gdf[filtered_gdf['area2'] >= value]
            elif col == 'capacidade':
                filtered_gdf = filtered_gdf[filtered_gdf['capacidade'] <= value]
            elif col == 'num_famili':
                filtered_gdf = filtered_gdf[filtered_gdf['num_famili'] <= value]
            elif col == 'data_de_cr':
                filtered_gdf = filtered_gdf[pd.to_datetime(filtered_gdf['data_de_cr'], errors='coerce') <= pd.to_datetime(value)]
            else:
                filtered_gdf = filtered_gdf[filtered_gdf[col] == value]

    # Adicionar polígonos filtrados ao mapa com tooltips personalizados
    for idx, row in filtered_gdf.iterrows():
        area_formatted = format_area(row.get('area_hecta', 0))
        area2_formatted = format_area(row.get('area2', 0))
        tooltip = f"<b>{row.get('nome_proje', 'N/A')} (Assentamento)</b><br>" \
                  f"Área: {area_formatted} hectares<br>" \
                  f"Área (segundo polígono): {area2_formatted} hectares<br>" \
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

    # Exibir tabela com os dados filtrados
    st.write("Tabela de dados filtrados:")
    st.dataframe(filtered_gdf.drop(columns='geometry'))

    # Função para converter DataFrame para CSV
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(filtered_gdf.drop(columns='geometry'))

    # Botão para baixar os dados filtrados como CSV
    st.download_button(
        label="Baixar dados filtrados como CSV",
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv',
    )

else:
    st.error("Não foi possível carregar o shapefile.")
