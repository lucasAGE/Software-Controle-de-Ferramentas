from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget

from interface.telalogin import TelaLogin
from interface.painel import PainelPrincipal
from telas.movimentacao import TelaMovimentacao


class InterfaceGrafica(QWidget):
    """
    Interface principal do sistema de Controle de Ferramentas.
    
    Gerencia a navegação entre as diferentes telas (login, painel, movimentação)
    utilizando um QStackedWidget para manter a consistência e organização da interface.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Ferramentas")
        self.setGeometry(100, 100, 500, 400)

        self.perfil_atual = None  # Pode ser 'admin' ou 'operador'
        self.stacked_widget = QStackedWidget()
        
        # Configuração do layout principal
        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)

        self._inicializar_telas()
        self.mostrar_tela("login")

    def _inicializar_telas(self):
        """
        Inicializa e registra as telas do sistema.
        
        As telas são armazenadas em um dicionário para facilitar a navegação.
        """
        self.tela_login = TelaLogin(self, self.definir_perfil)
        self.tela_painel = PainelPrincipal(self)
        self.tela_movimentacao = TelaMovimentacao(self)

        self.telas = {
            "login": self.tela_login,
            "painel": self.tela_painel,
            "movimentacao": self.tela_movimentacao
        }

        for tela in self.telas.values():
            self.stacked_widget.addWidget(tela)

    def mostrar_tela(self, nome: str):
        """
        Exibe a tela correspondente ao nome informado.
        
        Parâmetros:
            nome (str): Chave que identifica a tela a ser exibida.
        """
        tela = self.telas.get(nome)
        if tela:
            self.stacked_widget.setCurrentWidget(tela)
        else:
            print(f"[ERRO] Tela '{nome}' não encontrada.")

    def definir_perfil(self, perfil: str):
        """
        Define o perfil atual do usuário e configura o painel de acordo.
        
        Parâmetros:
            perfil (str): Perfil do usuário, por exemplo, 'admin' ou 'operador'.
        """
        self.perfil_atual = perfil
        self.tela_painel.configurar_por_perfil(perfil)
