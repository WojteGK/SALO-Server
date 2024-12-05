from PyQt6.QtWidgets import QMainWindow
from GUI import Ui_MainWindow
import subprocess

class MainWindowExtended(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.server_process = None
        self.pushButtonRunServer.clicked.connect(self.run_server)
        self.pushButtonStopServer.clicked.connect(self.stop_server)

    def run_server(self):
        """
        Start server process.
        """
        if self.server_process is None:
            self.server_process = subprocess.Popen(
                ["python", "server.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.labelServerStatus.setText("Server: ON")
            self.textEditServerLog.append("Server started...\n")

    def stop_server(self):
        """
        Stop server process.
        """
        if self.server_process is not None:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            self.labelServerStatus.setText("Server: OFF")
            self.textEditServerLog.append("Server stopped...\n")
