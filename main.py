if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from logic import *

    app = QApplication(sys.argv)
    window = MainWindowExtended()
    window.show()
    sys.exit(app.exec())