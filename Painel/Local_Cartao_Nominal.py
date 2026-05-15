import streamlit as st
import subprocess
import os
import platform

# Configuração da página
st.set_page_config(
    page_title="Executáveis Locais",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚙️ Ativar Scripts Locais")

st.markdown("""
Esta página permite executar aplicativos que estão no seu computador local ou na máquina virtual.

**⚠️ Importante:** O executável será aberto no seu computador, não no navegador.
""")

# ============ OPÇÕES DE EXECUTÁVEIS ============

st.divider()
st.subheader("🖥️ Selecione o executável:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🪪 Gerador de Cartões
    
    **Caminho:** `C:\\Users\\alberto.bernardo\\Desktop\\GeradorCartoes_Matriz.exe`
    
    **Descrição:** Gera cartões-resposta a partir da planilha de alunos.
    
    **Local:** Computador Local
    """)
    
    if st.button("🚀 Abrir Gerador de Cartões (Local)", use_container_width=True, type="primary"):
        caminho = r"C:\Users\alberto.bernardo\Desktop\GeradorCartoes_Matriz.exe"
        
        if os.path.exists(caminho):
            try:
                subprocess.Popen([caminho])
                st.success(f"✅ Executável aberto com sucesso!")
                st.info("Verifique a barra de tarefas do Windows - o aplicativo foi iniciado.")
            except Exception as e:
                st.error(f"❌ Erro ao abrir: {str(e)}")
        else:
            st.error(f"❌ Arquivo não encontrado em:\n`{caminho}`")

with col2:
    st.markdown("""
    ### 📁 Navegador de Cartões
    
    **Caminho:** `C:\\BI_Compartilhado\\Automacoes\\Cartao_Nominal_Atualizado\\dist`
    
    **Descrição:** Pasta com os executáveis do sistema de cartões.
    
    **Local:** Máquina Virtual
    """)
    
    if st.button("📂 Abrir Pasta (VM)", use_container_width=True, type="primary"):
        caminho = r"C:\BI_Compartilhado\Automacoes\Cartao_Nominal_Atualizado\dist"
        
        if os.path.exists(caminho):
            try:
                os.startfile(caminho)
                st.success(f"✅ Pasta aberta no Windows Explorer!")
            except Exception as e:
                st.error(f"❌ Erro ao abrir: {str(e)}")
        else:
            st.error(f"❌ Pasta não encontrada em:\n`{caminho}`")

# ============ CAMINHO PERSONALIZADO ============

st.divider()
st.subheader("🔧 Caminho Personalizado")

caminho_personalizado = st.text_input(
    "Digite o caminho completo do executável (.exe) ou pasta:",
    placeholder="Ex: C:\\Users\\seu_usuario\\Desktop\\meu_app.exe"
)

col1, col2 = st.columns(2)

with col1:
    if st.button("🚀 Executar", use_container_width=True):
        if caminho_personalizado:
            if os.path.exists(caminho_personalizado):
                try:
                    if caminho_personalizado.lower().endswith('.exe'):
                        subprocess.Popen([caminho_personalizado])
                        st.success("✅ Executável iniciado!")
                    else:
                        os.startfile(caminho_personalizado)
                        st.success("✅ Pasta aberta!")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
            else:
                st.error("❌ Caminho não encontrado!")
        else:
            st.warning("⚠️ Digite um caminho primeiro.")

with col2:
    if st.button("📂 Abrir Pasta", use_container_width=True):
        if caminho_personalizado:
            if os.path.exists(caminho_personalizado):
                try:
                    os.startfile(caminho_personalizado)
                    st.success("✅ Pasta aberta!")
                except Exception as e:
                    st.error(f"❌ Erro: {str(e)}")
            else:
                st.error("❌ Caminho não encontrado!")
        else:
            st.warning("⚠️ Digite um caminho primeiro.")

# ============ INFORMAÇÕES DO SISTEMA ============

st.divider()
st.subheader("💻 Informações do Sistema")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Sistema", platform.system())
with col2:
    st.metric("Computador", platform.node())
with col3:
    st.metric("Usuário", os.getlogin())

st.caption("⚠️ Esta página só funciona quando o Streamlit está rodando localmente (não no Streamlit Cloud).")