from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout,
    QMessageBox, QSpinBox, QTableWidget, QTableWidgetItem, QDialog,
    QDialogButtonBox, QHeaderView
)
from PyQt5.QtCore import Qt

from utils.movimentacoes import realizar_movimentacao
from database.database import buscar_ferramenta_por_codigo, buscar_ultimas_movimentacoes
from database.database_utils import buscar_estoque_ativo_usuario


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
        self.layout.addRow("Número de Operações Totais por Ferramenta:", self.spin_operacoes)

        # Campo de avaliação
        self.spin_avaliacao = QSpinBox()
        self.spin_avaliacao.setMinimum(1)
        self.spin_avaliacao.setMaximum(5)
        self.layout.addRow("Avaliação (1-5 / Pior-Melhor):", self.spin_avaliacao)

        # Botões OK / Cancelar
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validar_confirmar)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def selecionar_motivo(self, motivo):
        self.motivo_selecionado = motivo
        for m, b in self.motivos.items():
            b.setChecked(m == motivo)

    def validar_confirmar(self):
        if not self.motivo_selecionado:
            QMessageBox.warning(self, "Erro", "⚠️ Selecione um motivo para o consumo.")
            return
        self.accept()

    def get_values(self):
        return self.motivo_selecionado, self.spin_operacoes.value(), self.spin_avaliacao.value()


class TelaMovimentacao(QWidget):
    """
    Tela de movimentação de ferramentas.
    Permite retirada, devolução e consumo, exibe últimas movimentações e estoque ativo do usuário.
    """
    def __init__(self, navegacao, rfid_usuario):
        super().__init__()
        self.navegacao = navegacao
        self.rfid_usuario = rfid_usuario
        self.dados_ferramenta = None
        self.acao_selecionada = None
        self._init_ui()

    def _init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self._criar_label_titulo())
        self.layout.addLayout(self._criar_formulario())
        self.layout.addLayout(self._criar_botoes())

        # Tabela de últimas movimentações
        self.layout.addWidget(QLabel("📜 Últimas Movimentações:"))
        self.layout.addWidget(self._criar_tabela_logs())

        # Tabela de estoque ativo
        self.layout.addWidget(QLabel("🎒 Estoque Ativo do Usuário:"))
        self.layout.addWidget(self._criar_tabela_estoque_ativo())

        self.setLayout(self.layout)
        self.carregar_ultimas_movimentacoes()
        self.carregar_estoque_ativo()

    def _criar_label_titulo(self):
        label = QLabel("📦 Movimentação de Ferramentas")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _criar_formulario(self):
        form = QFormLayout()
        self.codigo_barras_input = QLineEdit()
        self.codigo_barras_input.setPlaceholderText("🔹 Escaneie o código de barras da ferramenta")
        self.codigo_barras_input.returnPressed.connect(self.buscar_dados_peca)
        form.addRow("🔖 Código de Barras:", self.codigo_barras_input)

        self.lbl_descricao = QLabel("🔎 Descrição: -")
        self.lbl_estoque = QLabel("📦 Almoxarifado: - | Ativo: -")
        self.lbl_consumivel = QLabel("🔁 Consumível: -")
        self.spin_quantidade = QSpinBox()
        self.spin_quantidade.setMinimum(1)
        self.spin_quantidade.setMaximum(999)

        form.addRow(self.lbl_descricao)
        form.addRow(self.lbl_estoque)
        form.addRow("🔢 Quantidade:", self.spin_quantidade)
        form.addRow(self.lbl_consumivel)

        self.label_status = QLabel("")
        form.addRow(self.label_status)
        return form

    def _criar_botoes(self):
        vbox = QVBoxLayout()
        btn_retirar = QPushButton("🔴 Retirar Ferramenta")
        btn_retirar.clicked.connect(lambda: self._executar_acao("RETIRADA"))
        vbox.addWidget(btn_retirar)

        btn_devolver = QPushButton("🟢 Devolver Ferramenta")
        btn_devolver.clicked.connect(lambda: self._executar_acao("DEVOLUCAO"))
        vbox.addWidget(btn_devolver)

        self.btn_consumir = QPushButton("🔶 Consumir Ferramenta")
        self.btn_consumir.clicked.connect(lambda: self._executar_acao("CONSUMO"))
        self.btn_consumir.setEnabled(False)
        vbox.addWidget(self.btn_consumir)

        btn_voltar = QPushButton("⬅️ Voltar")
        btn_voltar.clicked.connect(lambda: self.navegacao.mostrar_tela("painel"))
        vbox.addWidget(btn_voltar)
        return vbox

    def _criar_tabela_logs(self):
        self.tabela_logs = QTableWidget()
        self.tabela_logs.setColumnCount(9)
        self.tabela_logs.setHorizontalHeaderLabels([
            "Data/Hora", "Operador", "Código", "Descrição", "Tipo", 
            "Qtd", "Motivo", "Operações", "Avaliação"
        ])
        return self.tabela_logs

    def _criar_tabela_estoque_ativo(self):
        self.tabela_ativo = QTableWidget()
        self.tabela_ativo.setColumnCount(3)
        self.tabela_ativo.setHorizontalHeaderLabels(["Código", "Descrição", "Qtd Ativa"])
        header = self.tabela_ativo.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        return self.tabela_ativo

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QFormLayout,
    QMessageBox, QSpinBox, QTableWidget, QTableWidgetItem, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt


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
            botao.clicked.connect(lambda _, m=motivo: self.selecionar_motivo(m))
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
        self.layout.addRow("Avaliação (1-5):", self.spin_avaliacao)
        # Botões OK/Cancelar
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.validar_confirmar)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def selecionar_motivo(self, motivo):
        self.motivo_selecionado = motivo
        for m, b in self.motivos.items():
            b.setChecked(m == motivo)

    def validar_confirmar(self):
        if not self.motivo_selecionado:
            QMessageBox.warning(self, "Erro", "⚠️ Selecione um motivo para o consumo.")
            return
        self.accept()

    def get_values(self):
        return self.motivo_selecionado, self.spin_operacoes.value(), self.spin_avaliacao.value()


class TelaMovimentacao(QWidget):
    """
    Tela de movimentação de ferramentas.
    Permite retirada, devolução e consumo, exibe últimas movimentações e estoque ativo do usuário.
    """
    def __init__(self, navegacao, rfid_usuario):
        super().__init__()
        self.navegacao = navegacao
        self.rfid_usuario = rfid_usuario
        self.dados_ferramenta = None
        self._init_ui()


    def atualizar_tela(self):
        # Recarrega sempre que a tela for exibida
        self.carregar_ultimas_movimentacoes()
        self.carregar_estoque_ativo()

    def _init_ui(self):
        self.layout = QVBoxLayout()
        self.layout.addWidget(self._criar_label_titulo())
        self.layout.addLayout(self._criar_formulario())
        self.layout.addLayout(self._criar_botoes())
        self.layout.addWidget(QLabel("📜 Últimas Movimentações:"))
        self.layout.addWidget(self._criar_tabela_logs())
        self.layout.addWidget(QLabel("🎒 Estoque Ativo do Usuário:"))
        self.layout.addWidget(self._criar_tabela_estoque_ativo())
        self.setLayout(self.layout)
        self.carregar_ultimas_movimentacoes()
        self.carregar_estoque_ativo()

    def _criar_label_titulo(self):
        label = QLabel("📦 Movimentação de Ferramentas")
        label.setAlignment(Qt.AlignCenter)
        return label

    def _criar_formulario(self):
        form = QFormLayout()
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("🔹 Escaneie o código de barras")
        self.codigo_input.returnPressed.connect(self.buscar_dados_peca)
        form.addRow("Código de Barras:", self.codigo_input)
        self.lbl_descricao = QLabel("🔎 Descrição: -")
        self.lbl_estoque = QLabel("📦 Almoxarifado: - | Ativo: -")
        self.lbl_consumivel = QLabel("🔁 Consumível: -")
        self.spin_qtd = QSpinBox()
        self.spin_qtd.setMinimum(1)
        self.spin_qtd.setMaximum(999)
        form.addRow(self.lbl_descricao)
        form.addRow(self.lbl_estoque)
        form.addRow("Quantidade:", self.spin_qtd)
        form.addRow(self.lbl_consumivel)
        self.label_status = QLabel("")
        form.addRow(self.label_status)
        return form

    def _criar_botoes(self):
        v = QVBoxLayout()
        btn_r = QPushButton("🔴 Retirar")
        btn_r.clicked.connect(lambda: self._executar_acao('RETIRADA'))
        v.addWidget(btn_r)
        btn_d = QPushButton("🟢 Devolver")
        btn_d.clicked.connect(lambda: self._executar_acao('DEVOLUCAO'))
        v.addWidget(btn_d)
        self.btn_c = QPushButton("🔶 Consumir")
        self.btn_c.clicked.connect(lambda: self._executar_acao('CONSUMO'))
        self.btn_c.setEnabled(False)
        v.addWidget(self.btn_c)
        btn_volt = QPushButton("⬅️ Voltar")
        btn_volt.clicked.connect(lambda: self.navegacao.mostrar_tela('painel', self.rfid_usuario))
        v.addWidget(btn_volt)
        return v

    def _criar_tabela_logs(self):
        self.table_logs = QTableWidget()
        self.table_logs.setColumnCount(9)
        self.table_logs.setHorizontalHeaderLabels([
            "Data/Hora","Operador","Código","Descrição",
            "Tipo","Qtd","Motivo","Operações","Avaliação"
        ])
        return self.table_logs

    def _criar_tabela_estoque_ativo(self):
        self.table_ativo = QTableWidget()
        self.table_ativo.setColumnCount(3)
        self.table_ativo.setHorizontalHeaderLabels(["Código","Descrição","Qtd Ativa"])
        return self.table_ativo

    def _exibir_mensagem(self, t, m, tipo='info'):
        if tipo=='info':
            QMessageBox.information(self,t,m)
        else:
            QMessageBox.warning(self,t,m)

    def validar_campos(self):
        cod = self.codigo_input.text().strip()
        if not cod:
            self._exibir_mensagem("Erro","Insira um código!",'warning')
            return None
        return cod

    def buscar_dados_peca(self):
        cod = self.validar_campos()
        if not cod: return
        d = buscar_ferramenta_por_codigo(cod)
        if not d:
            self._exibir_mensagem("Erro","Ferramenta não encontrada.",'warning')
            self._limpar_campos()
            return
        self.dados_ferramenta = {'id':d['id'],'nome':d['nome'],'estoque_almoxarifado':d['estoque_almoxarifado'],'consumivel':d['consumivel']}
        ativos = buscar_estoque_ativo_usuario(self.rfid_usuario)
        sal = next((r[3] for r in ativos if r[0]==d['id']),0)
        self.lbl_descricao.setText(f"🔎 Descrição: {d['nome']}")
        self.lbl_estoque.setText(f"📦 Almoxarifado: {d['estoque_almoxarifado']} | Ativo: {sal}")
        self.lbl_consumivel.setText(d['consumivel'])
        self.spin_qtd.setValue(1)
        self.btn_c.setEnabled(d['consumivel']=='SIM')

    def _executar_acao(self, acao):
        cod = self.validar_campos()
        if not cod or not self.dados_ferramenta:
            self._aplicar_feedback_erro("Nenhuma ferramenta selecionada.")
            return
        q = self.spin_qtd.value()
        disp = self.dados_ferramenta['estoque_almoxarifado']
        ativos = buscar_estoque_ativo_usuario(self.rfid_usuario)
        saldo = next((r[3] for r in ativos if r[0]==self.dados_ferramenta['id']),0)
        if acao=='RETIRADA' and q>disp:
            self._aplicar_feedback_erro("Estoque insuficiente.")
            return
        if acao=='DEVOLUCAO' and q>saldo:
            self._aplicar_feedback_erro("Ativo insuficiente.")
            return
        if acao=='CONSUMO' and q>disp:
            self._aplicar_feedback_erro("Estoque insuficiente.")
            return
        self._resetar_feedback_visual()
        if acao=='CONSUMO':
            dlg=DialogoConsumo(self)
            if dlg.exec_()!=QDialog.Accepted: return
            motivo,ops,aval=dlg.get_values()
            resp=realizar_movimentacao(self.rfid_usuario,cod,acao,q,motivo,ops,aval)
        else:
            resp=realizar_movimentacao(self.rfid_usuario,cod,acao,q)
        ok=resp.get('status') if isinstance(resp,dict) else False
        msg=resp.get('mensagem') if isinstance(resp,dict) else str(resp)
        if ok:
            self.label_status.setText(msg)
            self._limpar_campos()
            self.carregar_ultimas_movimentacoes()
            self.carregar_estoque_ativo()
        else:
            self._aplicar_feedback_erro(msg)

    def _aplicar_feedback_erro(self, m):
        self.spin_qtd.setStyleSheet("background-color:#ffcccc;")
        self.label_status.setStyleSheet("color:red;font-weight:bold;")
        self.label_status.setText(m)

    def _resetar_feedback_visual(self):
        self.spin_qtd.setStyleSheet("")
        self.label_status.setStyleSheet("color:black;font-weight:normal;")
        self.label_status.setText("")

    def _limpar_campos(self):
        self.codigo_input.clear()
        self.lbl_descricao.setText("🔎 Descrição: -")
        self.lbl_estoque.setText("📦 Almoxarifado: - | Ativo: -")
        self.lbl_consumivel.setText("🔁 Consumível: -")
        self.spin_qtd.setValue(1)

    def carregar_ultimas_movimentacoes(self):
        dados=buscar_ultimas_movimentacoes()
        self.table_logs.setRowCount(0)
        for linha in dados:
            r=self.table_logs.rowCount()
            self.table_logs.insertRow(r)
            for c,item in enumerate(linha):
                self.table_logs.setItem(r,c,QTableWidgetItem(str(item)))

    def carregar_estoque_ativo(self):
        dados=buscar_estoque_ativo_usuario(self.rfid_usuario)
        self.table_ativo.setRowCount(0)
        for fid,nome,cod,sal in dados:
            r=self.table_ativo.rowCount()
            self.table_ativo.insertRow(r)
            self.table_ativo.setItem(r,0,QTableWidgetItem(cod))
            self.table_ativo.setItem(r,1,QTableWidgetItem(nome))
            self.table_ativo.setItem(r,2,QTableWidgetItem(str(sal)))
