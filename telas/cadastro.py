import os
import sqlite3
import hashlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QMessageBox, QComboBox, QHBoxLayout
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

from utils.registro import registrar_usuario, registrar_ferramenta, registrar_maquina
from database.database_utils import executar_query

def hash_senha(senha):
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()

class TelaCadastros(QWidget):
    def __init__(self, navegacao):
        super().__init__()
        self.navegacao = navegacao
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.build_title()
        self.build_user_section()
        self.build_tool_section()
        self.build_machine_section()
        self.build_back_button()
        self.setLayout(self.layout)

    def build_title(self):
        label_titulo = QLabel("Cadastros")
        label_titulo.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label_titulo)

    def build_user_section(self):
        label_usuarios = QLabel("📅 Usuários")
        label_usuarios.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label_usuarios)

        self.nome_usuario_input = QLineEdit()
        self.senha_usuario_input = QLineEdit()
        self.senha_usuario_input.setEchoMode(QLineEdit.Password)
        self.rfid_usuario_input = QLineEdit()
        self.tipo_usuario_input = QComboBox()
        self.tipo_usuario_input.addItems(["admin", "usuario"])

        form_usuario = QFormLayout()
        form_usuario.addRow("Nome:", self.nome_usuario_input)
        form_usuario.addRow("Senha:", self.senha_usuario_input)
        form_usuario.addRow("RFID:", self.rfid_usuario_input)
        form_usuario.addRow("Tipo:", self.tipo_usuario_input)
        self.layout.addLayout(form_usuario)

        botoes_usuario = QHBoxLayout()
        btn_usuario = QPushButton("Adicionar Usuário")
        btn_usuario.clicked.connect(self.adicionar_usuario)
        btn_remover_usuario = QPushButton("Remover Usuário")
        btn_remover_usuario.clicked.connect(self.remover_usuario)
        botoes_usuario.addWidget(btn_usuario)
        botoes_usuario.addWidget(btn_remover_usuario)
        self.layout.addLayout(botoes_usuario)

    def build_tool_section(self):
        label_ferramentas = QLabel("🔧 Ferramentas")
        label_ferramentas.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label_ferramentas)

        self.nome_ferramenta_input = QLineEdit()
        self.codigo_barra_input = QLineEdit()
        self.quantidade_input = QLineEdit()
        self.quantidade_input.setValidator(QIntValidator(0, 10000, self))
        self.estoque_ativo_input = QLineEdit()
        self.estoque_ativo_input.setValidator(QIntValidator(0, 10000, self))
        self.estoque_ativo_input.setPlaceholderText("Opcional (default: 0)")

        self.consumivel_input = QComboBox()
        self.consumivel_input.addItems(["NÃO", "SIM"])

        form_ferramenta = QFormLayout()
        form_ferramenta.addRow("Nome:", self.nome_ferramenta_input)
        form_ferramenta.addRow("Código de Barras:", self.codigo_barra_input)
        form_ferramenta.addRow("Estoque Almoxarifado:", self.quantidade_input)
        form_ferramenta.addRow("Estoque Ativo:", self.estoque_ativo_input)
        form_ferramenta.addRow("Consumível:", self.consumivel_input)
        self.layout.addLayout(form_ferramenta)

        botoes_ferramenta = QHBoxLayout()
        btn_ferramenta = QPushButton("Adicionar Ferramenta")
        btn_ferramenta.clicked.connect(self.adicionar_ferramenta)
        btn_remover_ferramenta = QPushButton("Remover Ferramenta")
        btn_remover_ferramenta.clicked.connect(self.remover_ferramenta)
        botoes_ferramenta.addWidget(btn_ferramenta)
        botoes_ferramenta.addWidget(btn_remover_ferramenta)
        self.layout.addLayout(botoes_ferramenta)

    def build_machine_section(self):
        label_maquinas = QLabel("🛠️ Máquinas")
        label_maquinas.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label_maquinas)

        self.nome_maquina_input = QLineEdit()
        form_maquina = QFormLayout()
        form_maquina.addRow("Nome:", self.nome_maquina_input)
        self.layout.addLayout(form_maquina)

        botoes_maquina = QHBoxLayout()
        btn_maquina = QPushButton("Adicionar Máquina")
        btn_maquina.clicked.connect(self.adicionar_maquina)
        btn_remover_maquina = QPushButton("Remover Máquina")
        btn_remover_maquina.clicked.connect(self.remover_maquina)
        botoes_maquina.addWidget(btn_maquina)
        botoes_maquina.addWidget(btn_remover_maquina)
        self.layout.addLayout(botoes_maquina)

    def build_back_button(self):
        btn_voltar = QPushButton("⬅️ Voltar")
        btn_voltar.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))
        self.layout.addWidget(btn_voltar)

    def validate_fields(self, fields):
        for field_name, field in fields:
            if not field.text().strip():
                QMessageBox.warning(self, "Erro", f"⚠️ Preencha o campo '{field_name}' corretamente!")
                return False
        return True

    def show_message(self, title, message, info=True):
        if info:
            QMessageBox.information(self, title, message)
        else:
            QMessageBox.warning(self, title, message)

    def adicionar_usuario(self):
        if not self.validate_fields([("Nome", self.nome_usuario_input),
                                     ("Senha", self.senha_usuario_input),
                                     ("RFID", self.rfid_usuario_input)]):
            return

        nome = self.nome_usuario_input.text().strip()
        senha = self.senha_usuario_input.text().strip()
        rfid = self.rfid_usuario_input.text().strip()
        tipo = self.tipo_usuario_input.currentText().strip()
        senha_hash = hash_senha(senha)

        ja_existe = executar_query("SELECT 1 FROM usuarios WHERE nome = ?", (nome,), fetch=True)
        if ja_existe:
            self.show_message("Erro", f"⚠️ Usuário '{nome}' já existe.", info=False)
            return

        try:
            resposta = registrar_usuario(nome, senha_hash, rfid, tipo)
        except Exception as e:
            self.show_message("Erro", f"Erro ao registrar usuário: {str(e)}", info=False)
            return

        if resposta.startswith("✅"):
            self.show_message("Sucesso", resposta)
            self.nome_usuario_input.clear()
            self.senha_usuario_input.clear()
            self.rfid_usuario_input.clear()
        else:
            self.show_message("Erro", resposta, info=False)

    def remover_usuario(self):
        nome = self.nome_usuario_input.text().strip()
        if not nome:
            self.show_message("Erro", "Informe o nome do usuário a ser removido.", info=False)
            return

        existe = executar_query("SELECT 1 FROM usuarios WHERE nome = ?", (nome,), fetch=True)
        if not existe:
            self.show_message("Erro", f"⚠️ Usuário '{nome}' não encontrado.", info=False)
            return

        executar_query("DELETE FROM usuarios WHERE nome = ?", (nome,))
        self.show_message("Sucesso", f"Usuário '{nome}' removido com sucesso.")

    def adicionar_ferramenta(self):
        if not self.validate_fields([("Nome", self.nome_ferramenta_input),
                                     ("Código de Barras", self.codigo_barra_input),
                                     ("Estoque Almoxarifado", self.quantidade_input)]):
            return

        nome = self.nome_ferramenta_input.text().strip()
        codigo = self.codigo_barra_input.text().strip()
        quantidade_str = self.quantidade_input.text().strip()

        if not quantidade_str.isdigit():
            self.show_message("Erro", "Estoque Almoxarifado deve ser um número inteiro.", info=False)
            return

        ja_existe = executar_query("SELECT 1 FROM ferramentas WHERE codigo_barra = ?", (codigo,), fetch=True)
        if ja_existe:
            self.show_message("Erro", f"⚠️ Ferramenta com código '{codigo}' já existe.", info=False)
            return

        quantidade = int(quantidade_str)
        estoque_ativo_str = self.estoque_ativo_input.text().strip()
        estoque_ativo = int(estoque_ativo_str) if estoque_ativo_str.isdigit() else 0
        consumivel = self.consumivel_input.currentText().strip()

        try:
            resposta = registrar_ferramenta(nome, codigo, quantidade, estoque_ativo, consumivel)
        except Exception as e:
            self.show_message("Erro", f"Erro ao registrar ferramenta: {str(e)}", info=False)
            return

        if resposta.startswith("✅"):
            self.show_message("Sucesso", resposta)
            self.nome_ferramenta_input.clear()
            self.codigo_barra_input.clear()
            self.quantidade_input.clear()
            self.estoque_ativo_input.clear()
        else:
            self.show_message("Erro", resposta, info=False)

    def remover_ferramenta(self):
        codigo = self.codigo_barra_input.text().strip()
        if not codigo:
            self.show_message("Erro", "Informe o código de barras da ferramenta a ser removida.", info=False)
            return

        existe = executar_query("SELECT 1 FROM ferramentas WHERE codigo_barra = ?", (codigo,), fetch=True)
        if not existe:
            self.show_message("Erro", f"⚠️ Ferramenta com código '{codigo}' não encontrada.", info=False)
            return

        executar_query("DELETE FROM ferramentas WHERE codigo_barra = ?", (codigo,))
        self.show_message("Sucesso", f"Ferramenta com código '{codigo}' removida com sucesso.")

    def adicionar_maquina(self):
        if not self.validate_fields([("Nome", self.nome_maquina_input)]):
            return

        nome = self.nome_maquina_input.text().strip()

        ja_existe = executar_query("SELECT 1 FROM maquinas WHERE nome = ?", (nome,), fetch=True)
        if ja_existe:
            self.show_message("Erro", f"⚠️ Máquina '{nome}' já existe.", info=False)
            return

        try:
            resposta = registrar_maquina(nome)
        except Exception as e:
            self.show_message("Erro", f"Erro ao registrar máquina: {str(e)}", info=False)
            return

        if resposta.startswith("✅"):
            self.show_message("Sucesso", resposta)
            self.nome_maquina_input.clear()
        else:
            self.show_message("Erro", resposta, info=False)

    def remover_maquina(self):
        nome = self.nome_maquina_input.text().strip()
        if not nome:
            self.show_message("Erro", "Informe o nome da máquina a ser removida.", info=False)
            return

        existe = executar_query("SELECT 1 FROM maquinas WHERE nome = ?", (nome,), fetch=True)
        if not existe:
            self.show_message("Erro", f"⚠️ Máquina '{nome}' não encontrada.", info=False)
            return

        executar_query("DELETE FROM maquinas WHERE nome = ?", (nome,))
        self.show_message("Sucesso", f"Máquina '{nome}' removida com sucesso.")
