import streamlit as st
import pandas as pd
import gspread
from google.oauth2 import service_account
from datetime import datetime

# Configuração da página - PRIMEIRO comando Streamlit
st.set_page_config(
    page_title="Painel de Alunos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .main-header h1 { margin: 0; font-size: 24px; }
    div[data-testid="stDataFrame"] th {
        background: #667eea !important;
        color: white !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<div class="main-header"><h1>📊 Painel de Alunos</h1></div>', unsafe_allow_html=True)

# ============ FUNÇÕES ============

@st.cache_data(ttl=300)
def conectar_google_sheets():
    """Conecta ao Google Sheets usando secrets do Streamlit Cloud"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        st.error(f"Erro na conexão: {str(e)}")
        return None

# ============ SIDEBAR ============

with st.sidebar:
    st.header("📁 Selecionar Arquivo")
    
    arquivo = st.file_uploader(
        "Escolha um arquivo CSV",
        type=['csv'],
        help="Selecione o arquivo CSV que deseja visualizar"
    )
    
    if arquivo is not None:
        try:
            df = pd.read_csv(arquivo, dtype=str).fillna('')
            st.session_state['df'] = df
            st.session_state['arquivo_nome'] = arquivo.name
            st.success(f"✅ {len(df):,} registros")
            st.caption(f"📋 {len(df.columns)} colunas")
            st.caption(f"📁 {arquivo.name}")
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")
    else:
        st.info("👆 Selecione um arquivo CSV")
    
    st.divider()
    
    if 'df' in st.session_state and not st.session_state['df'].empty:
        st.header("🔍 Filtros")
        busca = st.text_input("Buscar:", placeholder="Nome, RA, CPF...", key="busca")
        coluna_filtro = st.selectbox(
            "Filtrar por coluna:",
            ["Todas as colunas"] + list(st.session_state['df'].columns),
            key="coluna"
        )
        if st.button("🔄 Limpar", use_container_width=True):
            st.session_state['busca'] = ""
            st.session_state['coluna'] = "Todas as colunas"
            st.rerun()
        
        st.divider()
        reg_por_pagina = st.selectbox("Registros por página:", [20, 30, 50, 100], index=1)

# ============ CONTEÚDO PRINCIPAL ============

if 'df' not in st.session_state or st.session_state['df'].empty:
    st.info("👈 Selecione um arquivo CSV na barra lateral para visualizar os dados.")
    st.stop()

df = st.session_state['df']
busca = st.session_state.get('busca', '')
coluna_filtro = st.session_state.get('coluna', 'Todas as colunas')
reg_por_pagina = st.session_state.get('reg_por_pagina', 30)

# Aplica filtros
df_filtrado = df.copy()

if busca:
    if coluna_filtro != "Todas as colunas":
        mask = df_filtrado[coluna_filtro].astype(str).str.lower().str.contains(busca.lower(), na=False)
        df_filtrado = df_filtrado[mask]
    else:
        mask = df_filtrado.apply(
            lambda row: row.astype(str).str.lower().str.contains(busca.lower(), na=False).any(), axis=1
        )
        df_filtrado = df_filtrado[mask]

# Métricas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📊 Total", f"{len(df):,}")
with col2:
    st.metric("🔍 Exibindo", f"{len(df_filtrado):,}")
with col3:
    st.metric("📋 Colunas", len(df.columns))
with col4:
    st.metric("📁 Arquivo", st.session_state.get('arquivo_nome', 'N/A'))

st.divider()

# Paginação
total_paginas = max(1, (len(df_filtrado) - 1) // reg_por_pagina + 1)
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    pagina = st.number_input("Página", min_value=1, max_value=total_paginas, value=1, label_visibility="collapsed")

inicio = (pagina - 1) * reg_por_pagina
fim = min(inicio + reg_por_pagina, len(df_filtrado))
st.caption(f"Mostrando {inicio+1:,} a {fim:,} de {len(df_filtrado):,} | Página {pagina} de {total_paginas}")

# Tabela
st.dataframe(df_filtrado.iloc[inicio:fim], use_container_width=True, height=500, hide_index=True)

# Download
st.divider()
col1, col2 = st.columns([1, 4])
with col1:
    csv = df_filtrado.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 Baixar CSV", csv, f"alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
with col2:
    st.caption(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")