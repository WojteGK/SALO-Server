from PyQt6.QtWidgets import QMainWindow
from GUI import Ui_MainWindow
import subprocess
from datetime import datetime
import os
import shutil
import pandas as pd

class MainWindowExtended(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.server_process = None
        self.pushButtonRunServer.clicked.connect(self.run_server)
        self.pushButtonStopServer.clicked.connect(self.stop_server)

        self.pushButtonAddGroup.clicked.connect(self.add_group)
        self.pushButtonRemoveGroup.clicked.connect(self.remove_group)
        self.pushButtonAddConfiguration.clicked.connect(self.add_configuration)

        try:
            self.setStyleSheet(open("style.qss", "r").read())
        except:
            pass

        self.list_server_configs()

    def run_server(self):
        """
        Start server process.
        """
        try:
            if self.server_process is None:
                self.server_process = subprocess.Popen(
                    [os.path.join('.venv', 'Scripts', 'python.exe'), "server.py", f"--path {os.path.join(os.getcwd(), 'configs', self.listWidgetConfigList.currentItem().text())}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.labelServerStatus.setText("Server: ON")
                self.textEditServerLog.append(f"Server started at {str(datetime.now())}\n")
        except Exception as e:
            self.textEditServerLog.append(f"Error starting server: {str(e)}\n")

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

    def list_server_configs(self):
        """
        List all servers.
        """
        if not os.path.exists("configs"):
            os.makedirs("configs")

        self.listWidgetConfigList.clear()

        configs = [os.path.basename(f) for f in os.listdir("configs")]
        # Input the list into the listWidget
        self.listWidgetConfigList.addItems(configs)

    def add_group(self):
        """
        Add a group.
        """
        if self.lineEditGroupName.text() != "":
            self.listWidgetGroupList.addItem(self.lineEditGroupName.text())
            self.lineEditGroupName.clear()

    def remove_group(self):
        """
        Remove a group.
        """
        try:
            self.listWidgetGroupList.takeItem(self.listWidgetGroupList.currentRow())
        except:
            pass

    def add_configuration(self):
        """
        Add a configuration.
        """
        if self.lineEditConfigName.text() != "" and self.listWidgetGroupList.count() > 0:
            config_name = sanitize_filename(self.lineEditConfigName.text())
            model_path = [f for f in os.listdir(os.getcwd()) if f.endswith('.pt')][0]

            if not os.path.exists(os.path.join("configs", config_name)):
                os.makedirs(os.path.join("configs", config_name))
                # Copy the model to the configuration folder
                shutil.copy(model_path, os.path.join("configs", config_name, model_path))
                # Save the group list

                df = pd.DataFrame()
                alias = [self.listWidgetGroupList.item(i).text() for i in range(self.listWidgetGroupList.count())]
                df['group'] = [i for i in range(len(alias))]
                df['alias'] = alias
                df['count'] = [0 for i in range(len(alias))]

                df.to_csv(os.path.join("configs", config_name, "data.csv"), index=False)

                os.makedirs(os.path.join("configs", config_name, "images"))

def sanitize_filename(filename):
    # List of characters to remove or replace
    invalid_chars = r'\/:*?"<>|'
    # Replace them with underscore
    for ch in invalid_chars:
        filename = filename.replace(ch, "_")

    # Trim trailing dots and spaces to avoid Windows issues
    filename = filename.rstrip(". ")

    # Check for reserved names, etc. (optional)
    if filename.upper() in {"CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3",
                            "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                            "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6",
                            "LPT7", "LPT8", "LPT9"}:
        filename += "_safe"

    return filename
