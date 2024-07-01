import geopandas as gpd
import pandas as pd
import folium
from streamlit_folium import folium_static
import streamlit as st
import json
from shapely.geometry import mapping  # Importar mapping corretamente
from folium.plugins import DualMap
from branca.element import Figure

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

    # Criar um mapa inicial centrado em uma coordenada padrão
    fig = Figure(width=1000, height=600)
    map_left = fig.add_subplot(1, 2, 1)
    map_right = fig.add_subplot(1, 2, 2)

    dual_map = DualMap(location=[-24.0, -51.0], zoom_start=7, tiles=None, layout=(1, 2), control_scale=True)
    m = dual_map.m1

    # Basemaps disponíveis para seleção
    basemaps = {
        "OpenStreetMap": folium.TileLayer("openstreetmap"),
        "Stamen Terrain": folium.TileLayer("stamenterrain"),
        "Stamen Toner": folium.TileLayer("stamentoner"),
        "Esri Satellite": folium.TileLayer("esrisatellite"),
        # Adicione outros basemaps conforme desejado
    }

    # Adicionar basemaps ao DualMap
    for name, tile in basemaps.items():
        tile.add_to(dual_map.m2)

    # Selecionar o basemap padrão
    selected_basemap = st.sidebar.selectbox("Escolha um mapa de fundo:", list(basemaps.keys()))
    dual_map.m2 = basemaps[selected_basemap]

    # Adicionar polígonos filtrados ao mapa com tooltips personalizados
    for idx, row in gdf.iterrows():
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
    folium_static(dual_map)

    # Função para baixar os polígonos filtrados como GeoJSON
    def download_geojson():
        selected_features = []
        for idx, row in gdf.iterrows():
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
    gdf = gdf[['uf', 'municipio', 'cd_sipra', 'nome_pa', 'lotes', 'quant_fami', 'fase', 'area_incra', 'area_polig', 'data_criac', 'forma_obte', 'data_obten']]

    # Exibir tabela com os dados filtrados
    st.write("Tabela de dados:")
    st.dataframe(gdf)

    # Função para converter DataFrame para CSV
    @st.cache
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(gdf)

    # Botão para baixar os dados filtrados como CSV
    st.download_button(
        label="Baixar dados filtrados como CSV",
        data=csv,
        file_name='dados_filtrados.csv',
        mime='text/csv',
    )
