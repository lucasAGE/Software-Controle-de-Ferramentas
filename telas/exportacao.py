import os
import sqlite3
import pandas as pd
from database.config import DATABASE_CAMINHO, EXPORT_DIR

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QLineEdit, QFormLayout
)
from PyQt5.QtCore import Qt


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
        layout.addWidget(self._criar_btn_exportar_todas())
        layout.addLayout(self._criar_formulario_especifica())
        layout.addWidget(self._criar_btn_exportar_especifica())
        layout.addWidget(self._criar_btn_voltar())
        self.setLayout(layout)

    def _criar_label_titulo(self):
        """
        Cria e retorna o rótulo do título da tela.
        """
        label = QLabel("Exportação de Dados")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _criar_btn_exportar_todas(self):
        """
        Cria e retorna o botão para exportar todas as tabelas.
        """
        btn = QPushButton("Exportar Todas as Tabelas")
        btn.clicked.connect(self.exportar_todas_tabelas)
        return btn

    def _criar_formulario_especifica(self):
        """
        Cria e retorna o formulário para exportação de uma tabela específica.
        """
        form = QFormLayout()
        self.tabela_input = QLineEdit()
        self.tabela_input.setPlaceholderText("Nome da tabela a exportar")
        form.addRow("Nome da Tabela:", self.tabela_input)
        return form

    def _criar_btn_exportar_especifica(self):
        """
        Cria e retorna o botão para exportar uma tabela específica.
        """
        btn = QPushButton("Exportar Tabela Específica")
        btn.clicked.connect(self.exportar_tabela_especifica)
        return btn

    def _criar_btn_voltar(self):
        """
        Cria e retorna o botão para retornar à tela anterior.
        """
        btn = QPushButton("⬅️ Voltar")
        btn.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))
        return btn

    def _exibir_mensagem(self, titulo, mensagem, tipo="info"):
        """
        Exibe uma mensagem para o usuário utilizando QMessageBox.

        Parâmetros:
            titulo (str): Título da mensagem.
            mensagem (str): Conteúdo da mensagem.
            tipo (str): Tipo da mensagem ('info' para informações, 'warning' para avisos).
        """
        if tipo == "info":
            QMessageBox.information(self, titulo, mensagem)
        else:
            QMessageBox.warning(self, titulo, mensagem)

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

        caminho_exportacao = os.path.join(EXPORT_DIR, f"{nome_tabela}.xlsx")
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
                print(f"⚠️  A tabela '{nome_tabela}' está vazia.")
                return False

            df.to_excel(caminho_arquivo, index=False, engine='openpyxl')
            print(f"✅ Tabela '{nome_tabela}' exportada com sucesso.")
            return True

        except Exception as e:
            print(f"❌ Erro ao exportar tabela: {e}")
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
        conexao = None
        try:
            os.makedirs(EXPORT_DIR, exist_ok=True)
            conexao = sqlite3.connect(DATABASE_CAMINHO)
            cursor = conexao.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tabelas = cursor.fetchall()

            if not tabelas:
                print("⚠️  Nenhuma tabela encontrada.")
                return False

            sucesso = False
            for tabela in tabelas:
                nome_tabela = tabela[0]
                caminho = os.path.join(EXPORT_DIR, f"{nome_tabela}.xlsx")
                if self.exportar_tabela_para_excel(nome_tabela, caminho):
                    sucesso = True

            return sucesso

        except Exception as e:
            print(f"❌ Erro ao exportar todas as tabelas: {e}")
            return False

        finally:
            if conexao:
                conexao.close()
