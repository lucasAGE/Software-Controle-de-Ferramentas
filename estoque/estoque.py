from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

from main import dar_alta_ferramenta, dar_baixa_ferramenta

class TelaEstoque(QWidget):
    def __init__(self, navegacao):
        """
        Inicializa a tela de gerenciamento de estoque.
        
        Parâmetros:
            navegacao: objeto responsável pela navegação entre telas.
        """
        super().__init__()
        self.navegacao = navegacao
        self.init_ui()

    def init_ui(self):
        """
        Configura a interface do usuário, incluindo a criação do título, formulário e botões.
        """
        layout = QVBoxLayout()
        layout.addWidget(self._criar_label_titulo())
        layout.addLayout(self._criar_formulario())
        layout.addWidget(self._criar_botao_adicionar())
        layout.addWidget(self._criar_botao_remover())
        layout.addWidget(self._criar_botao_voltar())
        self.setLayout(layout)

    def _criar_label_titulo(self):
        """
        Cria e retorna o rótulo do título centralizado.
        """
        label_titulo = QLabel("Gerenciamento de Estoque")
        label_titulo.setAlignment(Qt.AlignCenter)
        return label_titulo

    def _criar_formulario(self):
        """
        Cria o formulário com os campos de entrada para o código de barras e quantidade.
        Utiliza QIntValidator para garantir que a quantidade seja numérica.
        """
        # Campo: Código de barras
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código de barras da ferramenta")
        
        # Campo: Quantidade a adicionar com validador numérico
        self.quantidade_input = QLineEdit()
        self.quantidade_input.setPlaceholderText("Quantidade a adicionar")
        self.quantidade_input.setValidator(QIntValidator(1, 10000, self))  # Exemplo de range de 1 a 10000
        
        form = QFormLayout()
        form.addRow("Código de Barras:", self.codigo_input)
        form.addRow("Quantidade:", self.quantidade_input)
        return form

    def _criar_botao_adicionar(self):
        """
        Cria e retorna o botão para adicionar quantidade ao estoque.
        """
        btn_adicionar = QPushButton("➕ Adicionar ao Estoque")
        btn_adicionar.clicked.connect(self.adicionar_estoque)
        return btn_adicionar

    def _criar_botao_remover(self):
        """
        Cria e retorna o botão para zerar o estoque da ferramenta.
        """
        btn_remover = QPushButton("🗑️ Zerar Estoque da Ferramenta")
        btn_remover.clicked.connect(self.remover_estoque)
        return btn_remover

    def _criar_botao_voltar(self):
        """
        Cria e retorna o botão para retornar à tela anterior.
        """
        btn_voltar = QPushButton("⬅️ Voltar")
        btn_voltar.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))
        return btn_voltar

    def _limpar_campos(self):
        """
        Limpa os campos de entrada da tela.
        """
        self.codigo_input.clear()
        self.quantidade_input.clear()

    def _exibir_mensagem(self, titulo, mensagem, tipo="info"):
        """
        Exibe uma mensagem para o usuário.
        
        Parâmetros:
            titulo (str): Título da mensagem.
            mensagem (str): Conteúdo da mensagem.
            tipo (str): Tipo da mensagem ('info' ou 'warning').
        """
        if tipo == "info":
            QMessageBox.information(self, titulo, mensagem)
        elif tipo == "warning":
            QMessageBox.warning(self, titulo, mensagem)

    def adicionar_estoque(self):
        """
        Valida os campos e processa a adição de quantidade ao estoque.
        Chama a função dar_alta_ferramenta e exibe a mensagem correspondente.
        """
        codigo = self.codigo_input.text().strip()
        qtd_text = self.quantidade_input.text().strip()

        if not codigo:
            self._exibir_mensagem("Erro", "Informe o código de barras da ferramenta.", "warning")
            return

        if not qtd_text:
            self._exibir_mensagem("Erro", "Informe a quantidade a adicionar.", "warning")
            return

        try:
            qtd = int(qtd_text)
        except ValueError:
            self._exibir_mensagem("Erro", "A quantidade deve ser um número válido.", "warning")
            return

        try:
            resposta = dar_alta_ferramenta(codigo, qtd)
            if isinstance(resposta, str) and resposta.startswith("✅"):
                self._exibir_mensagem("Sucesso", resposta, "info")
                self._limpar_campos()
            else:
                self._exibir_mensagem("Erro", resposta, "warning")
        except Exception as e:
            self._exibir_mensagem("Erro", f"Erro ao adicionar ao estoque: {e}", "warning")

    def remover_estoque(self):
        """
        Valida o campo de código e processa a remoção (zerar) do estoque de uma ferramenta.
        Chama a função dar_baixa_ferramenta e exibe a mensagem correspondente.
        """
        codigo = self.codigo_input.text().strip()
        if not codigo:
            self._exibir_mensagem("Erro", "Informe o código de barras da ferramenta.", "warning")
            return

        try:
            resposta = dar_baixa_ferramenta(codigo)
            if isinstance(resposta, str) and resposta.startswith("✅"):
                self._exibir_mensagem("Sucesso", resposta, "info")
                self._limpar_campos()
            else:
                self._exibir_mensagem("Erro", resposta, "warning")
        except Exception as e:
            self._exibir_mensagem("Erro", f"Erro ao remover do estoque: {e}", "warning")
