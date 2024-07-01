import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st
import json
from shapely.geometry import mapping  # Importar mapping corretamente
from folium.plugins import FloatImage  # Importar plugins de imagem flutuante

# Função para carregar shapefile
def load_shapefile(file_path):
    try:
        gdf = gpd.read_file(file_path)
        # Converter as colunas de área para numérica
        gdf['area_incra'] = pd.to_numeric(gdf['area_incra'], errors='coerce')
        gdf['area_polig'] = pd.to_numeric(gdf['area_polig'], errors='coerce')
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
    st.markdown("(As informações exibidas neste site são públicas e estão disponíveis no [Portal de Dados Abertos](https://dados.gov.br/dados/conjuntos-dados/sistema-de-informacoes-de-projetos-de-reforma-agraria---sipra))")
    st.write("Contato: 6dsvj@pm.me")

    # Opções de basemap com atribuições corretas
    basemaps = {
    'OpenStreetMap': folium.TileLayer('openstreetmap'),
    'Stamen Terrain': folium.TileLayer('stamenterrain', attr='Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'),
    'Stamen Toner': folium.TileLayer('stamentoner'),
    'Esri Satellite': folium.TileLayer('esrisatellite'),
    'CartoDB Positron': folium.TileLayer('cartodbpositron')
}
 
    # Selecionar o basemap no sidebar
    selected_basemap = st.sidebar.selectbox('Escolha um basemap:', list(basemaps.keys()))
    
    # Criar um mapa inicial com camada de azulejos 'Stamen Terrain'
    m = folium.Map(location=[-24.0, -51.0], zoom_start=7, tiles='Stamen Terrain')

    # Verificar se há filtros selecionados
    filters = {}

    # Lista de colunas para filtros e seus nomes de exibição
    filter_columns = {
        'uf': 'um estado',
        'municipio': 'um município',
        'nome_pa': 'um assentamento',
        'cd_sipra': 'um código SIPRA',
        'lotes': 'o total de lotes',
        'quant_fami': 'a quantidade de famílias beneficiárias',
        'fase': 'uma fase de consolidação',
        'data_criac': 'a data de criação',
        'forma_obte': 'a forma de obtenção do imóvel',
        'data_obten': 'a data de obtenção do imóvel',
        'area_incra_min': 'a área mínima (hectares) segundo dados do INCRA',
        'area_incra': 'a área máxima (hectares) segundo dados do INCRA',
        'area_polig_min': 'a área mínima (hectares) segundo polígono',
        'area_polig': 'a área máxima (hectares) segundo polígono'
    }

    # Opções para seleção de lotes, famílias beneficiárias e áreas
    options_lotes = [10, 50, 100, 300, 500, 800, 1200, 2000, 5000, 10000, 15000, 20000]
    options_familias = options_lotes  # Usando as mesmas opções de lotes para famílias beneficiárias
    options_area_incra = [500, 1000, 5000, 10000, 30000, 50000, 100000, 200000, 400000, 600000]

    # Definir Paraná como o estado inicialmente selecionado
    selected_state = 'PARANÁ'

    # Cria os selectboxes apenas para as colunas que existem no DataFrame
    for col, display_name in filter_columns.items():
        if col in gdf.columns or col in ['area_incra_min', 'area_polig_min']:
            if col == 'uf':
                options = [''] + sorted(gdf[col].dropna().unique().tolist())
                default_index = options.index(selected_state) if selected_state in options else 0
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options, index=default_index)
            elif col in ['lotes', 'quant_fami']:
                options = [None] + sorted(options_lotes)
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options, format_func=lambda x: 'Nenhum' if x is None else str(x))
            elif col in ['area_incra', 'area_incra_min', 'area_polig', 'area_polig_min']:
                options = [None] + sorted(options_area_incra)
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", options, format_func=lambda x: 'Nenhum' if x is None else str(x))
            elif col == 'data_criac':
                filters[col] = st.sidebar.date_input(f"Escolha {display_name}:", min_value=pd.to_datetime("1970-01-01"), max_value=pd.to_datetime("2034-12-31"))
            else:
                unique_values = [""] + sorted(gdf[col].dropna().unique().tolist())
                filters[col] = st.sidebar.selectbox(f"Escolha {display_name}:", unique_values, format_func=lambda x: 'Nenhum' if x == "" else str(x))

    filtered_gdf = gdf.copy()
    for col, value in filters.items():
        if value is not None and value != "":
            if col == 'area_incra':
                filtered_gdf = filtered_gdf[filtered_gdf['area_incra'] <= value]
            elif col == 'area_incra_min':
                filtered_gdf = filtered_gdf[filtered_gdf['area_incra'] >= value]
            elif col == 'area_polig':
                filtered_gdf = filtered_gdf[filtered_gdf['area_polig'] <= value]
            elif col == 'area_polig_min':
                filtered_gdf = filtered_gdf[filtered_gdf['area_polig'] >= value]
            elif col == 'lotes':
                filtered_gdf = filtered_gdf[filtered_gdf['lotes'] <= value]
            elif col == 'quant_fami':
                filtered_gdf = filtered_gdf[filtered_gdf['quant_fami'] <= value]
            elif col == 'data_criac':
                filtered_gdf = filtered_gdf[pd.to_datetime(filtered_gdf['data_criac'], errors='coerce') <= pd.to_datetime(value)]
            else:
                filtered_gdf = filtered_gdf[filtered_gdf[col] == value]

    # Adicionar polígonos filtrados ao mapa com tooltips personalizados
    for idx, row in filtered_gdf.iterrows():
        area_formatted = format_area(row.get('area_incra', 0))
        area_polig_formatted = format_area(row.get('area_polig', 0))
        tooltip = f"<b>{row.get('nome_pa', 'N/A')} (Assentamento)</b><br>" \
                  f"Área: {area_formatted} hectares<br>" \
                  f"Área (segundo polígono): {area_polig_formatted} hectares<br>" \
                  f"Lotes: {row.get('lotes', 'N/A')}<br>" \
                  f"Famílias: {row.get('quant_fami', 'N/A')}<br>" \
                  f"Fase: {row.get('fase', 'N/A')}<br>" \
                  f"Data de criação: {row.get('data_criac', 'N/A')}<br>" \
                  f"Forma de obtenção: {row.get('forma_obte', 'N/A')}<br>" \
                  f"Data de obtenção: {row.get('data_obten', 'N/A')}"
        folium.GeoJson(row['geometry'],
                       tooltip=tooltip,
                       ).add_to(m)

    # Exibir mapa no Streamlit novamente para refletir as mudanças
    folium_static(m)

    # Função para baixar os polígonos filtrados como GeoJSON
    def download_geojson():
        selected_features = []
        for idx, row in filtered_gdf.iterrows():
            geom = row['geometry']
            feature = {
                'type': 'Feature',
                'geometry': mapping(geom),
                'properties': {
                    'nome_pa': row.get('nome_pa', 'N/A'),
                    'area_incra': row.get('area_incra', 'N/A'),
                    'area_polig': row.get('area_polig', 'N/A'),
                    'lotes': row.get('lotes', 'N/A'),
                    'quant_fami': row.get('quant_fami', 'N/A'),
                    'fase': row.get('fase', 'N/A'),
                    'data_criac': row.get('data_criac', 'N/A'),
                    'forma_obte': row.get('forma_obte', 'N/A'),
                    'data_obten': row.get('data_obten', 'N/A')
                }
            }
            selected_features.append(feature)

        feature_collection = {
            'type': 'FeatureCollection',
            'features': selected_features
        }

        return json.dumps(feature_collection)

    geojson = download_geojson()

    st.markdown(f"### Baixar polígonos selecionados como GeoJSON")
    st.markdown("Clique abaixo para baixar um arquivo GeoJSON contendo os polígonos dos assentamentos selecionados.")

    st.download_button(
        label="Baixar GeoJSON dos polígonos selecionados",
        data=geojson,
        file_name='poligonos_selecionados.geojson',
        mime='application/json',
    )

    # Reordenar as colunas conforme especificado
    filtered_gdf = filtered_gdf[['uf', 'municipio', 'cd_sipra', 'nome_pa', 'lotes', 'quant_fami', 'fase', 'area_incra', 'area_polig', 'data_criac', 'forma_obte', 'data_obten']]

    # Exibir tabela com os dados filtrados
    st.write("Tabela de dados:")
    st.dataframe(filtered_gdf)

    # Função para converter DataFrame para CSV
    @st.cache
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(filtered_gdf)

    # Botão para baixar os dados filtrados como CSV
    st.download_button(
        label="Baixar dados filtrados como CSV",
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv',
    )
