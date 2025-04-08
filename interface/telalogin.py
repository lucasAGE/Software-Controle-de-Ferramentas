import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, QDateTime, Qt

from database.config import DATABASE_CAMINHO

class TelaLogin(QWidget):
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
        layout.addWidget(self._criar_botao_login_rfid())
        layout.addWidget(self._criar_botao_login_manual())
        layout.addWidget(self._criar_botao_sair())

        self.setLayout(layout)

    def _criar_titulo(self):
        label = QLabel("Controle de Ferramentas")
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

    def _criar_botao_login_rfid(self):
        btn = QPushButton("Fazer login com cartão RFID")
        btn.setStyleSheet("font-size: 14pt; padding: 10px;")
        btn.clicked.connect(lambda: self.navegacao.mostrar_tela("login_rfid"))
        return btn

    def _criar_botao_login_manual(self):
        btn = QPushButton("Fazer login com nome e senha")
        btn.setStyleSheet("font-size: 14pt; padding: 10px;")
        btn.clicked.connect(lambda: self.navegacao.mostrar_tela("login_manual"))
        return btn

    def _criar_botao_sair(self):
        btn = QPushButton("Sair")
        btn.clicked.connect(self.fechar_app)
        return btn

    def atualizar_data_hora(self):
        data_hora = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")
        self.label_data_hora.setText(f"Data e Hora: {data_hora}")

    def fechar_app(self):
        self.navegacao.close()
