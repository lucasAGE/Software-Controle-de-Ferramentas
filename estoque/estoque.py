from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QFormLayout, QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator

from main import adicionar_ferramenta, subtrair_ferramenta, zerar_ferramenta
from database.database import buscar_ferramenta_por_codigo, buscar_ultimas_movimentacoes


class TelaEstoque(QWidget):
    """
    Tela para gerenciamento de estoque:
      - ADICAO (➕)
      - SUBTRACAO parcial (➖)
      - ZERAR estoque (🗑️)
    Mostra descrição, valores atuais e histórico de movimentações.
    """
    def __init__(self, navegacao):
        """
        :param navegacao: instância de Navegacao, que mantém rfid_usuario atualizado
        """
        super().__init__()
        self.navegacao = navegacao
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()

        # Título
        lbl_title = QLabel("Gerenciamento de Estoque")
        lbl_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_title)

        # Formulário código + quantidade
        form = QFormLayout()
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código de barras")
        self.codigo_input.returnPressed.connect(self._on_codigo_enter)

        self.qtde_input = QLineEdit()
        self.qtde_input.setPlaceholderText("Quantidade")
        self.qtde_input.setValidator(QIntValidator(1, 1_000_000, self))

        form.addRow("Código:", self.codigo_input)
        form.addRow("Quantidade:", self.qtde_input)
        layout.addLayout(form)

        # Labels descrição e estoque
        self.lbl_descricao = QLabel("🔎 Descrição: -")
        self.lbl_estoque   = QLabel("📦 Almoxarifado: - | Ativo: -")
        layout.addWidget(self.lbl_descricao)
        layout.addWidget(self.lbl_estoque)

        # Tabela histórico
        layout.addWidget(QLabel("📜 Últimas Movimentações:"))
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "Data/Hora", "Operador", "Código", "Descrição", "Tipo",
            "Qtd", "Motivo", "Operações", "Avaliação"
        ])
        layout.addWidget(self.tabela)

        # Botões
        btn_add  = QPushButton("➕ Adicionar Estoque")
        btn_add.clicked.connect(self.adicionar)

        btn_sub  = QPushButton("➖ Subtrair Estoque")
        btn_sub.clicked.connect(self.subtrair)

        btn_zero = QPushButton("🗑️ Zerar Estoque")
        btn_zero.clicked.connect(self.zerar)

        btn_back = QPushButton("⬅️ Voltar")
        btn_back.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))

        for btn in (btn_add, btn_sub, btn_zero, btn_back):
            layout.addWidget(btn)

        self.setLayout(layout)
        self.codigo_input.setFocus()
        self._refresh_history()

    def _get_rfid(self):
        """Retorna o RFID atual; exibe erro se não estiver definido."""
        rfid = getattr(self.navegacao, "rfid_usuario", None)
        if not rfid:
            QMessageBox.warning(self, "Erro", "⚠️ Usuário não identificado.")
        return rfid

    def adicionar(self):
        """Executa ADICAO via adicionar_ferramenta."""
        rfid = self._get_rfid()
        if not rfid:
            return

        cod = self.codigo_input.text().strip()
        qt  = self.qtde_input.text().strip()
        if not cod:
            return self._msg("Erro", "Informe o código da ferramenta.", "warning")
        if not qt:
            return self._msg("Erro", "Informe a quantidade.", "warning")
        try:
            q = int(qt)
        except ValueError:
            return self._msg("Erro", "Quantidade inválida.", "warning")

        resp = adicionar_ferramenta(rfid, cod, q)
        if resp.startswith("✅"):
            self._msg("Sucesso", resp, "info")
            self._clear_all()
            self._refresh_history()
        else:
            self._msg("Erro", resp, "warning")

    def subtrair(self):
        """Executa SUBTRACAO parcial via subtrair_ferramenta."""
        rfid = self._get_rfid()
        if not rfid:
            return

        cod = self.codigo_input.text().strip()
        qt  = self.qtde_input.text().strip()
        if not cod:
            return self._msg("Erro", "Informe o código da ferramenta.", "warning")
        if not qt:
            return self._msg("Erro", "Informe a quantidade.", "warning")
        try:
            q = int(qt)
        except ValueError:
            return self._msg("Erro", "Quantidade inválida.", "warning")

        resp = subtrair_ferramenta(rfid, cod, q)
        if resp.startswith("✅"):
            self._msg("Sucesso", resp, "info")
            self._clear_all()
            self._refresh_history()
        else:
            self._msg("Erro", resp, "warning")

    def zerar(self):
        """Executa ZERAR estoque via zerar_ferramenta."""
        rfid = self._get_rfid()
        if not rfid:
            return

        cod = self.codigo_input.text().strip()
        if not cod:
            return self._msg("Erro", "Informe o código da ferramenta.", "warning")

        resp = zerar_ferramenta(rfid, cod)
        if resp.startswith("✅"):
            self._msg("Sucesso", resp, "info")
            self._clear_all()
            self._refresh_history()
        else:
            self._msg("Erro", resp, "warning")

    def _on_codigo_enter(self):
        """Ao pressionar Enter no código, busca dados e atualiza histórico."""
        cod = self.codigo_input.text().strip()
        if not cod:
            self._clear_labels()
        else:
            dados = buscar_ferramenta_por_codigo(cod)
            if dados:
                self.lbl_descricao.setText(f"🔎 Descrição: {dados['nome']}")
                self.lbl_estoque.setText(
                    f"📦 Almoxarifado: {dados['estoque_almoxarifado']} | Ativo: {dados['estoque_ativo']}"
                )
            else:
                QMessageBox.warning(self, "Erro", "Ferramenta não encontrada.")
                self._clear_labels()
        self._refresh_history()

    def _refresh_history(self):
        """Recarrega a tabela com as últimas movimentações."""
        registros = buscar_ultimas_movimentacoes()
        self.tabela.setRowCount(0)
        for linha in registros:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, val in enumerate(linha):
                self.tabela.setItem(row, col, QTableWidgetItem(str(val)))

    def _clear_all(self):
        """Limpa campos de entrada e labels."""
        self.codigo_input.clear()
        self.qtde_input.clear()
        self._clear_labels()

    def _clear_labels(self):
        """Reseta labels de descrição e estoque."""
        self.lbl_descricao.setText("🔎 Descrição: -")
        self.lbl_estoque.setText("📦 Almoxarifado: - | Ativo: -")

    def _msg(self, title, text, kind="info"):
        """Exibe QMessageBox de informação ou alerta."""
        if kind == "info":
            QMessageBox.information(self, title, text)
        else:
            QMessageBox.warning(self, title, text)
