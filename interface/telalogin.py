import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer, QDateTime, Qt

import database.config as config

class TelaLogin(QWidget):
    BTN_STYLE = "font-size:14pt; padding:10px;"

    def __init__(self, navegacao, definir_perfil_callback) -> None:
        super().__init__()
        self.navegacao = navegacao
        self.definir_perfil_callback = definir_perfil_callback

        # Ajuste: inicia o relógio antes de construir a UI
        self._start_clock()

        self.database_file = config.DATABASE_CAMINHO
        if not os.path.exists(self.database_file):
            QMessageBox.warning(self, "Backup", "Banco de dados não encontrado.")

        # Agora self.label_data_hora já existe
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        layout.addWidget(self._criar_titulo())
        layout.addWidget(self.label_data_hora)         # OK
        layout.addWidget(self._criar_label_banco())
        layout.addWidget(self._criar_botao("login_rfid", "Fazer login com cartão RFID"))
        layout.addWidget(self._criar_botao("login_manual", "Fazer login com nome e senha"))
        layout.addWidget(self._criar_botao_sair())

        self.setLayout(layout)

    def _criar_titulo(self) -> QLabel:
        label = QLabel("Controle de Ferramentas")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size:18pt; font-weight:bold;")
        return label

    def _start_clock(self) -> None:
        # Cria o label e o timer antes da UI
        self.label_data_hora = QLabel()
        self.label_data_hora.setAlignment(Qt.AlignCenter)
        self.atualizar_data_hora()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.atualizar_data_hora)
        self.timer.start(1000)

    def atualizar_data_hora(self) -> None:
        agora = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")
        self.label_data_hora.setText(f"Data e Hora: {agora}")

    def _criar_label_banco(self) -> QLabel:
        nome = os.path.basename(self.database_file)
        label = QLabel(f"📂 Banco de Dados atual: {nome}")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _criar_botao(self, tela: str, texto: str) -> QPushButton:
        btn = QPushButton(texto)
        btn.setStyleSheet(self.BTN_STYLE)
        btn.clicked.connect(lambda: self.navegacao.mostrar_tela(tela))
        return btn

    def _criar_botao_sair(self) -> QPushButton:
        btn = QPushButton("Sair")
        btn.clicked.connect(self.fechar_app)
        return btn

    def fechar_app(self) -> None:
        self.timer.stop()
        self.navegacao.close()

    def closeEvent(self, event) -> None:
        self.timer.stop()
        super().closeEvent(event)
