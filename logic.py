from PyQt6.QtWidgets import QMainWindow
from GUI import Ui_MainWindow
import subprocess
from datetime import datetime

class MainWindowExtended(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.server_process = None
        self.pushButtonRunServer.clicked.connect(self.run_server)
        self.pushButtonStopServer.clicked.connect(self.stop_server)

        try:
            self.setStyleSheet(open("style.qss", "r").read())
        except:
            pass

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
            self.textEditServerLog.append(f"Server started at {str(datetime.now())}\n")

    def stop_server(self):
        """
        Stop server process.
        """
        if self.server_process is not None:
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            self.labelServerStatus.setText("Server: OFF")
            self.textEditServerLog.append(f"Server stopped at {str(datetime.now())}\n")
