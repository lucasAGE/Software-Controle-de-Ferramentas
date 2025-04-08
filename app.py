import sys
from PyQt5.QtWidgets import QApplication
from interface.navegacao import Navegacao

def main():
    # Cria (ou reutiliza) a instância do QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Apenas o main inicializa a interface e inicia o loop de eventos.
    janela = Navegacao()
    janela.setWindowTitle("Controle de Ferramentas")
    janela.resize(800, 600)
    janela.show()

    # Inicia o loop de eventos; certifique-se de que nenhum outro módulo o invoque.
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
