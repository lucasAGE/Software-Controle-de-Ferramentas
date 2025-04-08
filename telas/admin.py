from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QLineEdit, QFormLayout, QMessageBox
)
from PyQt5.QtGui import QFont, QIntValidator
from PyQt5.QtCore import Qt

from main import registrar_usuario, registrar_ferramenta, registrar_maquina



class Admin(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Administrador")
        # Removemos a geometria fixa pois vamos usar tela cheia
        # self.setGeometry(200, 200, 400, 350)

        # Define uma fonte padrão maior para todos os widgets
        self.setFont(QFont("Arial", 14))
        
        main_layout = QVBoxLayout()

        # Criação das seções de usuários, máquinas e ferramentas
        self.build_user_section(main_layout)
        self.build_machine_section(main_layout)
        self.build_tool_section(main_layout)

        self.setLayout(main_layout)
        # Exibe a janela maximizada (modo full-screen)
        self.showMaximized()

    def build_user_section(self, layout):
        """Cria a seção de gerenciamento de usuários."""
        label_usuarios = QLabel("🔹 Gerenciar Usuários")
        label_usuarios.setAlignment(Qt.AlignCenter)
        label_usuarios.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(label_usuarios)

        self.nome_usuario_input = QLineEdit()
        self.rfid_input = QLineEdit()

        form_usuarios = QFormLayout()
        form_usuarios.addRow("Nome:", self.nome_usuario_input)
        form_usuarios.addRow("RFID:", self.rfid_input)
        layout.addLayout(form_usuarios)

        adicionar_usuario_btn = QPushButton("Adicionar Usuário")
        adicionar_usuario_btn.clicked.connect(self.adicionar_usuario)
        layout.addWidget(adicionar_usuario_btn)

    def build_machine_section(self, layout):
        """Cria a seção de gerenciamento de máquinas."""
        label_maquinas = QLabel("🔹 Gerenciar Máquinas")
        label_maquinas.setAlignment(Qt.AlignCenter)
        label_maquinas.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(label_maquinas)

        self.nome_maquina_input = QLineEdit()

        form_maquinas = QFormLayout()
        form_maquinas.addRow("Nome:", self.nome_maquina_input)
        layout.addLayout(form_maquinas)

        adicionar_maquina_btn = QPushButton("Adicionar Máquina")
        adicionar_maquina_btn.clicked.connect(self.adicionar_maquina)
        layout.addWidget(adicionar_maquina_btn)

    def build_tool_section(self, layout):
        """Cria a seção de gerenciamento de ferramentas."""
        label_ferramentas = QLabel("🔹 Gerenciar Ferramentas")
        label_ferramentas.setAlignment(Qt.AlignCenter)
        label_ferramentas.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(label_ferramentas)

        self.nome_ferramenta_input = QLineEdit()
        self.codigo_barra_input = QLineEdit()
        self.quantidade_input = QLineEdit()
        # Validador para garantir que o valor seja um inteiro válido
        self.quantidade_input.setValidator(QIntValidator(0, 10000, self))

        form_ferramentas = QFormLayout()
        form_ferramentas.addRow("Nome:", self.nome_ferramenta_input)
        form_ferramentas.addRow("Código de Barra:", self.codigo_barra_input)
        form_ferramentas.addRow("Quantidade:", self.quantidade_input)
        layout.addLayout(form_ferramentas)

        adicionar_ferramenta_btn = QPushButton("Adicionar Ferramenta")
        adicionar_ferramenta_btn.clicked.connect(self.adicionar_ferramenta)
        layout.addWidget(adicionar_ferramenta_btn)

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
        """Exibe mensagem de informação ou alerta."""
        if info:
            QMessageBox.information(self, title, message)
        else:
            QMessageBox.warning(self, title, message)

    def adicionar_usuario(self):
        if not self.validate_fields([("Nome", self.nome_usuario_input), ("RFID", self.rfid_input)]):
            return

        nome = self.nome_usuario_input.text().strip()
        rfid = self.rfid_input.text().strip()

        try:
            resposta = registrar_usuario(nome, rfid)
        except Exception as e:
            self.show_message("Erro", f"Erro ao registrar usuário: {str(e)}", info=False)
            return

        if resposta.startswith("✅"):
            self.show_message("Sucesso", resposta)
            self.nome_usuario_input.clear()
            self.rfid_input.clear()
        else:
            self.show_message("Erro", resposta, info=False)

    def adicionar_maquina(self):
        if not self.validate_fields([("Nome", self.nome_maquina_input)]):
            return

        nome = self.nome_maquina_input.text().strip()

        try:
            resposta = registrar_maquina(nome, "ignorado")  # Localização eliminada
        except Exception as e:
            self.show_message("Erro", f"Erro ao registrar máquina: {str(e)}", info=False)
            return

        if resposta.startswith("✅"):
            self.show_message("Sucesso", resposta)
            self.nome_maquina_input.clear()
        else:
            self.show_message("Erro", resposta, info=False)

    def adicionar_ferramenta(self):
        if not self.validate_fields([("Nome", self.nome_ferramenta_input),
                                     ("Código de Barra", self.codigo_barra_input),
                                     ("Quantidade", self.quantidade_input)]):
            return

        nome = self.nome_ferramenta_input.text().strip()
        codigo_barra = self.codigo_barra_input.text().strip()
        quantidade_str = self.quantidade_input.text().strip()

        # A validação de quantidade é reforçada pelo QIntValidator, mas checamos para garantir
        if not quantidade_str.isdigit():
            self.show_message("Erro", "⚠️ A quantidade deve ser um número válido!", info=False)
            return

        quantidade = int(quantidade_str)

        try:
            resposta = registrar_ferramenta(nome, codigo_barra, quantidade)
        except Exception as e:
            self.show_message("Erro", f"Erro ao registrar ferramenta: {str(e)}", info=False)
            return

        if resposta.startswith("✅"):
            self.show_message("Sucesso", resposta)
            self.nome_ferramenta_input.clear()
            self.codigo_barra_input.clear()
            self.quantidade_input.clear()
        else:
            self.show_message("Erro", resposta, info=False)
