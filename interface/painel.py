from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt

class PainelPrincipal(QWidget):
    """
    Painel principal do sistema, exibindo as opções de navegação de acordo com o perfil do usuário.
    """
    def __init__(self, navegacao):
        """
        Inicializa o painel principal.
        
        Parâmetros:
            navegacao: Objeto responsável pela navegação entre telas.
        """
        super().__init__()
        self.navegacao = navegacao
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def configurar_por_perfil(self, perfil):
        """
        Configura o painel de acordo com o perfil do usuário.
        
        Parâmetros:
            perfil (str): Perfil do usuário, por exemplo, 'admin' ou 'operador'.
        """
        self._limpar_layout()

        # Título do painel
        titulo = "Painel do Administrador" if perfil == "admin" else "Painel do Operador"
        self._adicionar_botao(titulo, comando=None, enabled=False, estilo="font-weight: bold; font-size: 14pt;")
        
        # Ações comuns
        self._adicionar_botao("Movimentar Ferramentas", comando=lambda: self.navegacao.mostrar_tela("movimentacao"))
        self._adicionar_botao("Exportar Dados", comando=lambda: self.navegacao.mostrar_tela("export"))
        
        # Ações exclusivas do administrador
        if perfil == "admin":
            self._adicionar_botao("Cadastrar Itens", comando=lambda: self.navegacao.mostrar_tela("cadastro"))
            self._adicionar_botao("Alterar Estoque", comando=lambda: self.navegacao.mostrar_tela("estoque"))
        
        # Botão de logout
        self._adicionar_botao("Sair para Login", comando=lambda: self.navegacao.mostrar_tela("login"))

    def _limpar_layout(self):
        """
        Remove todos os widgets do layout atual para que o painel seja reconfigurado.
        """
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def _adicionar_botao(self, texto, comando=None, enabled=True, estilo=None):
        """
        Cria e adiciona um botão ao layout do painel.
        
        Parâmetros:
            texto (str): Texto do botão.
            comando (callable, opcional): Função a ser executada ao clicar no botão.
            enabled (bool, opcional): Define se o botão estará habilitado.
            estilo (str, opcional): Estilo CSS a ser aplicado ao botão.
        """
        botao = QPushButton(texto)
        botao.setEnabled(enabled)
        if estilo:
            botao.setStyleSheet(estilo)
        if comando:
            botao.clicked.connect(comando)
        self.layout.addWidget(botao)
