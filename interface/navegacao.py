from PyQt5.QtWidgets import QStackedWidget

from interface.telalogin import TelaLogin
from interface.painel import PainelPrincipal
from telas.movimentacao import TelaMovimentacao
from telas.admin import Admin
from telas.exportacao import TelaExportacao
from telas.cadastro import TelaCadastros
from estoque.estoque import TelaEstoque
from telas.tela_login_rfid import TelaLoginRFID
from telas.tela_login_manual import TelaLoginManual  # <- nova tela importada


class Navegacao(QStackedWidget):
    """Gerencia a navegação entre telas no sistema."""

    def __init__(self):
        super().__init__()
        self.telas = {}
        self.perfil_atual = None
        self.rfid_usuario = None

        try:
            self._inicializar_telas()
            self.mostrar_tela("login")  # Inicia na tela de login
        except Exception as e:
            print(f"❌ Erro ao carregar as telas: {e}")

    def _inicializar_telas(self):
        """Inicializa e registra as telas do sistema."""
        self.telas = {
            "login": TelaLogin(self, self.definir_perfil),
            "login_rfid": TelaLoginRFID(self, self.definir_perfil),
            "login_manual": TelaLoginManual(self, self.definir_perfil),  # <- nova tela registrada
            "painel": PainelPrincipal(self),
            "export": TelaExportacao(self),
            "cadastro": TelaCadastros(self),
            "estoque": TelaEstoque(self),
            "admin": Admin()
        }
        for tela in self.telas.values():
            self.addWidget(tela)

    def mostrar_tela(self, nome_tela, rfid_usuario=None):
        """
        Exibe a tela especificada.

        Se a tela 'movimentacao' for solicitada, ela é criada dinamicamente utilizando o RFID do usuário.
        
        Parâmetros:
            nome_tela (str): Nome da tela a ser exibida.
            rfid_usuario (str, opcional): RFID do usuário, se necessário.
        """
        if nome_tela == "movimentacao":
            if rfid_usuario:
                self.rfid_usuario = rfid_usuario
            self.telas["movimentacao"] = TelaMovimentacao(self, self.rfid_usuario)
            self.addWidget(self.telas["movimentacao"])

        if nome_tela in self.telas:
            if hasattr(self.telas[nome_tela], "atualizar_tela"):
                self.telas[nome_tela].atualizar_tela()
            self.setCurrentWidget(self.telas[nome_tela])
            print(f"📌 Mudando para a tela: {nome_tela}")
        else:
            print(f"⚠️ Erro: Tela '{nome_tela}' não encontrada!")

    def definir_perfil(self, perfil, rfid_usuario):
        """
        Define o perfil do usuário e atualiza a tela do painel conforme o perfil.

        Parâmetros:
            perfil (str): Perfil do usuário (ex: 'admin' ou 'operador').
            rfid_usuario (str): RFID do usuário.
        """
        self.perfil_atual = perfil
        self.rfid_usuario = rfid_usuario
        if "painel" in self.telas:
            self.telas["painel"].configurar_por_perfil(perfil)
