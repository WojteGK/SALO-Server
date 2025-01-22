from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QSizePolicy
from GUI import Ui_MainWindow
import subprocess
from datetime import datetime
import os
import shutil
import pandas as pd
import socket

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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

        self.layout = QVBoxLayout(self.widgetPLTChart)
        self.canvas = MplCanvas(self.widgetPLTChart, width=5, height=4, dpi=100)
        self.layout.addWidget(self.canvas)
        self.plot_timer = QTimer()
        self.plot_timer.timeout.connect(self.refresh_chart)
        self.plot_timer.start(1000)

        self.current_config = None

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
                    [os.path.join(os.getcwd(),'.venv', 'Scripts', 'python.exe'), "server.py", f"--path", f"{os.path.join(os.getcwd(), 'configs', self.listWidgetConfigList.currentItem().text())}"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                self.labelServerStatus.setText("Server: ON")
                self.textEditServerLog.append(f"Server started on {get_device_ip()}")
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

                self.currrent_config = config_name

                self.list_server_configs()

    def refresh_chart(self):
        """
        Refresh the chart.
        """
        if self.current_config is not None:
            target = str(max([int(f.strip('.csv')) for f in os.listdir(os.path.join("configs", self.current_config, 'cache'))])) + '.csv'
            data = pd.read_csv(os.path.join("configs", self.current_config, 'cache', target))
            self.canvas.plot_barchart(data['alias'], data['count'])

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)

        # Make the canvas expand/shrink to fill the available space
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding
        )
        # Inform the layout system that the size may have changed
        self.updateGeometry()

    def plot_barchart(self, categories, values):
        """
        A helper method to create/update a bar chart on this canvas.
        """
        # Clear any existing drawing on the Axes
        self.ax.clear()

        # Plot a vertical bar chart
        self.ax.bar(categories, values, width=0.6, color='skyblue', edgecolor='black')

        # Set labels/titles if desired
        self.ax.set_xlabel("Categories")
        self.ax.set_ylabel("Values")
        self.ax.set_title("Bar Chart Example")

        # Redraw the canvas
        self.draw()


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

def get_device_ip():
    """
    Get the current device's IP address in the network.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to an external address; doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
