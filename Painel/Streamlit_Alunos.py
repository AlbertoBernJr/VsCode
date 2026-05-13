import streamlit as st
import pandas as pd
from datetime import datetime

credentials = service_account.Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

client = gspread.authorize(credentials)

# Configuração da página
st.set_page_config(
    page_title="Painel de Alunos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
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
    
    .stDownloadButton button {
        background: #4caf50 !important;
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Título
st.markdown('<div class="main-header"><h1>📊 Painel de Alunos</h1></div>', unsafe_allow_html=True)

# Sidebar - Upload do arquivo
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
            st.error(f"❌ Erro ao ler arquivo: {str(e)}")
    else:
        st.info("👆 Selecione um arquivo CSV para começar")
    
    st.divider()
    
    # Filtros (só aparecem se dados carregados)
    if 'df' in st.session_state and not st.session_state['df'].empty:
        st.header("🔍 Filtros")
        
        busca = st.text_input(
            "Buscar:",
            placeholder="Digite nome, RA, CPF...",
            key="busca_input"
        )
        
        coluna_filtro = st.selectbox(
            "Filtrar por coluna:",
            ["Todas as colunas"] + list(st.session_state['df'].columns),
            key="coluna_select"
        )
        
        if st.button("🔄 Limpar Filtros", use_container_width=True):
            st.session_state['busca_input'] = ""
            st.session_state['coluna_select'] = "Todas as colunas"
            st.rerun()
        
        st.divider()
        
        reg_por_pagina = st.selectbox(
            "Registros por página:",
            [20, 30, 50, 100],
            index=1
        )
        st.session_state['reg_por_pagina'] = reg_por_pagina

# Conteúdo principal
if 'df' not in st.session_state or st.session_state['df'].empty:
    st.info("👈 Selecione um arquivo CSV na barra lateral para visualizar os dados.")
    
    # Mostra instruções
    st.markdown("""
    ### 📋 Como usar:
    1. Clique em **"Browse files"** na barra lateral
    2. Selecione o arquivo CSV (ex: `[BD] - P1.csv`)
    3. Use a busca e filtros para encontrar dados
    """)
    
    st.stop()

# Pega dados da sessão
df = st.session_state['df']
busca = st.session_state.get('busca_input', '')
coluna_filtro = st.session_state.get('coluna_select', 'Todas as colunas')
reg_por_pagina = st.session_state.get('reg_por_pagina', 30)

# Aplica filtros
df_filtrado = df.copy()

if busca:
    if coluna_filtro != "Todas as colunas":
        mask = df_filtrado[coluna_filtro].astype(str).str.lower().str.contains(busca.lower(), na=False)
        df_filtrado = df_filtrado[mask]
    else:
        mask = df_filtrado.apply(
            lambda row: row.astype(str).str.lower().str.contains(busca.lower(), na=False).any(), 
            axis=1
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

col_pag1, col_pag2, col_pag3 = st.columns([1, 3, 1])
with col_pag2:
    pagina = st.number_input(
        "Página",
        min_value=1,
        max_value=total_paginas,
        value=1,
        label_visibility="collapsed"
    )

inicio = (pagina - 1) * reg_por_pagina
fim = min(inicio + reg_por_pagina, len(df_filtrado))

st.caption(f"Mostrando {inicio+1:,} a {fim:,} de {len(df_filtrado):,} registros | Página {pagina} de {total_paginas}")

# Tabela
df_pagina = df_filtrado.iloc[inicio:fim]

st.dataframe(
    df_pagina,
    use_container_width=True,
    height=500,
    hide_index=True
)

# Download
st.divider()
col_down1, col_down2 = st.columns([1, 4])

with col_down1:
    csv = df_filtrado.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Baixar CSV",
        data=csv,
        file_name=f"alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_down2:
    st.caption(f"🕒 Atualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")