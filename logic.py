from PyQt6.QtWidgets import QMainWindow
from GUI import Ui_MainWindow

class MainWindowExtended(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.pushButtonRunServer.clicked.connect(self.run_server)
        self.pushButtonStopServer.clicked.connect(self.stop_server)

    def run_server(self):
        """
        Start server process.
        """
        self.labelServerStatus.setText("Server: ON")
        self.textEditServerLog.append("Server started...\n")

    def stop_server(self):
        """
        Stop server process.
        """
        self.labelServerStatus.setText("Server: OFF")
        self.textEditServerLog.append("Server stopped...\n")
