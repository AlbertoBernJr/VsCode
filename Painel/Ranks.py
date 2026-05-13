"""
Gerador de Ranks - Google Sheets
Compatível com Python 3.8+
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import gspread
from google.oauth2 import service_account
import pandas as pd
import os
import threading
import ssl

# Desativa SSL para redes corporativas
ssl._create_default_https_context = ssl._create_unverified_context
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Configuração do tema
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Caminho da credencial
CAMINHO_CREDENCIAL = "../credential.json"

class GeradorRanks:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Gerador de Ranks")
        self.root.geometry("800x650")
        
        # Centralizar janela
        self.root.update_idletasks()
        w = 800
        h = 650
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
        
        # Variáveis
        self.planilha_destino_id = None
        self.planilha_origem_id = None
        self.dia_selecionado = None
        self.gabarito_texto = ""
        
        # Cliente Google Sheets
        self.client = None
        self.inicializar_google()
        
        # Criar interface
        self.criar_interface()
    
    def inicializar_google(self):
        """Inicializa conexão com Google Sheets"""
        try:
            if not os.path.exists(CAMINHO_CREDENCIAL):
                messagebox.showerror("Erro", f"Arquivo de credenciais nao encontrado:\n{CAMINHO_CREDENCIAL}")
                return
            
            credentials = service_account.Credentials.from_service_account_file(
                CAMINHO_CREDENCIAL,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.client = gspread.authorize(credentials)
            self.lbl_status.configure(text="Conectado ao Google Sheets", text_color='green')
        except Exception as e:
            self.lbl_status.configure(text=f"Erro na conexao: {str(e)[:50]}", text_color='red')
    
    def criar_interface(self):
        # ===== TÍTULO =====
        titulo = ctk.CTkFrame(self.root, fg_color='#667eea', corner_radius=10)
        titulo.pack(fill='x', padx=15, pady=(15, 10))
        
        ctk.CTkLabel(titulo, text="Gerador de Ranks", 
                     font=ctk.CTkFont(size=22, weight='bold'),
                     text_color='white').pack(pady=15)
        
        # ===== CONTEÚDO PRINCIPAL =====
        main_frame = ctk.CTkFrame(self.root, fg_color='transparent')
        main_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        # ----- PLANILHA DE DESTINO -----
        frame_destino = ctk.CTkFrame(main_frame)
        frame_destino.pack(fill='x', pady=5)
        
        ctk.CTkLabel(frame_destino, text="Planilha de Destino (onde estao as abas RESPOSTA e Gabarito):",
                     font=ctk.CTkFont(size=12, weight='bold')).pack(anchor='w', padx=15, pady=(10, 5))
        
        row_destino = ctk.CTkFrame(frame_destino, fg_color='transparent')
        row_destino.pack(fill='x', padx=15, pady=5)
        
        self.entrada_destino = ctk.CTkEntry(row_destino, placeholder_text="ID da planilha ou URL...", height=35)
        self.entrada_destino.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ctk.CTkButton(row_destino, text="Selecionar", command=self.selecionar_destino,
                      width=100, height=35, fg_color='#667eea').pack(side='right')
        
        self.lbl_destino = ctk.CTkLabel(frame_destino, text="Nenhuma planilha selecionada", 
                                         text_color='gray', font=ctk.CTkFont(size=10))
        self.lbl_destino.pack(anchor='w', padx=15, pady=(0, 10))
        
        # ----- DIA -----
        frame_dia = ctk.CTkFrame(main_frame)
        frame_dia.pack(fill='x', pady=5)
        
        ctk.CTkLabel(frame_dia, text="Selecione o Dia:",
                     font=ctk.CTkFont(size=12, weight='bold')).pack(anchor='w', padx=15, pady=(10, 5))
        
        row_dia = ctk.CTkFrame(frame_dia, fg_color='transparent')
        row_dia.pack(fill='x', padx=15, pady=5)
        
        self.btn_dia1 = ctk.CTkButton(row_dia, text="1 DIA", command=lambda: self.selecionar_dia(1),
                                       width=150, height=40, fg_color='#2196F3',
                                       font=ctk.CTkFont(size=14, weight='bold'))
        self.btn_dia1.pack(side='left', padx=(0, 10))
        
        self.btn_dia2 = ctk.CTkButton(row_dia, text="2 DIA", command=lambda: self.selecionar_dia(2),
                                       width=150, height=40, fg_color='#9E9E9E',
                                       font=ctk.CTkFont(size=14, weight='bold'))
        self.btn_dia2.pack(side='left')
        
        self.lbl_dia = ctk.CTkLabel(frame_dia, text="Nenhum dia selecionado",
                                     text_color='gray', font=ctk.CTkFont(size=10))
        self.lbl_dia.pack(anchor='w', padx=15, pady=(5, 10))
        
        # ----- PLANILHA DE ORIGEM -----
        frame_origem = ctk.CTkFrame(main_frame)
        frame_origem.pack(fill='x', pady=5)
        
        ctk.CTkLabel(frame_origem, text="Planilha de Origem (de onde copiar os dados):",
                     font=ctk.CTkFont(size=12, weight='bold')).pack(anchor='w', padx=15, pady=(10, 5))
        
        row_origem = ctk.CTkFrame(frame_origem, fg_color='transparent')
        row_origem.pack(fill='x', padx=15, pady=5)
        
        self.entrada_origem = ctk.CTkEntry(row_origem, placeholder_text="ID da planilha ou URL...", height=35)
        self.entrada_origem.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        ctk.CTkButton(row_origem, text="Selecionar", command=self.selecionar_origem,
                      width=100, height=35, fg_color='#667eea').pack(side='right')
        
        self.lbl_origem = ctk.CTkLabel(frame_origem, text="Nenhuma planilha selecionada",
                                        text_color='gray', font=ctk.CTkFont(size=10))
        self.lbl_origem.pack(anchor='w', padx=15, pady=(0, 10))
        
        # ----- GABARITO -----
        frame_gabarito = ctk.CTkFrame(main_frame)
        frame_gabarito.pack(fill='x', pady=5)
        
        ctk.CTkLabel(frame_gabarito, text="Gabarito (uma letra por linha, maximo 100):",
                     font=ctk.CTkFont(size=12, weight='bold')).pack(anchor='w', padx=15, pady=(10, 5))
        
        self.texto_gabarito = ctk.CTkTextbox(frame_gabarito, height=120, font=ctk.CTkFont(size=13))
        self.texto_gabarito.pack(fill='x', padx=15, pady=5)
        self.texto_gabarito.insert('1.0', "Digite o gabarito aqui...\nExemplo:\nA\nB\nC\nD\nE")
        
        self.lbl_contagem = ctk.CTkLabel(frame_gabarito, text="0 letras",
                                          text_color='gray', font=ctk.CTkFont(size=10))
        self.lbl_contagem.pack(anchor='w', padx=15, pady=(0, 5))
        
        # Atualiza contagem ao digitar
        self.texto_gabarito.bind('<KeyRelease>', self.atualizar_contagem)
        
        ctk.CTkButton(frame_gabarito, text="Limpar Gabarito", command=self.limpar_gabarito,
                      width=120, height=30, fg_color='#ff5252', text_color='white',
                      font=ctk.CTkFont(size=11)).pack(anchor='w', padx=15, pady=(0, 10))
        
        # ----- BOTÃO EXECUTAR -----
        self.btn_executar = ctk.CTkButton(main_frame, text="EXECUTAR", command=self.executar,
                                           height=50, fg_color='#4CAF50', text_color='white',
                                           font=ctk.CTkFont(size=16, weight='bold'))
        self.btn_executar.pack(pady=15)
        
        # ----- BARRA DE STATUS -----
        self.lbl_status = ctk.CTkLabel(self.root, text="Pronto para iniciar",
                                        text_color='gray', font=ctk.CTkFont(size=11))
        self.lbl_status.pack(side='bottom', pady=10)
    
    def extrair_id_planilha(self, texto):
        """Extrai o ID da planilha de uma URL ou texto"""
        if not texto:
            return None
        
        # Se for URL, extrai o ID
        if 'spreadsheets/d/' in texto:
            inicio = texto.find('spreadsheets/d/') + len('spreadsheets/d/')
            fim = texto.find('/', inicio) if '/' in texto[inicio:] else len(texto)
            return texto[inicio:fim]
        
        # Se já for o ID puro
        if len(texto) > 30 and '/' not in texto:
            return texto
        
        return None
    
    def selecionar_destino(self):
        """Seleciona a planilha de destino"""
        id_planilha = self.extrair_id_planilha(self.entrada_destino.get())
        
        if not id_planilha:
            messagebox.showwarning("Atencao", "Cole o ID ou URL da planilha de destino.")
            return
        
        try:
            planilha = self.client.open_by_key(id_planilha)
            self.planilha_destino_id = id_planilha
            
            # Lista abas
            abas = [aba.title for aba in planilha.worksheets()]
            
            self.lbl_destino.configure(
                text=f"Planilha: {planilha.title} | Abas: {', '.join(abas[:5])}{'...' if len(abas) > 5 else ''}",
                text_color='green'
            )
            self.lbl_status.configure(text=f"Planilha destino selecionada: {planilha.title}", text_color='green')
        except Exception as e:
            self.lbl_destino.configure(text=f"Erro: {str(e)[:60]}", text_color='red')
            messagebox.showerror("Erro", f"Nao foi possivel acessar a planilha:\n{str(e)}")
    
    def selecionar_origem(self):
        """Seleciona a planilha de origem"""
        id_planilha = self.extrair_id_planilha(self.entrada_origem.get())
        
        if not id_planilha:
            messagebox.showwarning("Atencao", "Cole o ID ou URL da planilha de origem.")
            return
        
        try:
            planilha = self.client.open_by_key(id_planilha)
            self.planilha_origem_id = id_planilha
            
            self.lbl_origem.configure(
                text=f"Planilha: {planilha.title} | {planilha.sheet1.title}",
                text_color='green'
            )
            self.lbl_status.configure(text=f"Planilha origem selecionada: {planilha.title}", text_color='green')
        except Exception as e:
            self.lbl_origem.configure(text=f"Erro: {str(e)[:60]}", text_color='red')
            messagebox.showerror("Erro", f"Nao foi possivel acessar a planilha:\n{str(e)}")
    
    def selecionar_dia(self, dia):
        """Seleciona 1 ou 2 dia"""
        self.dia_selecionado = dia
        
        # Atualiza visual dos botões
        if dia == 1:
            self.btn_dia1.configure(fg_color='#2196F3')
            self.btn_dia2.configure(fg_color='#9E9E9E')
            self.lbl_dia.configure(text="Selecionado: 1 DIA (RESPOSTA-1Dia)", text_color='#2196F3')
        else:
            self.btn_dia1.configure(fg_color='#9E9E9E')
            self.btn_dia2.configure(fg_color='#2196F3')
            self.lbl_dia.configure(text="Selecionado: 2 DIA (RESPOSTA-2Dia)", text_color='#2196F3')
    
    def atualizar_contagem(self, event=None):
        """Atualiza contagem de letras do gabarito"""
        texto = self.texto_gabarito.get('1.0', 'end-1c')
        if texto == "Digite o gabarito aqui...\nExemplo:\nA\nB\nC\nD\nE":
            self.lbl_contagem.configure(text="0 letras", text_color='gray')
            return
        
        # Conta linhas não vazias
        linhas = [l.strip().upper() for l in texto.split('\n') if l.strip()]
        count = len(linhas)
        
        if count > 100:
            self.lbl_contagem.configure(text=f"{count} letras (maximo 100!)", text_color='red')
        else:
            self.lbl_contagem.configure(text=f"{count} letras", text_color='green')
    
    def limpar_gabarito(self):
        """Limpa o campo de gabarito"""
        self.texto_gabarito.delete('1.0', 'end')
        self.texto_gabarito.insert('1.0', '')
        self.lbl_contagem.configure(text="0 letras", text_color='gray')
    
    def validar_campos(self):
        """Valida se todos os campos foram preenchidos"""
        if not self.planilha_destino_id:
            messagebox.showwarning("Validacao", "Selecione a planilha de DESTINO.")
            return False
        
        if not self.dia_selecionado:
            messagebox.showwarning("Validacao", "Selecione 1 DIA ou 2 DIA.")
            return False
        
        if not self.planilha_origem_id:
            messagebox.showwarning("Validacao", "Selecione a planilha de ORIGEM.")
            return False
        
        # Valida gabarito
        texto = self.texto_gabarito.get('1.0', 'end-1c')
        if texto == "Digite o gabarito aqui...\nExemplo:\nA\nB\nC\nD\nE":
            messagebox.showwarning("Validacao", "Insira o gabarito.")
            return False
        
        linhas = [l.strip().upper() for l in texto.split('\n') if l.strip()]
        if not linhas:
            messagebox.showwarning("Validacao", "O gabarito esta vazio.")
            return False
        
        if len(linhas) > 100:
            messagebox.showwarning("Validacao", f"Gabarito com {len(linhas)} letras. Maximo permitido: 100.")
            return False
        
        # Salva gabarito processado
        self.gabarito_texto = linhas
        
        return True
    
    def executar(self):
        """Executa o processo principal"""
        if not self.validar_campos():
            return
        
        self.btn_executar.configure(text="EXECUTANDO...", state='disabled', fg_color='#FF9800')
        self.lbl_status.configure(text="Processando...", text_color='#FF9800')
        self.root.update()
        
        # Executa em thread separada para não travar a interface
        thread = threading.Thread(target=self._executar_processo)
        thread.daemon = True
        thread.start()
    
    def _executar_processo(self):
        """Processo principal em thread"""
        try:
            # Abre planilhas
            planilha_destino = self.client.open_by_key(self.planilha_destino_id)
            planilha_origem = self.client.open_by_key(self.planilha_origem_id)
            
            # Determina aba de resposta
            nome_aba_resposta = f'RESPOSTA-{self.dia_selecionado}Dia'
            
            # Verifica se a aba existe
            try:
                aba_resposta = planilha_destino.worksheet(nome_aba_resposta)
            except:
                self._erro(f"Aba '{nome_aba_resposta}' nao encontrada na planilha de destino!")
                return
            
            # Copia dados da origem
            aba_origem = planilha_origem.sheet1
            dados_origem = aba_origem.get_all_values()
            
            if not dados_origem:
                self._erro("A planilha de origem esta vazia!")
                return
            
            # Limpa e cola na aba de resposta
            aba_resposta.clear()
            aba_resposta.update('A1', dados_origem)
            
            self._log(f"Dados copiados para '{nome_aba_resposta}': {len(dados_origem)} linhas x {len(dados_origem[0])} colunas")
            
            # Cola gabarito na aba Gabarito
            try:
                aba_gabarito = planilha_destino.worksheet('Gabarito')
            except:
                self._erro("Aba 'Gabarito' nao encontrada na planilha de destino!")
                return
            
            # Prepara gabarito para colar a partir de C3
            gabarito_coluna = [[letra] for letra in self.gabarito_texto]
            
            # Atualiza a partir de C3
            aba_gabarito.update('C3', gabarito_coluna)
            
            self._log(f"Gabarito inserido em 'Gabarito' C3:C{2 + len(self.gabarito_texto)}: {len(self.gabarito_texto)} letras")
            
            # Sucesso!
            self.root.after(0, self._sucesso)
            
        except Exception as e:
            self.root.after(0, lambda: self._erro(str(e)))
    
    def _log(self, mensagem):
        """Atualiza status"""
        self.root.after(0, lambda: self.lbl_status.configure(text=mensagem, text_color='green'))
    
    def _erro(self, mensagem):
        """Mostra erro"""
        self.root.after(0, lambda: self.lbl_status.configure(text=f"Erro: {mensagem[:80]}", text_color='red'))
        self.root.after(0, lambda: self.btn_executar.configure(text="EXECUTAR", state='normal', fg_color='#4CAF50'))
        self.root.after(0, lambda: messagebox.showerror("Erro", mensagem))
    
    def _sucesso(self):
        """Mostra mensagem de sucesso"""
        self.btn_executar.configure(text="EXECUTAR", state='normal', fg_color='#4CAF50')
        self.lbl_status.configure(text="Processo concluido com sucesso!", text_color='green')
        messagebox.showinfo("Sucesso", 
                           f"Processo concluido!\n\n"
                           f"Dados copiados para: RESPOSTA-{self.dia_selecionado}Dia\n"
                           f"Gabarito inserido em: Gabarito C3:C{2 + len(self.gabarito_texto)}")
    
    def iniciar(self):
        """Inicia o aplicativo"""
        self.root.mainloop()


if __name__ == '__main__':
    app = GeradorRanks()
    app.iniciar()