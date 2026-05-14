import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from datetime import datetime

# Configuração da página
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
    .stDownloadButton button {
        background: #4caf50 !important;
        color: white !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>📊 Painel de Alunos</h1></div>', unsafe_allow_html=True)

# ============ CARREGAR CSV DO GOOGLE DRIVE ============

@st.cache_data(ttl=180)  # Cache de 3 minutos
def carregar_csv_do_drive():
    """Baixa o arquivo CSV diretamente do Google Drive usando credencial"""
    try:
        # Autentica com a conta de serviço
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        # Conecta ao Google Drive
        service = build('drive', 'v3', credentials=credentials)
        
        # ID do arquivo CSV
        # Time BI/CSV/[BD] - P1.csv
        file_id = '1zSd2eW6KcXtIt3NT-6YtLQnsMnqC7DD6'
        
        # Baixa o arquivo
        request = service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_buffer.seek(0)
        
        # Lê o CSV
        df = pd.read_csv(file_buffer, dtype=str).fillna('')
        
        return df, None
        
    except Exception as e:
        return None, f"Erro: {str(e)}"

# ============ CARREGA DADOS ============

with st.spinner("🔄 Carregando dados do Google Drive..."):
    df, erro = carregar_csv_do_drive()

if erro:
    st.error(f"❌ {erro}")
    st.info("""
    **Verifique:**
    1. Se o arquivo foi compartilhado com: `python-agent@drive-time-bi.iam.gserviceaccount.com`
    2. Se o ID do arquivo está correto
    3. Se os Secrets estão configurados no Streamlit Cloud
    """)
    st.stop()

if df is None or df.empty:
    st.warning("⚠️ O arquivo foi carregado mas está vazio.")
    st.stop()

# ============ SIDEBAR ============

with st.sidebar:
    st.header("🔍 Filtros")
    
    busca = st.text_input("Buscar:", placeholder="Nome, RA, CPF, curso...")
    
    coluna_filtro = st.selectbox(
        "Filtrar por coluna:",
        ["Todas as colunas"] + list(df.columns)
    )
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Limpar", use_container_width=True):
            st.rerun()
    with col2:
        if st.button("🔃 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    reg_por_pagina = st.selectbox(
        "Registros por página:",
        [20, 30, 50, 100],
        index=1
    )
    
    st.divider()
    
    # Informações do arquivo
    st.caption(f"📊 Total: {len(df):,} registros")
    st.caption(f"📋 Colunas: {len(df.columns)}")
    st.caption(f"📁 Fonte: Time BI/CSV/[BD] - P1.csv")
    st.caption(f"🕒 Atualizado: {datetime.now().strftime('%H:%M:%S')}")

# ============ APLICA FILTROS ============

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

# ============ MÉTRICAS ============

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📊 Total", f"{len(df):,}")
with col2:
    st.metric("🔍 Exibindo", f"{len(df_filtrado):,}")
with col3:
    st.metric("📋 Colunas", len(df.columns))
with col4:
    st.metric("🔄 Atualização", "Automática")

st.divider()

# ============ PAGINAÇÃO ============

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

st.caption(
    f"Mostrando {inicio+1:,} a {fim:,} de {len(df_filtrado):,} registros "
    f"| Página {pagina} de {total_paginas}"
)

# ============ TABELA ============

st.dataframe(
    df_filtrado.iloc[inicio:fim],
    use_container_width=True,
    height=500,
    hide_index=True
)

# ============ DOWNLOAD ============

st.divider()

col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    csv = df_filtrado.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 Baixar CSV",
        data=csv,
        file_name=f"alunos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with col2:
    st.caption(f"🕒 Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

with col3:
    st.caption(f"📁 [BD] - P1.csv")