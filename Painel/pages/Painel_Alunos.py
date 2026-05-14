import streamlit as st
import pandas as pd
from google.oauth2 import service_account
import gspread
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Painel de Alunos",
    page_icon="👨‍🎓",
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

st.markdown('<div class="main-header"><h1>👨‍🎓 Painel de Alunos</h1></div>', unsafe_allow_html=True)

# ============ CONEXÃO COM GOOGLE SHEETS ============

@st.cache_data(ttl=180)
def carregar_dados_google_sheets():
    """Carrega dados diretamente da planilha Google Sheets"""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        
        client = gspread.authorize(credentials)
        
        # Planilha principal
        planilha_id = '1BO7HtP9oa-cF7NQHsYCKYWUUswL7rvDAP0IVXDtiiMo'
        planilha = client.open_by_key(planilha_id)
        
        # Aba específica
        aba = planilha.worksheet('[BD]-Mat/PreMat2')
        dados = aba.get_all_records()
        
        if not dados:
            return None, "Planilha vazia"
        
        df = pd.DataFrame(dados).fillna('')
        
        return df, None
        
    except Exception as e:
        return None, f"Erro: {str(e)}"

# ============ CARREGA DADOS ============

with st.spinner("🔄 Carregando dados da planilha..."):
    df, erro = carregar_dados_google_sheets()

if erro:
    st.error(f"❌ {erro}")
    st.info("""
    **Verifique:**
    1. Se a planilha está compartilhada com: `python-agent@drive-time-bi.iam.gserviceaccount.com`
    2. Se o nome da aba está correto: `[BD]-Mat/PreMat2`
    3. Se os Secrets estão configurados no Streamlit Cloud
    """)
    st.stop()

if df is None or df.empty:
    st.warning("⚠️ A planilha está vazia.")
    st.stop()

# ============ INICIALIZA SESSÃO ============

if 'busca_input' not in st.session_state:
    st.session_state['busca_input'] = ""
if 'coluna_select' not in st.session_state:
    st.session_state['coluna_select'] = "Todas as colunas"
if 'pagina_input' not in st.session_state:
    st.session_state['pagina_input'] = 1
if 'reg_pagina' not in st.session_state:
    st.session_state['reg_pagina'] = 30

# ============ FUNÇÕES ============

def aplicar_filtros(df, busca, coluna):
    """Aplica filtros de busca no DataFrame"""
    if not busca or not busca.strip():
        return df.copy()
    
    termo = busca.strip().lower()
    
    if coluna != "Todas as colunas":
        mask = df[coluna].astype(str).str.lower().str.contains(termo, na=False)
        return df[mask].copy()
    else:
        mask = pd.Series(False, index=df.index)
        for col in df.columns:
            mask |= df[col].astype(str).str.lower().str.contains(termo, na=False)
        return df[mask].copy()

def mudar_pagina(delta):
    """Muda a página com segurança"""
    nova_pagina = st.session_state['pagina_input'] + delta
    
    df_temp = aplicar_filtros(df, st.session_state['busca_input'], st.session_state['coluna_select'])
    total_paginas = max(1, (len(df_temp) - 1) // st.session_state['reg_pagina'] + 1)
    
    if 1 <= nova_pagina <= total_paginas:
        st.session_state['pagina_input'] = nova_pagina

# ============ SIDEBAR ============

with st.sidebar:
    st.header("🔍 Busca")
    
    busca = st.text_input(
        "Buscar por nome, RA, CPF...",
        placeholder="Digite aqui...",
        key="busca_input",
        label_visibility="collapsed"
    )
    
    coluna_filtro = st.selectbox(
        "Filtrar por coluna:",
        ["Todas as colunas"] + list(df.columns),
        key="coluna_select"
    )
    
    st.divider()
    
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
    
    st.caption("Registros por página:")
    reg_por_pagina = st.selectbox(
        "Registros por página",
        [20, 30, 50, 100],
        index=1,
        label_visibility="collapsed",
        key="reg_pagina"
    )
    
    st.divider()
    
    # PAGINAÇÃO
    st.markdown("**📄 Página**")
    
    df_filtrado = aplicar_filtros(df, busca, coluna_filtro)
    total_paginas = max(1, (len(df_filtrado) - 1) // reg_por_pagina + 1)
    
    if st.session_state['pagina_input'] > total_paginas:
        st.session_state['pagina_input'] = total_paginas
    
    pagina = st.session_state['pagina_input']
    
    col_pag1, col_pag2, col_pag3 = st.columns([1, 2, 1])
    
    with col_pag1:
        st.button("◀", key="btn_anterior", use_container_width=True,
                 disabled=(pagina <= 1), on_click=mudar_pagina, args=(-1,))
    
    with col_pag2:
        st.number_input(
            "Página atual",
            min_value=1,
            max_value=total_paginas,
            value=pagina,
            label_visibility="collapsed",
            key="pagina_input"
        )
    
    with col_pag3:
        st.button("▶", key="btn_proximo", use_container_width=True,
                 disabled=(pagina >= total_paginas), on_click=mudar_pagina, args=(1,))
    
    st.caption(f"Página {pagina} de {total_paginas}")
    
    st.divider()
    
    # TOTAL DE ALUNOS
    st.markdown(f"""
    <div class="metric-box">
        <div class="number">{len(df):,}</div>
        <div class="label">Total de Alunos</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    st.caption(f"📁 [BD]-Mat/PreMat2")
    st.caption(f"🕒 {datetime.now().strftime('%d/%m/%Y %H:%M')}")

# ============ TABELA ============

inicio = (pagina - 1) * reg_por_pagina
fim = min(inicio + reg_por_pagina, len(df_filtrado))

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