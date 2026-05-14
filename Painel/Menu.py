import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 12px;
        color: white;
        margin-bottom: 30px;
        text-align: center;
    }
    .main-header h1 { margin: 0; font-size: 28px; }
    .main-header p { margin: 10px 0 0 0; opacity: 0.9; font-size: 16px; }
    
    .welcome-card {
        background: white;
        padding: 30px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        text-align: center;
        margin: 20px 0;
    }
    .welcome-card h2 { color: #667eea; margin-bottom: 10px; }
    .welcome-card p { color: #666; font-size: 16px; }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown("""
<div class="main-header">
    <h1>📊 Sistema de Gestão</h1>
    <p>Selecione uma página no menu lateral para começar</p>
</div>
""", unsafe_allow_html=True)

# Conteúdo inicial
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div class="welcome-card">
        <h2>👋 Bem-vindo!</h2>
        <p>Utilize o menu lateral para navegar entre as páginas disponíveis.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    **Páginas disponíveis:**
    - 📊 **Painel de Alunos** - Visualização dos dados de matrícula
    """)