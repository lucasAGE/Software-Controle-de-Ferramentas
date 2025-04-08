from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QMessageBox, QLineEdit, QPushButton
from PyQt5.QtCore import QDateTime, Qt
import os
from database.config import DATABASE_CAMINHO
from database.database_utils import executar_query

class TelaLoginRFID(QWidget):
    def __init__(self, navegacao, definir_perfil_callback):
        super().__init__()
        self.navegacao = navegacao
        self.definir_perfil_callback = definir_perfil_callback
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Título
        label_titulo = QLabel("Leitor de Cartão RFID")
        label_titulo.setAlignment(Qt.AlignCenter)
        label_titulo.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(label_titulo)

        # Data/Hora
        self.label_data_hora = QLabel("")
        self.label_data_hora.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_data_hora)
        self.atualizar_data_hora()
        from PyQt5.QtCore import QTimer
        timer = QTimer(self)
        timer.timeout.connect(self.atualizar_data_hora)
        timer.start(1000)

        # Informação do banco de dados
        label_banco = QLabel(f"📂 Banco de dados atual: {os.path.basename(DATABASE_CAMINHO)}")
        label_banco.setAlignment(Qt.AlignCenter)
        layout.addWidget(label_banco)

        # Instrução para o usuário
        self.label_instrucao = QLabel("Aproxime seu cartão RFID...")
        self.label_instrucao.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label_instrucao)

        # QLineEdit para capturar a entrada do leitor (keyboard wedge)
        self.input_rfid = QLineEdit()
        self.input_rfid.setPlaceholderText("Aproxime o cartão RFID...")
        self.input_rfid.setAlignment(Qt.AlignCenter)
        # Ao receber o Enter, processa a entrada
        self.input_rfid.returnPressed.connect(self.processar_entrada)
        layout.addWidget(self.input_rfid)

        # Botão Voltar
        btn_voltar = QPushButton("Voltar")
        btn_voltar.clicked.connect(self.voltar_tela_login)
        layout.addWidget(btn_voltar)

        self.setLayout(layout)

    def processar_entrada(self):
        """
        Processa o código RFID recebido via QLineEdit.
        """
        rfid_code = self.input_rfid.text().strip()
        if not rfid_code:
            return

        # Limpa o campo para permitir nova leitura, se necessário
        self.input_rfid.clear()

        # Consulta o banco de dados para verificar o usuário
        query = "SELECT tipo, nome FROM usuarios WHERE rfid = ?"
        resultado = executar_query(query, (rfid_code,), fetch_one=True)

        if resultado:
            tipo, nome = resultado
            print(f"Usuário encontrado: {nome} (Tipo: {tipo})")
            self.definir_perfil_callback(tipo, rfid_code)
            self.navegacao.mostrar_tela("painel")
        else:
            QMessageBox.warning(self, "RFID não encontrado",
                                f"O cartão {rfid_code} não está cadastrado.")
            # Recoloca o foco no campo para nova tentativa
            self.input_rfid.setFocus()

    def atualizar_data_hora(self):
        data_hora = QDateTime.currentDateTime().toString("dd/MM/yyyy HH:mm:ss")
        self.label_data_hora.setText(f"Data e Hora: {data_hora}")

    def showEvent(self, event):
        """
        Garante que o QLineEdit receba o foco quando a tela é exibida.
        """
        super().showEvent(event)
        self.input_rfid.setFocus()

    def voltar_tela_login(self):
        self.navegacao.mostrar_tela("login")
