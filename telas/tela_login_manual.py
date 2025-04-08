import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer, QDateTime, Qt

from database.config import DATABASE_CAMINHO
from database.database_utils import executar_query

class TelaLoginManual(QWidget):
    def __init__(self, navegacao, definir_perfil_callback):
        super().__init__()
        self.navegacao = navegacao
        self.definir_perfil_callback = definir_perfil_callback
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(self._criar_titulo())
        layout.addWidget(self._criar_label_data_hora())
        layout.addWidget(self._criar_label_banco())

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Nome do usuário")
        layout.addWidget(self.input_usuario)

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.setEchoMode(QLineEdit.Password)
        self.input_senha.returnPressed.connect(self.fazer_login)
        layout.addWidget(self.input_senha)

        self.botao_login = QPushButton("Entrar")
        self.botao_login.clicked.connect(self.fazer_login)
        layout.addWidget(self.botao_login)

        layout.addWidget(self._criar_botao_voltar())

        self.setLayout(layout)

    def _criar_titulo(self):
        label = QLabel("Login com Nome e Senha")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        return label

    def _criar_label_data_hora(self):
        self.label_data_hora = QLabel("")
        self.label_data_hora.setAlignment(Qt.AlignCenter)
        self.atualizar_data_hora()

        timer = QTimer(self)
        timer.timeout.connect(self.atualizar_data_hora)
        timer.start(1000)
        return self.label_data_hora

    def _criar_label_banco(self):
        label = QLabel(f"📂 Banco de dados atual: {os.path.basename(DATABASE_CAMINHO)}")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _criar_botao_voltar(self):
        btn = QPushButton("Voltar")
        btn.clicked.connect(self.voltar_tela_login)
        return btn

    def atualizar_data_hora(self):
        data_hora = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")
        self.label_data_hora.setText(f"Data e Hora: {data_hora}")

    def fazer_login(self):
        nome = self.input_usuario.text().strip()
        senha = self.input_senha.text().strip()

        if not nome or not senha:
            QMessageBox.warning(self, "Campos vazios", "Preencha todos os campos.")
            return

        query = "SELECT tipo, rfid FROM usuarios WHERE nome = ? AND senha = ?"
        resultado = executar_query(query, (nome, senha), fetch_one=True)

        if resultado:
            tipo, rfid = resultado
            self.definir_perfil_callback(tipo, rfid)
            self.navegacao.mostrar_tela("painel")
        else:
            QMessageBox.critical(self, "Erro de login", "Usuário ou senha inválidos.")

    def voltar_tela_login(self):
        self.navegacao.mostrar_tela("login")
