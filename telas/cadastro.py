import os
import sqlite3
import hashlib
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QMessageBox, QComboBox
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt

from main import registrar_usuario, registrar_ferramenta, registrar_maquina

def hash_senha(senha):
    """
    Gera um hash SHA-256 para a senha informada.
    Em produção, considere utilizar bibliotecas como o bcrypt.
    """
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
        """Constrói a seção de cadastro de usuários."""
        label_usuarios = QLabel("📅 Usuários")
        label_usuarios.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label_usuarios)

        # Criando os campos de cadastro de usuário
        self.nome_usuario_input = QLineEdit()
        self.senha_usuario_input = QLineEdit()
        self.senha_usuario_input.setEchoMode(QLineEdit.Password)
        self.rfid_usuario_input = QLineEdit()
        self.tipo_usuario_input = QComboBox()
        # Exemplo de tipos; ajuste conforme necessário
        self.tipo_usuario_input.addItems(["admin", "usuario"])

        form_usuario = QFormLayout()
        form_usuario.addRow("Nome:", self.nome_usuario_input)
        form_usuario.addRow("Senha:", self.senha_usuario_input)
        form_usuario.addRow("RFID:", self.rfid_usuario_input)
        form_usuario.addRow("Tipo:", self.tipo_usuario_input)
        self.layout.addLayout(form_usuario)

        btn_usuario = QPushButton("Adicionar Usuário")
        btn_usuario.clicked.connect(self.adicionar_usuario)
        self.layout.addWidget(btn_usuario)

    def build_tool_section(self):
        """Constrói a seção de cadastro de ferramentas."""
        label_ferramentas = QLabel("🔧 Ferramentas")
        label_ferramentas.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label_ferramentas)

        self.nome_ferramenta_input = QLineEdit()
        self.codigo_barra_input = QLineEdit()
        self.quantidade_input = QLineEdit()
        self.quantidade_input.setValidator(QIntValidator(0, 10000, self))

        # Novos campos para refletir a estrutura do banco
        self.estoque_ativo_input = QLineEdit()
        self.estoque_ativo_input.setValidator(QIntValidator(0, 10000, self))
        self.estoque_ativo_input.setPlaceholderText("Opcional (default: 0)")

        self.consumivel_input = QComboBox()
        self.consumivel_input.addItems(["NÃO", "SIM"])  # Padrão é "NÃO"

        form_ferramenta = QFormLayout()
        form_ferramenta.addRow("Nome:", self.nome_ferramenta_input)
        form_ferramenta.addRow("Código de Barras:", self.codigo_barra_input)
        form_ferramenta.addRow("Quantidade:", self.quantidade_input)
        form_ferramenta.addRow("Estoque Ativo:", self.estoque_ativo_input)
        form_ferramenta.addRow("Consumível:", self.consumivel_input)
        self.layout.addLayout(form_ferramenta)

        btn_ferramenta = QPushButton("Adicionar Ferramenta")
        btn_ferramenta.clicked.connect(self.adicionar_ferramenta)
        self.layout.addWidget(btn_ferramenta)

    def build_machine_section(self):
        """Constrói a seção de cadastro de máquinas."""
        label_maquinas = QLabel("🛠️ Máquinas")
        label_maquinas.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label_maquinas)

        self.nome_maquina_input = QLineEdit()
        # Se o campo "localizacao" não for necessário, ele não aparece no cadastro.
        form_maquina = QFormLayout()
        form_maquina.addRow("Nome:", self.nome_maquina_input)
        self.layout.addLayout(form_maquina)

        btn_maquina = QPushButton("Adicionar Máquina")
        btn_maquina.clicked.connect(self.adicionar_maquina)
        self.layout.addWidget(btn_maquina)

    def build_back_button(self):
        """Cria o botão para retornar à tela anterior."""
        btn_voltar = QPushButton("⬅️ Voltar")
        btn_voltar.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))
        self.layout.addWidget(btn_voltar)

    def validate_fields(self, fields):
        """
        Valida os campos informados.
        fields: lista de tuplas (nome_do_campo, QLineEdit)
        """
        for field_name, field in fields:
            if not field.text().strip():
                QMessageBox.warning(self, "Erro", f"⚠️ Preencha o campo '{field_name}' corretamente!")
                return False
        return True

    def show_message(self, title, message, info=True):
        """Exibe uma mensagem de sucesso ou de erro."""
        if info:
            QMessageBox.information(self, title, message)
        else:
            QMessageBox.warning(self, title, message)

    def adicionar_usuario(self):
        # Valida os campos obrigatórios (nome, senha e RFID)
        if not self.validate_fields([("Nome", self.nome_usuario_input),
                                     ("Senha", self.senha_usuario_input),
                                     ("RFID", self.rfid_usuario_input)]):
            return

        nome = self.nome_usuario_input.text().strip()
        senha = self.senha_usuario_input.text().strip()
        rfid = self.rfid_usuario_input.text().strip()
        tipo = self.tipo_usuario_input.currentText().strip()

        # Aplica hash na senha antes de registrar
        senha_hash = hash_senha(senha)

        try:
            # Registrar usuário com os quatro parâmetros: nome, senha_hash, rfid e tipo
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

    def adicionar_ferramenta(self):
        # Valida os campos obrigatórios para ferramentas
        if not self.validate_fields([("Nome", self.nome_ferramenta_input),
                                     ("Código de Barras", self.codigo_barra_input),
                                     ("Quantidade", self.quantidade_input)]):
            return

        nome = self.nome_ferramenta_input.text().strip()
        codigo = self.codigo_barra_input.text().strip()
        quantidade_str = self.quantidade_input.text().strip()

        if not quantidade_str.isdigit():
            self.show_message("Erro", "Quantidade deve ser um número inteiro.", info=False)
            return

        quantidade = int(quantidade_str)

        # Para estoque_ativo: se não informado, usa 0
        estoque_ativo_str = self.estoque_ativo_input.text().strip()
        estoque_ativo = int(estoque_ativo_str) if estoque_ativo_str.isdigit() else 0
        consumivel = self.consumivel_input.currentText().strip()

        try:
            # Registrar ferramenta com os cinco parâmetros
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

    def adicionar_maquina(self):
        # Valida o campo obrigatório para máquina (apenas nome)
        if not self.validate_fields([("Nome", self.nome_maquina_input)]):
            return

        nome = self.nome_maquina_input.text().strip()

        try:
            # Registrar máquina usando somente o nome, já que o campo localização foi removido
            resposta = registrar_maquina(nome)
        except Exception as e:
            self.show_message("Erro", f"Erro ao registrar máquina: {str(e)}", info=False)
            return

        if resposta.startswith("✅"):
            self.show_message("Sucesso", resposta)
            self.nome_maquina_input.clear()
        else:
            self.show_message("Erro", resposta, info=False)

