"""
Painel de Alunos - Visualizador de CSV
Compatível com Python 3.8+
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import json
import os
import sys

# Arquivo de configuração (salva o último CSV usado)
CONFIG_FILE = "painel_config.json"

def salvar_config(caminho):
    """Salva o caminho do último CSV usado"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"ultimo_csv": caminho}, f)
    except:
        pass

def carregar_config():
    """Carrega o caminho do último CSV usado"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f).get("ultimo_csv", "")
    except:
        pass
    return ""

class PainelAlunos:
    def __init__(self, root):
        self.root = root
        self.root.title("Painel de Alunos")
        self.root.geometry("1200x750")
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        self.df = pd.DataFrame()
        self.df_filtrado = pd.DataFrame()
        self.pagina = 1
        self.reg_por_pagina = 30
        self.arquivo_atual = None
        self.ordenacao_coluna = None
        self.ordenacao_asc = True
        
        self.criar_interface()
        
        # Tenta carregar o último arquivo
        ultimo = carregar_config()
        if ultimo and os.path.exists(ultimo):
            self.arquivo_atual = ultimo
            self.carregar_csv(ultimo, mostrar_msg=False)
        else:
            self.mostrar_tela_inicial()
    
    def mostrar_tela_inicial(self):
        """Mostra mensagem inicial"""
        self.lbl_status.config(text="Bem-vindo! Selecione um arquivo CSV para começar.", fg='#667eea')
        self.lbl_caminho.config(text="Nenhum arquivo selecionado")
    
    def criar_interface(self):
        # ===== BARRA SUPERIOR =====
        topo = tk.Frame(self.root, bg='#667eea', height=50)
        topo.pack(fill='x')
        topo.pack_propagate(False)
        
        tk.Label(topo, text="Painel de Alunos", bg='#667eea', fg='white',
                font=('Segoe UI', 16, 'bold')).pack(side='left', padx=20, pady=10)
        
        # ===== BARRA DE FERRAMENTAS =====
        toolbar = tk.Frame(self.root, bg='#f8f9fa', height=45)
        toolbar.pack(fill='x', padx=10, pady=5)
        toolbar.pack_propagate(False)
        
        self.btn_atualizar = tk.Button(toolbar, text="Atualizar", command=self.recarregar,
                                       bg='#667eea', fg='white', font=('Segoe UI', 9, 'bold'),
                                       padx=15, pady=3, bd=0, cursor='hand2')
        self.btn_atualizar.pack(side='left', padx=3)
        
        self.btn_selecionar = tk.Button(toolbar, text="Selecionar CSV", command=self.selecionar_arquivo,
                                        bg='white', fg='#333', font=('Segoe UI', 9),
                                        padx=15, pady=3, bd=1, cursor='hand2')
        self.btn_selecionar.pack(side='left', padx=3)
        
        tk.Button(toolbar, text="Exportar", command=self.exportar,
                 bg='#4caf50', fg='white', font=('Segoe UI', 9, 'bold'),
                 padx=15, pady=3, bd=0, cursor='hand2').pack(side='left', padx=3)
        
        # Separador
        ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=10, pady=5)
        
        # Caminho do arquivo
        self.lbl_caminho = tk.Label(toolbar, text="", fg='#666', font=('Segoe UI', 8), bg='#f8f9fa')
        self.lbl_caminho.pack(side='left', padx=5)
        
        # ===== ÁREA DE BUSCA =====
        busca_frame = tk.Frame(self.root, bg='white')
        busca_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(busca_frame, text="Buscar:", font=('Segoe UI', 12), bg='white').pack(side='left', padx=(10, 5))
        
        self.entrada_busca = tk.Entry(busca_frame, font=('Segoe UI', 11), bd=0, width=30)
        self.entrada_busca.pack(side='left', fill='x', expand=True, padx=5, pady=8)
        self.entrada_busca.bind('<KeyRelease>', self.filtrar)
        self.entrada_busca.insert(0, "Buscar por nome, RA, CPF, curso...")
        self.entrada_busca.config(fg='gray')
        self.entrada_busca.bind('<FocusIn>', self._on_focus_in)
        self.entrada_busca.bind('<FocusOut>', self._on_focus_out)
        
        tk.Label(busca_frame, text="Coluna:", font=('Segoe UI', 9), bg='white', fg='#666').pack(side='left', padx=(15, 5))
        
        self.coluna_filtro = ttk.Combobox(busca_frame, width=22, state='readonly', font=('Segoe UI', 9))
        self.coluna_filtro.pack(side='left', padx=5, pady=8)
        self.coluna_filtro.bind('<<ComboboxSelected>>', self.filtrar)
        
        tk.Button(busca_frame, text="Limpar", command=self.limpar_busca,
                 bg='#ff5252', fg='white', font=('Segoe UI', 8, 'bold'),
                 padx=10, pady=3, bd=0, cursor='hand2').pack(side='left', padx=10)
        
        # ===== TABELA =====
        tabela_frame = tk.Frame(self.root)
        tabela_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Frame para Treeview com scrollbars
        tree_frame = tk.Frame(tabela_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Treeview com linhas alternadas e seleção de células
        self.tree = ttk.Treeview(tree_frame, show='headings', selectmode='extended')
        
        # Configurar tags para linhas alternadas
        self.tree.tag_configure('evenrow', background='#f8f9fa')
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('selected', background='#c8e6c9')
        
        vsb = tk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        hsb = tk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind para copiar (Ctrl+C)
        self.tree.bind('<Control-c>', self.copiar_selecao)
        self.tree.bind('<Control-C>', self.copiar_selecao)
        
        # Menu de contexto (botão direito)
        self.menu_contexto = tk.Menu(self.root, tearoff=0)
        self.menu_contexto.add_command(label="Copiar", command=self.copiar_selecao)
        self.menu_contexto.add_command(label="Copiar com cabeçalhos", command=self.copiar_com_cabecalhos)
        self.menu_contexto.add_separator()
        self.menu_contexto.add_command(label="Selecionar tudo", command=self.selecionar_tudo)
        
        self.tree.bind('<Button-3>', self.mostrar_menu_contexto)
        
        # ===== PAGINAÇÃO =====
        pag_frame = tk.Frame(self.root, bg='#f8f9fa', height=40)
        pag_frame.pack(fill='x', padx=10, pady=5)
        pag_frame.pack_propagate(False)
        
        tk.Label(pag_frame, text="Registros por pagina:", font=('Segoe UI', 9), 
                bg='#f8f9fa', fg='#666').pack(side='left', padx=(10, 5))
        
        self.spin_pagina = tk.Spinbox(pag_frame, from_=10, to=100, width=5, 
                                       font=('Segoe UI', 9), command=self.mudar_registros_pagina)
        self.spin_pagina.delete(0, 'end')
        self.spin_pagina.insert(0, '30')
        self.spin_pagina.pack(side='left', padx=2)
        
        # Botões de navegação
        nav_frame = tk.Frame(pag_frame, bg='#f8f9fa')
        nav_frame.pack(side='right', padx=10)
        
        self.btn_anterior = tk.Button(nav_frame, text="Anterior", command=self.pag_anterior,
                                      font=('Segoe UI', 9), padx=10, bd=1, cursor='hand2')
        self.btn_anterior.pack(side='left', padx=2)
        
        self.lbl_pagina = tk.Label(nav_frame, text="", font=('Segoe UI', 9), 
                                    bg='#f8f9fa', width=25)
        self.lbl_pagina.pack(side='left', padx=5)
        
        self.btn_proximo = tk.Button(nav_frame, text="Proximo", command=self.prox_pagina,
                                     font=('Segoe UI', 9), padx=10, bd=1, cursor='hand2')
        self.btn_proximo.pack(side='left', padx=2)
        
        # ===== BARRA DE STATUS =====
        status_frame = tk.Frame(self.root, bg='#e8eaf6', height=30)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)
        
        self.lbl_status = tk.Label(status_frame, text="", fg='#333', font=('Segoe UI', 9), 
                                    bg='#e8eaf6', anchor='w')
        self.lbl_status.pack(side='left', fill='x', padx=10, pady=3)
    
    def _on_focus_in(self, event):
        if self.entrada_busca.get() == "Buscar por nome, RA, CPF, curso...":
            self.entrada_busca.delete(0, 'end')
            self.entrada_busca.config(fg='black')
    
    def _on_focus_out(self, event):
        if not self.entrada_busca.get():
            self.entrada_busca.insert(0, "Buscar por nome, RA, CPF, curso...")
            self.entrada_busca.config(fg='gray')
    
    def mostrar_menu_contexto(self, event):
        """Mostra menu ao clicar com botão direito"""
        try:
            self.menu_contexto.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu_contexto.grab_release()
    
    def copiar_selecao(self, event=None):
        """Copia itens selecionados para a área de transferência"""
        selecionados = self.tree.selection()
        if not selecionados:
            return
        
        linhas = []
        for item in selecionados:
            valores = self.tree.item(item)['values']
            linha = '\t'.join(str(v) for v in valores)
            linhas.append(linha)
        
        texto = '\n'.join(linhas)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        
        self.lbl_status.config(text=f"Copiado(s) {len(selecionados)} registro(s)", fg='#2e7d32')
    
    def copiar_com_cabecalhos(self):
        """Copia seleção incluindo cabeçalhos"""
        selecionados = self.tree.selection()
        if not selecionados:
            return
        
        colunas = self.tree['columns']
        cabecalho = '\t'.join(colunas)
        
        linhas = []
        for item in selecionados:
            valores = self.tree.item(item)['values']
            linha = '\t'.join(str(v) for v in valores)
            linhas.append(linha)
        
        texto = cabecalho + '\n' + '\n'.join(linhas)
        self.root.clipboard_clear()
        self.root.clipboard_append(texto)
        
        self.lbl_status.config(text=f"Copiado(s) {len(selecionados)} registro(s) com cabecalhos", fg='#2e7d32')
    
    def selecionar_tudo(self):
        """Seleciona todos os itens visíveis"""
        for item in self.tree.get_children():
            self.tree.selection_add(item)
    
    def carregar_csv(self, caminho, mostrar_msg=True):
        """Carrega arquivo CSV"""
        try:
            if mostrar_msg:
                self.lbl_status.config(text="Carregando dados...", fg='#f57c00')
                self.root.update()
            
            self.df = pd.read_csv(caminho, dtype=str).fillna('')
            self.df_filtrado = self.df.copy()
            self.arquivo_atual = caminho
            self.pagina = 1
            
            # Salva preferência
            salvar_config(caminho)
            
            # Atualiza interface
            self.atualizar_tabela()
            
            from datetime import datetime
            data_mod = os.path.getmtime(caminho)
            data_str = datetime.fromtimestamp(data_mod).strftime('%d/%m/%Y %H:%M')
            nome = os.path.basename(caminho)
            tamanho = os.path.getsize(caminho)
            
            if tamanho > 1024 * 1024:
                tamanho_str = f"{tamanho / (1024*1024):.1f} MB"
            else:
                tamanho_str = f"{tamanho / 1024:.1f} KB"
            
            self.lbl_status.config(
                text=f"{len(self.df):,} registros | {len(self.df.columns)} colunas | {tamanho_str} | Atualizado: {data_str}",
                fg='#2e7d32'
            )
            self.lbl_caminho.config(text=f"Arquivo: {nome}")
            
        except Exception as e:
            self.lbl_status.config(text=f"Erro ao carregar: {str(e)[:80]}", fg='#c62828')
            if mostrar_msg:
                messagebox.showerror("Erro", f"Nao foi possivel carregar o arquivo:\n\n{str(e)}")
    
    def recarregar(self):
        """Recarrega o arquivo atual"""
        if self.arquivo_atual and os.path.exists(self.arquivo_atual):
            self.carregar_csv(self.arquivo_atual)
        elif self.arquivo_atual:
            messagebox.showwarning("Arquivo nao encontrado", 
                                  f"O arquivo nao foi encontrado:\n{self.arquivo_atual}\n\nSelecione novamente.")
            self.selecionar_arquivo()
        else:
            self.selecionar_arquivo()
    
    def selecionar_arquivo(self):
        """Abre diálogo para selecionar CSV"""
        arquivo = filedialog.askopenfilename(
            title="Selecionar arquivo CSV",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
            initialdir=os.path.dirname(self.arquivo_atual) if self.arquivo_atual else None
        )
        if arquivo:
            self.carregar_csv(arquivo)
    
    def atualizar_tabela(self):
        """Renderiza a tabela com os dados"""
        # Limpa tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.df_filtrado.empty:
            self.tree['columns'] = []
            return
        
        # Configura colunas com largura ajustada
        colunas = list(self.df_filtrado.columns)
        self.tree['columns'] = colunas
        
        for col in colunas:
            # Largura baseada no nome completo da coluna
            largura = max(100, min(300, len(str(col)) * 10))
            self.tree.heading(col, text=col, 
                            command=lambda c=col: self.ordenar_por_coluna(c))
            self.tree.column(col, width=largura, minwidth=80, stretch=True)
        
        # Atualiza combobox de filtro
        self.coluna_filtro['values'] = ['Todas as colunas'] + colunas
        if not self.coluna_filtro.get() or self.coluna_filtro.get() not in self.coluna_filtro['values']:
            self.coluna_filtro.set('Todas as colunas')
        
        # Paginação
        inicio = (self.pagina - 1) * self.reg_por_pagina
        fim = min(inicio + self.reg_por_pagina, len(self.df_filtrado))
        pagina_df = self.df_filtrado.iloc[inicio:fim]
        
        # Insere dados com linhas alternadas
        for idx, (_, row) in enumerate(pagina_df.iterrows()):
            valores = [str(v)[:200] if pd.notna(v) else '' for v in row]
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert('', 'end', values=valores, tags=(tag,))
        
        # Atualiza info de paginação
        total_pag = max(1, (len(self.df_filtrado) - 1) // self.reg_por_pagina + 1)
        self.lbl_pagina.config(
            text=f"Pagina {self.pagina} de {total_pag} ({inicio+1:,}-{fim:,} de {len(self.df_filtrado):,})"
        )
        
        # Estado dos botões
        self.btn_anterior.config(state='normal' if self.pagina > 1 else 'disabled')
        self.btn_proximo.config(state='normal' if self.pagina < total_pag else 'disabled')
    
    def ordenar_por_coluna(self, coluna):
        """Ordena pela coluna clicada"""
        if self.ordenacao_coluna == coluna:
            self.ordenacao_asc = not self.ordenacao_asc
        else:
            self.ordenacao_coluna = coluna
            self.ordenacao_asc = True
        
        self.df_filtrado = self.df_filtrado.sort_values(coluna, ascending=self.ordenacao_asc)
        self.pagina = 1
        self.atualizar_tabela()
    
    def mudar_registros_pagina(self):
        """Altera quantidade de registros por página"""
        try:
            valor = int(self.spin_pagina.get())
            if 5 <= valor <= 200:
                self.reg_por_pagina = valor
                self.pagina = 1
                self.atualizar_tabela()
        except:
            pass
    
    def filtrar(self, event=None):
        """Filtra dados conforme busca"""
        termo = self.entrada_busca.get().lower().strip()
        if termo == "buscar por nome, ra, cpf, curso...":
            termo = ""
        
        coluna = self.coluna_filtro.get()
        
        if termo:
            try:
                if coluna and coluna != 'Todas as colunas':
                    mask = self.df[coluna].astype(str).str.lower().str.contains(termo, na=False)
                    self.df_filtrado = self.df[mask]
                else:
                    mask = self.df.apply(
                        lambda row: row.astype(str).str.lower().str.contains(termo, na=False).any(), 
                        axis=1
                    )
                    self.df_filtrado = self.df[mask]
            except:
                self.df_filtrado = self.df.copy()
        else:
            self.df_filtrado = self.df.copy()
        
        self.pagina = 1
        self.atualizar_tabela()
    
    def limpar_busca(self):
        """Limpa campo de busca"""
        self.entrada_busca.delete(0, 'end')
        self.coluna_filtro.set('Todas as colunas')
        self.filtrar()
    
    def pag_anterior(self):
        """Vai para página anterior"""
        if self.pagina > 1:
            self.pagina -= 1
            self.atualizar_tabela()
    
    def prox_pagina(self):
        """Vai para próxima página"""
        total_pag = max(1, (len(self.df_filtrado) - 1) // self.reg_por_pagina + 1)
        if self.pagina < total_pag:
            self.pagina += 1
            self.atualizar_tabela()
    
    def exportar(self):
        """Exporta dados filtrados para CSV"""
        if self.df_filtrado.empty:
            messagebox.showwarning("Sem dados", "Nao ha dados para exportar.")
            return
        
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            title="Exportar dados"
        )
        if arquivo:
            try:
                self.df_filtrado.to_csv(arquivo, index=False, encoding='utf-8-sig')
                messagebox.showinfo("Sucesso", 
                                   f"Dados exportados com sucesso!\n\n{len(self.df_filtrado):,} registros")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao exportar:\n{str(e)}")


def main():
    root = tk.Tk()
    
    # Centralizar janela
    root.update_idletasks()
    w = 1200
    h = 750
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f'{w}x{h}+{x}+{y}')
    
    app = PainelAlunos(root)
    root.mainloop()

if __name__ == '__main__':
    main()