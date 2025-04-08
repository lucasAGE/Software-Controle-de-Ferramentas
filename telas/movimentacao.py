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
        self.layout.addRow("Número de Operações Totais:", self.spin_operacoes)

        # Campo de avaliação
        self.spin_avaliacao = QSpinBox()
        self.spin_avaliacao.setMinimum(1)
        self.spin_avaliacao.setMaximum(5)
        self.layout.addRow("Avaliação (1-5/Pior-Melhor):", self.spin_avaliacao)

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
        self.acao_selecionada = None


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

        self.label_status = QLabel("")
        self.label_status.setStyleSheet("color: black; font-weight: normal;")
        form_layout.addRow("", self.label_status)
        

        return form_layout

    def _criar_botoes(self):
        """
        Cria e retorna um layout contendo os botões de movimentação e navegação.
        """
        layout_botoes = QVBoxLayout()

        btn_retirar = QPushButton("🔴 Retirar Ferramenta")
        btn_retirar.clicked.connect(lambda: self._setar_acao_e_mover("RETIRADA"))
        layout_botoes.addWidget(btn_retirar)

        btn_devolver = QPushButton("🟢 Devolver Ferramenta")
        btn_devolver.clicked.connect(lambda: self._setar_acao_e_mover("DEVOLUCAO"))
        layout_botoes.addWidget(btn_devolver)

        # Botão de consumo como atributo, começa desabilitado
        self.btn_consumir = QPushButton("🔶 Consumir Ferramenta")
        self.btn_consumir.clicked.connect(lambda: self._setar_acao_e_mover("CONSUMO"))
        self.btn_consumir.setEnabled(False)
        layout_botoes.addWidget(self.btn_consumir)

        btn_voltar = QPushButton("⬅️ Voltar")
        btn_voltar.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))
        layout_botoes.addWidget(btn_voltar)

        return layout_botoes

    def _setar_acao_e_mover(self, acao):
        """
        Define a ação selecionada e executa a movimentação correspondente.
        """
        self.acao_selecionada = acao
        self.realizar_movimentacao_gui(acao)



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
        Também prepara a interface para a movimentação.
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

            self.dados_ferramenta = dados  # guarda os dados para uso na movimentação

            self.spin_quantidade.setValue(1)
            self.spin_quantidade.setMaximum(999)  # limite temporário — será corrigido na movimentação

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
        """
        codigo_barras = self.validar_campos()
        if not codigo_barras:
            return

        if not hasattr(self, 'dados_ferramenta') or not self.dados_ferramenta:
            self._aplicar_feedback_erro("❌ Nenhuma peça selecionada.")
            return

        estoque_disponivel = self.dados_ferramenta['quantidade']
        estoque_ativo = self.dados_ferramenta['estoque_ativo']
        quantidade = self.spin_quantidade.value()

        # Verificações manuais de limites
        if acao == "RETIRADA" and quantidade > estoque_disponivel:
            self._aplicar_feedback_erro("❌ Estoque insuficiente para retirada.")
            self.spin_quantidade.clear()
            return

        if acao == "DEVOLUCAO" and quantidade > estoque_ativo:
            self._aplicar_feedback_erro("❌ Estoque ativo insuficiente para devolução.")
            self.spin_quantidade.clear()
            return

        if acao == "CONSUMO" and quantidade > estoque_disponivel:
            self._aplicar_feedback_erro("❌ Estoque insuficiente para consumo.")
            self.spin_quantidade.clear()
            return

        # Ajusta visualmente, tudo ok
        self._resetar_feedback_visual()

        # Pop-up para consumo
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

        # Resposta e feedback visual
        if isinstance(resposta, dict):
            mensagem = resposta.get("mensagem", "")
            if resposta.get("status"):
                self.label_status.setText(mensagem)
                self._limpar_campos()
                self.carregar_ultimas_movimentacoes()
            else:
                self._aplicar_feedback_erro(mensagem)
        else:
            if isinstance(resposta, str) and resposta.startswith("❌"):
                self._aplicar_feedback_erro(resposta)
            else:
                self.label_status.setText(resposta)


    def _aplicar_feedback_erro(self, mensagem):
        self.spin_quantidade.setStyleSheet("background-color: #ffcccc;")
        self.label_status.setStyleSheet("color: red; font-weight: bold;")
        self.label_status.setText(mensagem)

    def _resetar_feedback_visual(self):
        self.spin_quantidade.setStyleSheet("")
        self.label_status.setStyleSheet("color: black; font-weight: normal;")
        self.label_status.setText("")

         
            
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
