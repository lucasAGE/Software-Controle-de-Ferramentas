import os
import sqlite3
import pandas as pd
import datetime

from database.config import DATABASE_CAMINHO  # Note que não usamos mais EXPORT_DIR fixo
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox,
    QLineEdit, QFormLayout, QFileDialog
)
from PyQt5.QtCore import Qt

# Lógica para definição dos turnos
TURNOS = {
    "1turno": datetime.time(6, 0),
    "2turno": datetime.time(14, 0),
    "3turno": datetime.time(22, 0),
}

def get_turno_atual():
    agora = datetime.datetime.now().time()
    # Itera em ordem reversa para encontrar o turno apropriado
    for nome, hora in reversed(list(TURNOS.items())):
        if agora >= hora:
            return nome
    return "1turno"

def get_export_filename(nome_tabela, data=None, turno=None):
    """
    Gera o nome do arquivo de exportação conforme o padrão:
    [nome_da_tabela]_[YYYY-MM-DD]_[turno].xlsx
    """
    if data is None:
        data = datetime.date.today()
    if turno is None:
        turno = get_turno_atual()
    return f"{nome_tabela}_{data}_{turno}.xlsx"

class TelaExportacao(QWidget):
    def __init__(self, navegacao):
        """
        Inicializa a tela de exportação de dados.
        
        Parâmetros:
            navegacao: objeto responsável pela navegação entre telas.
        """
        super().__init__()
        self.navegacao = navegacao
        self.init_ui()

    def init_ui(self):
        """
        Configura a interface do usuário, criando o layout, os rótulos, formulários e botões.
        """
        layout = QVBoxLayout()
        layout.addWidget(self._criar_label_titulo())
        layout.addLayout(self._criar_painel_listagem_tabelas())
        layout.addWidget(self._criar_btn_exportar_todas())
        #layout.addLayout(self._criar_formulario_especifica())
        #layout.addWidget(self._criar_btn_exportar_especifica())
        layout.addWidget(self._criar_btn_abrir_pasta_export())
        layout.addWidget(self._criar_btn_voltar())
        self.setLayout(layout)

    def _criar_label_titulo(self):
        label = QLabel("Exportação de Dados")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _criar_painel_listagem_tabelas(self):
        """
        Cria um painel simples exibindo a listagem fixa das tabelas e o resumo dos nomes das colunas.
        """
        painel = QVBoxLayout()
        tabelas_info = {
            "usuarios": "id, nome, senha, rfid, tipo",
            "ferramentas": "id, nome, codigo_barra, quantidade, estoque_ativo, consumivel",
            "logs": "id, usuario_id, ferramenta_id, acao, data_hora, quantidade, motivo, operacoes, avaliacao",
            "maquinas": "id, nome"
        }
        for tabela, colunas in tabelas_info.items():
            label_tabela = QLabel(f"Tabela: {tabela}")
            label_tabela.setStyleSheet("font-weight: bold;")
            label_colunas = QLabel(f"Colunas: {colunas}")
            painel.addWidget(label_tabela)
            painel.addWidget(label_colunas)
        return painel

    def _criar_btn_exportar_todas(self):
        btn = QPushButton("Exportar Todas as Tabelas")
        btn.clicked.connect(self.exportar_todas_tabelas)
        return btn

    def _criar_formulario_especifica(self):
        form = QFormLayout()
        self.tabela_input = QLineEdit()
        self.tabela_input.setPlaceholderText("Nome da tabela a exportar")
        form.addRow("Nome da Tabela:", self.tabela_input)
        return form

    def _criar_btn_exportar_especifica(self):
        btn = QPushButton("Exportar Tabela Específica")
        btn.clicked.connect(self.exportar_tabela_especifica)
        return btn

    def _criar_btn_abrir_pasta_export(self):
        btn = QPushButton("Abrir Pasta de Exportação")
        btn.clicked.connect(self.abrir_pasta_export)
        return btn

    def _criar_btn_voltar(self):
        btn = QPushButton("⬅️ Voltar")
        btn.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))
        return btn

    def _exibir_mensagem(self, titulo, mensagem, tipo="info"):
        if tipo == "info":
            QMessageBox.information(self, titulo, mensagem)
        else:
            QMessageBox.warning(self, titulo, mensagem)

    def selecionar_pasta_export(self):
        """
        Abre um diálogo para que o usuário escolha a pasta de destino para a exportação.
        """
        pasta = QFileDialog.getExistingDirectory(self, "Selecione a pasta de exportação")
        return pasta

    def abrir_pasta_export(self):
        """
        Abre o explorador de arquivos na pasta escolhida pelo usuário.
        """
        pasta = self.selecionar_pasta_export()
        if pasta:
            try:
                os.startfile(pasta)  # Método específico para Windows
            except Exception as e:
                self._exibir_mensagem("Erro", f"Não foi possível abrir a pasta: {e}", "warning")

    def exportar_todas_tabelas(self):
        """
        Exporta todas as tabelas do banco de dados para arquivos Excel individuais.
        """
        if self.exportar_todas_tabelas_para_excel():
            self._exibir_mensagem("Sucesso", "Todas as tabelas foram exportadas com sucesso!", "info")
        else:
            self._exibir_mensagem("Erro", "Falha ao exportar tabelas!", "warning")

    def exportar_tabela_especifica(self):
        """
        Exporta uma tabela específica para um arquivo Excel, conforme informado pelo usuário.
        """
        nome_tabela = self.tabela_input.text().strip()
        if not nome_tabela:
            self._exibir_mensagem("Erro", "Informe o nome da tabela a exportar.", "warning")
            return
        pasta_destino = self.selecionar_pasta_export()
        if not pasta_destino:
            self._exibir_mensagem("Exportação Cancelada", "Nenhuma pasta selecionada.", "warning")
            return
        caminho_exportacao = os.path.join(pasta_destino, get_export_filename(nome_tabela))
        if self.exportar_tabela_para_excel(nome_tabela, caminho_exportacao):
            self._exibir_mensagem("Sucesso", f"Tabela '{nome_tabela}' exportada com sucesso!", "info")
        else:
            self._exibir_mensagem("Erro", f"Erro ao exportar a tabela '{nome_tabela}'.", "warning")

    def exportar_tabela_para_excel(self, nome_tabela, caminho_arquivo):
        """
        Exporta uma tabela específica para um arquivo Excel.
        
        Parâmetros:
            nome_tabela (str): Nome da tabela a ser exportada.
            caminho_arquivo (str): Caminho completo do arquivo Excel a ser gerado.
            
        Retorna:
            bool: True se a exportação foi bem-sucedida; caso contrário, False.
        """
        conexao = None
        try:
            os.makedirs(os.path.dirname(caminho_arquivo), exist_ok=True)
            conexao = sqlite3.connect(DATABASE_CAMINHO)
            query = f"SELECT * FROM {nome_tabela}"
            df = pd.read_sql_query(query, conexao)
            if df.empty:
                print(f"⚠️ A tabela '{nome_tabela}' está vazia.")
                return False
            df.to_excel(caminho_arquivo, index=False, engine='openpyxl')
            print(f"✅ Tabela '{nome_tabela}' exportada com sucesso em {caminho_arquivo}.")
            return True
        except Exception as e:
            print(f"❌ Erro ao exportar tabela '{nome_tabela}': {e}")
            return False
        finally:
            if conexao:
                conexao.close()

    def exportar_todas_tabelas_para_excel(self):
        """
        Exporta todas as tabelas do banco de dados para arquivos Excel individuais.
        
        Retorna:
            bool: True se pelo menos uma tabela foi exportada com sucesso; caso contrário, False.
        """
        pasta_destino = self.selecionar_pasta_export()
        if not pasta_destino:
            self._exibir_mensagem("Exportação Cancelada", "Nenhuma pasta selecionada.", "warning")
            return False

        conexao = None
        try:
            os.makedirs(pasta_destino, exist_ok=True)
            conexao = sqlite3.connect(DATABASE_CAMINHO)
            cursor = conexao.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = cursor.fetchall()
            if not tabelas:
                print("⚠️ Nenhuma tabela encontrada.")
                return False
            sucesso = False
            for tabela in tabelas:
                nome_tabela = tabela[0]
                caminho = os.path.join(pasta_destino, get_export_filename(nome_tabela))
                if self.exportar_tabela_para_excel(nome_tabela, caminho):
                    sucesso = True
            return sucesso
        except Exception as e:
            print(f"❌ Erro ao exportar todas as tabelas: {e}")
            return False
        finally:
            if conexao:
                conexao.close()
