import sys
from PyQt6.QtWidgets import QApplication
from interface_dinamica import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    janela_principal = MainWindow()
    janela_principal.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()