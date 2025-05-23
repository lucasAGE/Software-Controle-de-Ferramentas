#!/usr/bin/env python3
"""
interface/navegacao.py

Gerencia a navegação entre telas no sistema de controle de ferramentas.
"""

from PyQt5.QtWidgets import QStackedWidget

# Imports relativos para módulos dentro de 'interface'
from .telalogin import TelaLogin
from .painel import PainelPrincipal

# Imports absolutos para módulos externos
from telas.movimentacao import TelaMovimentacao
from telas.admin import Admin
from telas.exportacao import TelaExportacao
from telas.cadastro import TelaCadastros
from estoque.estoque import TelaEstoque
from telas.tela_login_rfid import TelaLoginRFID
from telas.tela_login_manual import TelaLoginManual


class Navegacao(QStackedWidget):
    """Gerencia a navegação entre telas no sistema."""

    def __init__(self):
        super().__init__()
        self.telas = {}
        self.perfil_atual = None
        self.rfid_usuario = None

        try:
            self._inicializar_telas()
            self.mostrar_tela("login")  # Tela inicial
        except Exception as e:
            print(f"❌ Erro ao carregar as telas: {e}")

    def _inicializar_telas(self):
        """Inicializa e registra as telas do sistema."""
        self.telas = {
            "login": TelaLogin(self, self.definir_perfil),
            "login_rfid": TelaLoginRFID(self, self.definir_perfil),
            "login_manual": TelaLoginManual(self, self.definir_perfil),
            "painel": PainelPrincipal(self),
            "export": TelaExportacao(self),
            "cadastro": TelaCadastros(self),
            "estoque": TelaEstoque(self),
            "admin": Admin()
        }
        for tela in self.telas.values():
            self.addWidget(tela)

    def mostrar_tela(self, nome_tela: str, rfid_usuario: str = None):
        """
        Exibe a tela especificada; para movimentação, injeta o RFID do usuário.

        :param nome_tela: chave da tela a ser exibida
        :param rfid_usuario: RFID do usuário, se aplicável
        """
        if nome_tela == "movimentacao":
            if rfid_usuario:
                self.rfid_usuario = rfid_usuario
            # Cria dinamicamente TelaMovimentacao com RFID
            self.telas["movimentacao"] = TelaMovimentacao(self, self.rfid_usuario)
            self.addWidget(self.telas["movimentacao"])

        tela = self.telas.get(nome_tela)
        if tela:
            if hasattr(tela, "atualizar_tela"):
                tela.atualizar_tela()
            self.setCurrentWidget(tela)
            print(f"📌 Mudando para a tela: {nome_tela}")
        else:
            print(f"⚠️ Erro: Tela '{nome_tela}' não encontrada!")

    def definir_perfil(self, perfil: str, rfid_usuario: str):
        """
        Define perfil atual e atualiza painel conforme o tipo de usuário.

        :param perfil: 'admin' ou 'operador'
        :param rfid_usuario: RFID do usuário
        """
        self.perfil_atual = perfil
        self.rfid_usuario = rfid_usuario
        painel = self.telas.get("painel")
        if painel and hasattr(painel, "configurar_por_perfil"):
            painel.configurar_por_perfil(perfil)
