import streamlit as st
import subprocess
import os

# Configuração da página
st.set_page_config(
    page_title="Cartão Nominal - Local",
    page_icon="🪪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🪪 Gerador de Cartões Nominais")

st.markdown("""
### Aplicativo Local

Clique no botão abaixo para abrir o Gerador de Cartões Nominais no seu computador.

⚠️ O aplicativo será aberto fora do navegador.
""")

st.divider()

# ============ CAMINHO DO EXECUTÁVEL ============

caminho_executavel = r"C:\Users\alberto.bernardo\Desktop\GeradorCartoes_Matriz.exe"

# Verifica se o arquivo existe
arquivo_existe = os.path.exists(caminho_executavel)

# Exibe informações
col1, col2 = st.columns([1, 3])

with col1:
    if arquivo_existe:
        st.success("✅ Disponível")
    else:
        st.error("❌ Não encontrado")

with col2:
    st.code(caminho_executavel, language="text")

st.divider()

# ============ BOTÃO PARA EXECUTAR ============

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    if st.button("🚀 Abrir Gerador de Cartões", use_container_width=True, type="primary"):
        if arquivo_existe:
            try:
                subprocess.Popen([caminho_executavel])
                st.success("✅ Aplicativo iniciado com sucesso!")
                st.info("Verifique a barra de tarefas do Windows.")
            except Exception as e:
                st.error(f"❌ Erro ao abrir: {str(e)}")
        else:
            st.error(f"""
            ❌ Arquivo não encontrado!
            
            **Caminho procurado:**
            `{caminho_executavel}`
            
            **Verifique se:**
            - O arquivo está na pasta correta
            - O nome do arquivo está correto
            - O computador está acessível
            """)

# ============ INFORMAÇÕES ============

st.divider()
st.caption("""
📝 **Observações:**
- Este botão só funciona quando o Streamlit está rodando localmente (`localhost`)
- No Streamlit Cloud, o botão não terá efeito
- O aplicativo abre em uma janela separada do Windows
""")