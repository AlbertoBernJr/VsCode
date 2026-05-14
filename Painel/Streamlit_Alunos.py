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
    initial_sidebar_state="expanded"
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
    .metric-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
    }
    .metric-box .number {
        font-size: 28px;
        font-weight: 700;
        color: #667eea;
    }
    .metric-box .label {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>📊 Painel de Alunos</h1></div>', unsafe_allow_html=True)

# ============ CARREGAR CSV DO GOOGLE DRIVE ============

@st.cache_data(ttl=180)
def carregar_csv_do_drive():
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/drive.readonly']
        )
        
        service = build('drive', 'v3', credentials=credentials)
        file_id = '1zSd2eW6KcXtIt3NT-6YtLQnsMnqC7DD6'
        
        request = service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        file_buffer.seek(0)
        df = pd.read_csv(file_buffer, dtype=str).fillna('')
        
        return df, None
        
    except Exception as e:
        return None, f"Erro: {str(e)}"

# ============ CARREGA DADOS ============

with st.spinner("🔄 Carregando dados do Google Drive..."):
    df, erro = carregar_csv_do_drive()

if erro:
    st.error(f"❌ {erro}")
    st.stop()

if df is None or df.empty:
    st.warning("⚠️ O arquivo está vazio.")
    st.stop()

# ============ INICIALIZA SESSÃO ============

if 'busca_input' not in st.session_state:
    st.session_state['busca_input'] = ""
if 'coluna_select' not in st.session_state:
    st.session_state['coluna_select'] = "Todas as colunas"
if 'pagina_input' not in st.session_state:
    st.session_state['pagina_input'] = 1

# ============ SIDEBAR ============

with st.sidebar:
    st.header("🔍 Busca")
    
    # Campo de busca
    busca = st.text_input(
        "Buscar por nome, RA, CPF...",
        placeholder="Digite aqui...",
        key="busca_input",
        label_visibility="collapsed"
    )
    
    # Filtro por coluna
    coluna_filtro = st.selectbox(
        "Filtrar por coluna:",
        ["Todas as colunas"] + list(df.columns),
        key="coluna_select"
    )
    
    st.divider()
    
    # Botões
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Limpar", use_container_width=True):
            st.session_state['busca_input'] = ""
            st.session_state['coluna_select'] = "Todas as colunas"
            st.session_state['pagina_input'] = 1
            st.rerun()
    with col2:
        if st.button("🔃 Atualizar", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    # Total de alunos
    st.markdown(f"""
    <div class="metric-box">
        <div class="number">{len(df):,}</div>
        <div class="label">Total de Alunos</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Registros por página
    st.caption("Registros por página:")
    reg_por_pagina = st.selectbox(
        "Registros por página",
        [20, 30, 50, 100],
        index=1,
        label_visibility="collapsed",
        key="reg_pagina"
    )
    
    st.divider()
    
    # Paginação
    st.markdown("**📄 Página**")
    
    # Aplica filtros primeiro para calcular total de páginas
    df_filtrado = df.copy()
    if busca and busca.strip():
        termo = busca.strip().lower()
        if coluna_filtro != "Todas as colunas":
            mask = df_filtrado[coluna_filtro].astype(str).str.lower().str.contains(termo, na=False)
            df_filtrado = df_filtrado[mask]
        else:
            mask = pd.Series(False, index=df_filtrado.index)
            for col in df_filtrado.columns:
                mask |= df_filtrado[col].astype(str).str.lower().str.contains(termo, na=False)
            df_filtrado = df_filtrado[mask]
    
    total_paginas = max(1, (len(df_filtrado) - 1) // reg_por_pagina + 1)
    
    # Navegação com setas
    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    with col_pag1:
        if st.button("◀", use_container_width=True, disabled=st.session_state['pagina_input'] <= 1):
            st.session_state['pagina_input'] -= 1
            st.rerun()
    
    with col_pag2:
        pagina = st.number_input(
            "Página atual",
            min_value=1,
            max_value=total_paginas,
            value=st.session_state['pagina_input'],
            label_visibility="collapsed",
            key="pagina_input"
        )
    
    with col_pag3:
        if st.button("▶", use_container_width=True, disabled=st.session_state['pagina_input'] >= total_paginas):
            st.session_state['pagina_input'] += 1
            st.rerun()
    
    st.caption(f"Página {pagina} de {total_paginas}")
    
    st.divider()
    
    st.caption(f"📁 [BD] - P1.csv")
    st.caption(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ============ CONTEÚDO PRINCIPAL ============

# Já temos df_filtrado da sidebar
inicio = (pagina - 1) * reg_por_pagina
fim = min(inicio + reg_por_pagina, len(df_filtrado))

# ============ TABELA ============

st.dataframe(
    df_filtrado.iloc[inicio:fim],
    use_container_width=True,
    height=550,
    hide_index=True
)

# ============ RODAPÉ ============

st.divider()

col1, col2 = st.columns([1, 4])
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
    st.caption(f"Mostrando {inicio+1:,} a {fim:,} de {len(df_filtrado):,} alunos")