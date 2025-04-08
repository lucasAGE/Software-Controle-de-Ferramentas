from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout, 
    QMessageBox, QSpinBox, QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt

from main import realizar_movimentacao
from database.database import buscar_ferramenta_por_codigo, buscar_ultimas_movimentacoes


class DialogoConsumo(QDialog):
    """
    Popup para registrar os dados adicionais no consumo de um item consumível.
    Agora o motivo é escolhido entre opções fixas.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar Consumo")
        self.setModal(True)
        self.motivo_selecionado = None
        self.init_ui()

    def init_ui(self):
        self.layout = QFormLayout(self)

        # Botões para motivo
        self.motivos = {
            "Desgaste Natural": QPushButton("🟢 Desgaste Natural"),
            "Quebra Prematura": QPushButton("🔴 Quebra Prematura"),
            "Erro de Fundição": QPushButton("🟡 Erro de Fundição"),
            "Uso Incorreto": QPushButton("🔵 Uso Incorreto")
        }

        for motivo, botao in self.motivos.items():
            botao.setCheckable(True)
            botao.clicked.connect(lambda checked, m=motivo: self.selecionar_motivo(m))
            self.layout.addRow(botao)

        # Campo de operações
        self.spin_operacoes = QSpinBox()
        self.spin_operacoes.setMinimum(1)
        self.spin_operacoes.setMaximum(999)
        self.layout.addRow("Número de Operações:", self.spin_operacoes)

        # Campo de avaliação
        self.spin_avaliacao = QSpinBox()
        self.spin_avaliacao.setMinimum(1)
        self.spin_avaliacao.setMaximum(5)
        self.layout.addRow("Avaliação (1-5):", self.spin_avaliacao)

        # Botões OK / Cancelar
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validar_confirmar)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def selecionar_motivo(self, motivo):
        self.motivo_selecionado = motivo
        # Desmarca os outros botões
        for m, b in self.motivos.items():
            b.setChecked(m == motivo)

    def validar_confirmar(self):
        if not self.motivo_selecionado:
            QMessageBox.warning(self, "Erro", "⚠️ Selecione um motivo para o consumo.")
            return
        self.accept()

    def get_values(self):
        """
        Retorna os valores: motivo selecionado, número de operações e avaliação.
        """
        return self.motivo_selecionado, self.spin_operacoes.value(), self.spin_avaliacao.value()


class TelaMovimentacao(QWidget):
    """
    Tela de movimentação de ferramentas.

    Permite a retirada, devolução e consumo de ferramentas, busca os dados da peça 
    e exibe as últimas movimentações em uma tabela.
    """
    def __init__(self, navegacao, rfid_usuario):
        """
        Inicializa a tela de movimentação.

        Parâmetros:
            navegacao (object): Objeto responsável pela navegação entre telas.
            rfid_usuario (str): RFID do usuário atual.
        """
        super().__init__()
        self.navegacao = navegacao
        self.rfid_usuario = rfid_usuario
        self._init_ui()

    def _init_ui(self):
        """
        Configura a interface do usuário, organizando os componentes em layout.
        """
        self.layout = QVBoxLayout()

        # Adiciona o título
        self.layout.addWidget(self._criar_label_titulo())

        # Adiciona o formulário de entrada
        self.layout.addLayout(self._criar_formulario())

        # Adiciona os botões de movimentação e navegação
        self.layout.addLayout(self._criar_botoes())

        # Adiciona a tabela de últimas movimentações
        self.layout.addWidget(QLabel("📜 Últimas Movimentações:"))
        self.layout.addWidget(self._criar_tabela())

        self.setLayout(self.layout)
        self.carregar_ultimas_movimentacoes()

    def _criar_label_titulo(self):
        """
        Cria e retorna o rótulo de título da tela.
        """
        label = QLabel("📦 Movimentação de Ferramentas")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _criar_formulario(self):
        """
        Cria e retorna o layout de formulário para entrada dos dados da ferramenta.
        """
        form_layout = QFormLayout()
        
        self.codigo_barras_input = QLineEdit()
        self.codigo_barras_input.setPlaceholderText("🔹 Escaneie o código de barras da ferramenta")
        self.codigo_barras_input.returnPressed.connect(self.buscar_dados_peca)
        form_layout.addRow("🔖 Código de Barras:", self.codigo_barras_input)

        self.lbl_descricao = QLabel("🔎 Descrição: -")
        self.lbl_estoque = QLabel("📦 Estoque Atual: -")
        self.lbl_consumivel = QLabel("🔁 Consumível: -")
        self.spin_quantidade = QSpinBox()
        self.spin_quantidade.setMinimum(1)
        self.spin_quantidade.setMaximum(999)

        form_layout.addRow("📄 Descrição:", self.lbl_descricao)
        form_layout.addRow("📊 Estoque:", self.lbl_estoque)
        form_layout.addRow("🔢 Quantidade:", self.spin_quantidade)
        form_layout.addRow("🔁 Consumível:", self.lbl_consumivel)        

        return form_layout

    def _criar_botoes(self):
        """
        Cria e retorna um layout contendo os botões de movimentação e navegação.
        """
        layout_botoes = QVBoxLayout()

        btn_retirar = QPushButton("🔴 Retirar Ferramenta")
        btn_retirar.clicked.connect(lambda: self.realizar_movimentacao_gui("RETIRADA"))
        layout_botoes.addWidget(btn_retirar)

        btn_devolver = QPushButton("🟢 Devolver Ferramenta")
        btn_devolver.clicked.connect(lambda: self.realizar_movimentacao_gui("DEVOLUCAO"))
        layout_botoes.addWidget(btn_devolver)

        # Botão de consumo como atributo, começa desabilitado
        self.btn_consumir = QPushButton("🔶 Consumir Ferramenta")
        self.btn_consumir.clicked.connect(lambda: self.realizar_movimentacao_gui("CONSUMO"))
        self.btn_consumir.setEnabled(False)
        layout_botoes.addWidget(self.btn_consumir)

        btn_voltar = QPushButton("⬅️ Voltar")
        btn_voltar.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))
        layout_botoes.addWidget(btn_voltar)

        return layout_botoes


    def _criar_tabela(self):
        """
        Cria e retorna a tabela que exibirá as últimas movimentações.
        """
        self.tabela = QTableWidget()
        # Atualize o número de colunas se desejar incluir mais dados (ex.: motivo, operações e avaliação)
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels([
            "Data/Hora", "Operador", "Código", "Descrição", "Tipo", 
            "Qtd", "Motivo", "Operações", "Avaliação"
        ])
        return self.tabela

    def _exibir_mensagem(self, titulo, mensagem, tipo="info"):
        """
        Exibe uma mensagem ao usuário utilizando QMessageBox.

        Parâmetros:
            titulo (str): Título da mensagem.
            mensagem (str): Conteúdo da mensagem.
            tipo (str): Tipo de mensagem ('info' ou 'warning').
        """
        if tipo == "info":
            QMessageBox.information(self, titulo, mensagem)
        else:
            QMessageBox.warning(self, titulo, mensagem)

    def validar_campos(self):
        """
        Valida os campos de entrada, garantindo que o código de barras esteja preenchido.

        Retorna:
            str ou None: O código de barras se válido; caso contrário, None.
        """
        codigo_barras = self.codigo_barras_input.text().strip()
        if not codigo_barras:
            self._exibir_mensagem("Erro", "⚠️ Nenhum código de barras foi inserido!", "warning")
            return None
        return codigo_barras

    def buscar_dados_peca(self):
        """
        Busca os dados da ferramenta a partir do código de barras e atualiza os campos:
        - Descrição
        - Estoque total e ativo
        - Status de consumível
        Também habilita/desabilita o botão de consumo com base nisso.
        """
        codigo = self.codigo_barras_input.text().strip()
        if not codigo:
            return

        dados = buscar_ferramenta_por_codigo(codigo)
        if dados:
            self.lbl_descricao.setText(f"🔎 Descrição: {dados['nome']}")
            self.lbl_estoque.setText(
                f"📦 Estoque Atual: {dados['quantidade']} unidades | Ativo: {dados['estoque_ativo']}"
            )
            self.lbl_consumivel.setText(dados.get("consumivel", "NÃO").strip().upper())

            self.dados_ferramenta = dados  # guarda os dados para uso nas ações

            # Resetar valor e deixar o máximo para definir depois conforme a ação
            self.spin_quantidade.setValue(1)
            self.spin_quantidade.setMaximum(999)  # máximo temporário

            # Habilita botão de consumo se for SIM
            if dados.get("consumivel", "NÃO").strip().upper() == "SIM":
                self.btn_consumir.setEnabled(True)
            else:
                self.btn_consumir.setEnabled(False)
        else:
            self.lbl_descricao.setText("🔎 Descrição: -")
            self.lbl_estoque.setText("📦 Estoque Atual: -")
            self.lbl_consumivel.setText("🔁 Consumível: -")
            self._exibir_mensagem("Erro", "❌ Peça não encontrada.", "warning")
            self.dados_ferramenta = None
            self.btn_consumir.setEnabled(False)


    def realizar_movimentacao_gui(self, acao):
        """
        Realiza a movimentação da ferramenta conforme a ação especificada (RETIRADA, DEVOLUCAO ou CONSUMO)
        e atualiza a interface.

        Parâmetros:
            acao (str): Tipo de movimentação.
        """
        codigo_barras = self.validar_campos()
        if not codigo_barras:
            return

        if not hasattr(self, 'dados_ferramenta') or not self.dados_ferramenta:
            self._exibir_mensagem("Erro", "⚠️ Nenhuma peça selecionada.", "warning")
            return

        estoque_disponivel = self.dados_ferramenta['quantidade']
        estoque_ativo = self.dados_ferramenta['estoque_ativo']

        # Ajusta o máximo permitido no campo de quantidade, conforme a ação
        if acao == "DEVOLUCAO":
            limite = estoque_ativo if estoque_ativo > 0 else 1
        else:  # RETIRADA ou CONSUMO
            limite = estoque_disponivel if estoque_disponivel > 0 else 1
        self.spin_quantidade.setMaximum(limite)

        # Se o valor atual for maior que o limite, força para o limite
        if self.spin_quantidade.value() > limite:
            self.spin_quantidade.setValue(limite)

        quantidade = self.spin_quantidade.value()

        # Validação específica para devolução
        if acao == "DEVOLUCAO" and estoque_ativo < quantidade:
            self._exibir_mensagem("Erro", "⚠️ Estoque ativo insuficiente para devolução.", "warning")
            return

        # Ação de consumo com popup
        if acao == "CONSUMO":
            dialog = DialogoConsumo(self)
            if dialog.exec_() == QDialog.Accepted:
                motivo, operacoes, avaliacao = dialog.get_values()
                resposta = realizar_movimentacao(
                    self.rfid_usuario, codigo_barras, acao, quantidade, motivo, operacoes, avaliacao
                )
            else:
                return  # Cancelado
        else:
            resposta = realizar_movimentacao(self.rfid_usuario, codigo_barras, acao, quantidade)

        if isinstance(resposta, dict):
            if resposta.get("status"):
                self._exibir_mensagem("Sucesso", resposta.get("mensagem"), "info")
                self._limpar_campos()
                self.carregar_ultimas_movimentacoes()
            else:
                self._exibir_mensagem("Erro", resposta.get("mensagem"), "warning")
        else:
            if resposta.startswith("✅"):
                self._exibir_mensagem("Sucesso", resposta, "info")
                self._limpar_campos()
                self.carregar_ultimas_movimentacoes()
            else:
                self._exibir_mensagem("Erro", resposta, "warning")



    def _limpar_campos(self):
        """
        Limpa os campos de entrada e reseta os labels para os valores padrão.
        """
        self.codigo_barras_input.clear()
        self.lbl_descricao.setText("🔎 Descrição: -")
        self.lbl_estoque.setText("📦 Estoque Atual: -")
        self.spin_quantidade.setValue(1)

    def carregar_ultimas_movimentacoes(self):
        """
        Carrega e exibe as últimas movimentações na tabela.
        """
        dados = buscar_ultimas_movimentacoes()
        self.tabela.setRowCount(0)
        for linha in dados:
            row = self.tabela.rowCount()
            self.tabela.insertRow(row)
            for col, item in enumerate(linha):
                self.tabela.setItem(row, col, QTableWidgetItem(str(item)))
