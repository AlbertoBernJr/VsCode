import streamlit as st
import requests
import os

# Configuração da página
st.set_page_config(
    page_title="Cartão Nominal - Download",
    page_icon="🪪",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🪪 Gerador de Cartões Nominais")

st.markdown("""
### Download do Aplicativo

Baixe o executável do Gerador de Cartões Nominais para o seu computador.

📁 **Local do arquivo:** Google Drive
""")

st.divider()

# ============ ID DO ARQUIVO NO GOOGLE DRIVE ============

FILE_ID = "1O1pW-2Gt5oQ0nO-PyWu_HB1ZwPg0nmit"
DOWNLOAD_URL = f"https://drive.google.com/uc?id={FILE_ID}&export=download"

# ============ BOTÃO DE DOWNLOAD ============

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("""
    ### 🪪 GeradorCartoes_Matriz.exe
    
    **Descrição:** Aplicativo para geração de cartões-resposta dos alunos.
    
    **Plataforma:** Windows
    """)
    
    # Tenta fazer o download
    try:
        response = requests.get(DOWNLOAD_URL, allow_redirects=True, timeout=10)
        
        if response.status_code == 200:
            st.download_button(
                label="📥 Baixar Gerador de Cartões",
                data=response.content,
                file_name="GeradorCartoes_Matriz.exe",
                mime="application/x-msdownload",
                use_container_width=True,
                type="primary"
            )
            st.success("✅ Arquivo pronto para download!")
        else:
            st.error(f"❌ Erro ao acessar o arquivo. Status: {response.status_code}")
    except Exception as e:
        st.error(f"❌ Erro de conexão: {str(e)}")
        st.info("""
        **Alternativa:** Acesse o link direto:
        [Abrir no Google Drive](https://drive.google.com/file/d/1O1pW-2Gt5oQ0nO-PyWu_HB1ZwPg0nmit/view)
        """)

st.divider()

# ============ INSTRUÇÕES ============

st.markdown("""
### 📝 Como usar:

1. Clique no botão **"Baixar Gerador de Cartões"**
2. Salve o arquivo no seu computador
3. Execute `GeradorCartoes_Matriz.exe`
4. Siga as instruções do aplicativo

### ⚙️ Requisitos:

- Windows 10 ou superior
- Microsoft Excel instalado (para atualização da base)
- 50 MB de espaço livre

### 🔗 Link direto:

[Copiar link do Google Drive](https://drive.google.com/file/d/1O1pW-2Gt5oQ0nO-PyWu_HB1ZwPg0nmit/view)
""")

st.caption("🕒 Última atualização do executável: verifique no Google Drive")