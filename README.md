🗺️ MapaAssentamentos

<https://reformaagrariabr.streamlit.app/>

Visualização interativa dos projetos de assentamento de reforma agrária no Brasil
✨ Funcionalidades

    🌎 Mapa interativo com visualização geoespacial dos assentamentos
    🔍 Filtros avançados por:
        Estado e município
        Nome e código SIPRA
        Quantidade de lotes e famílias
        Fase de consolidação
        Área (INCRA e polígono)
        Data de criação e obtenção
        Forma de obtenção do imóvel
    📊 Visualização em tabela dos dados filtrados
    💾 Exportação de dados em formatos GeoJSON e CSV
    🔄 Atualização automática do mapa conforme filtros aplicados

📋 Requisitos
Text Only

streamlit>=1.0.0
geopandas>=0.9.0
folium>=0.12.0
pandas>=1.3.0
streamlit-folium>=0.6.0
shapely>=1.7.0

🚀 Instalação

    Clone este repositório:

Bash

git clone https://github.com/seu-usuario/mapa-assentamentos.git
cd mapa-assentamentos

Instale as dependências:
Bash

pip install -r requirements.txt

Baixe o arquivo de dados:

    O arquivo pasbr_geo.geojson deve estar na raiz do projeto
    Você pode baixá-lo do Portal de Dados Abertos

Execute a aplicação:

    Bash

    streamlit run app.py

🖥️ Como usar

    Acesse a aplicação no navegador (geralmente em http://localhost:8501)
    Use o painel lateral para aplicar filtros:
        Selecione um estado (pré-configurado para iniciar com Paraná)
        Refine por município, área, lotes, ou outros critérios
    Explore o mapa interativo que exibe os assentamentos filtrados
    Passe o mouse sobre os polígonos para ver informações detalhadas
    Consulte a tabela de dados abaixo do mapa
    Baixe os dados filtrados em formato GeoJSON ou CSV com os botões disponíveis

📊 Sobre os dados

Os dados exibidos são provenientes do Sistema de Informações de Projetos de Reforma Agrária (SIPRA) e estão disponíveis publicamente no Portal de Dados Abertos.

Principais campos disponíveis:

    Nome do projeto de assentamento
    Localização (UF e município)
    Código SIPRA
    Área oficial (INCRA) e área do polígono geométrico
    Número de lotes e famílias assentadas
    Fase de consolidação
    Datas de criação e obtenção
    Forma de obtenção do imóvel

🤝 Como contribuir

Contribuições são bem-vindas! Siga estes passos:

    Faça um fork do projeto
    Crie uma branch para sua feature (git checkout -b feature/nova-funcionalidade)
    Faça commit das mudanças (git commit -m 'Adiciona nova funcionalidade')
    Envie para o GitHub (git push origin feature/nova-funcionalidade)
    Abra um Pull Request

📧 Contato

6dsvjr@pm.me

Os dados usados estão todos disponíveis publicamente, como indicado em link no próprio dashboard.
