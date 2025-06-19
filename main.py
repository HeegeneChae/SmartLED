import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QSlider, QLabel, QColorDialog, 
    QVBoxLayout, QHBoxLayout, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QColor
import serial
import serial.tools.list_ports

class SmartLightGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart RGB Light Controller")
        self.resize(500, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-family: 'Segoe UI', Arial;
            }
            QPushButton {
                background-color: #0d47a1;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:disabled {
                background-color: #424242;
            }
            QPushButton:checked {
                background-color: #c62828;
            }
            QSlider::groove:horizontal {
                border: 1px solid #424242;
                height: 8px;
                background: #424242;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0d47a1;
                border: none;
                width: 18px;
                margin: -5px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: #1565c0;
            }
            QLabel {
                color: #e0e0e0;
            }
            QGroupBox {
                border: 1px solid #424242;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)

        self.serial_port = None
        self.connected = False
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Connection Group
        connection_group = QGroupBox("Connection")
        connection_layout = QVBoxLayout()
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect_serial)
        connection_layout.addWidget(self.btn_connect)
        connection_group.setLayout(connection_layout)
        main_layout.addWidget(connection_group)

        # Control Group
        control_group = QGroupBox("Light Control")
        control_layout = QVBoxLayout()
        
        # Power and Color buttons
        button_layout = QHBoxLayout()
        self.btn_onoff = QPushButton("Turn ON")
        self.btn_onoff.setEnabled(False)
        self.btn_onoff.setCheckable(True)
        self.btn_onoff.clicked.connect(self.toggle_onoff)
        
        self.btn_color = QPushButton("Pick Color")
        self.btn_color.setEnabled(False)
        self.btn_color.clicked.connect(self.open_color_picker)
        
        button_layout.addWidget(self.btn_onoff)
        button_layout.addWidget(self.btn_color)
        control_layout.addLayout(button_layout)

        # Brightness control
        brightness_layout = QVBoxLayout()
        brightness_label = QLabel("Brightness")
        self.slider_brightness = QSlider(Qt.Horizontal)
        self.slider_brightness.setMinimum(0)
        self.slider_brightness.setMaximum(255)
        self.slider_brightness.setValue(128)
        self.slider_brightness.setEnabled(False)
        self.slider_brightness.valueChanged.connect(self.brightness_changed)
        brightness_layout.addWidget(brightness_label)
        brightness_layout.addWidget(self.slider_brightness)
        control_layout.addLayout(brightness_layout)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # Status Group
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        self.lbl_status = QLabel("Disconnected")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.lbl_status)
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)

        self.setLayout(main_layout)

        # Initial color
        self.current_color = (255, 255, 255)
        self.brightness = 128
        self.power_on = False

    def connect_serial(self):
        if not self.connected:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                self.lbl_status.setText("No serial ports found!")
                return
            port_name = ports[0].device  # 일단 첫번째 포트 자동선택
            try:
                self.serial_port = serial.Serial(port_name, 115200, timeout=1)
                self.connected = True
                self.lbl_status.setText(f"Connected: {port_name}")
                self.btn_connect.setText("Disconnect")
                self.btn_onoff.setEnabled(True)
                self.btn_color.setEnabled(True)
                self.slider_brightness.setEnabled(True)
            except Exception as e:
                self.lbl_status.setText(f"Connection failed: {e}")
        else:
            self.serial_port.close()
            self.connected = False
            self.lbl_status.setText("Disconnected")
            self.btn_connect.setText("Connect")
            self.btn_onoff.setEnabled(False)
            self.btn_color.setEnabled(False)
            self.slider_brightness.setEnabled(False)

    def toggle_onoff(self):
        self.power_on = self.btn_onoff.isChecked()
        if self.power_on:
            self.btn_onoff.setText("Turn OFF")
        else:
            self.btn_onoff.setText("Turn ON")
        self.send_data()

    def open_color_picker(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.current_color = (color.red(), color.green(), color.blue())
            self.send_data()

    def brightness_changed(self):
        self.brightness = self.slider_brightness.value()
        self.send_data()

    def send_data(self):
        if self.connected and self.serial_port:
            # 시리얼 프로토콜: P(on/off), R, G, B, BRT (brightness)
            # 예시: "P1 R255 G128 B64 BR128\n"
            p = 1 if self.power_on else 0
            r, g, b = self.current_color
            br = self.brightness
            msg = f"P{p} R{r} G{g} B{b} BR{br}\n"
            try:
                self.serial_port.write(msg.encode())
                self.lbl_status.setText(f"Sent: {msg.strip()}")
            except Exception as e:
                self.lbl_status.setText(f"Send error: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = SmartLightGUI()
    gui.show()
    sys.exit(app.exec_())
