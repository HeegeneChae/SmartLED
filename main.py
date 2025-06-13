import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QSlider, QLabel, QColorDialog, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt
import serial
import serial.tools.list_ports

class SmartLightGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart RGB Light Controller")
        self.resize(400, 300)

        self.serial_port = None
        self.connected = False

        self.init_ui()

    def init_ui(self):
        # Connect Button
        self.btn_connect = QPushButton("Connect")
        self.btn_connect.clicked.connect(self.connect_serial)

        # On/Off Button
        self.btn_onoff = QPushButton("Turn ON")
        self.btn_onoff.setEnabled(False)
        self.btn_onoff.setCheckable(True)
        self.btn_onoff.clicked.connect(self.toggle_onoff)

        # Color Picker Button
        self.btn_color = QPushButton("Pick Color")
        self.btn_color.setEnabled(False)
        self.btn_color.clicked.connect(self.open_color_picker)

        # Brightness Slider
        self.slider_brightness = QSlider(Qt.Horizontal)
        self.slider_brightness.setMinimum(0)
        self.slider_brightness.setMaximum(255)
        self.slider_brightness.setValue(128)
        self.slider_brightness.setEnabled(False)
        self.slider_brightness.valueChanged.connect(self.brightness_changed)

        # Status Label
        self.lbl_status = QLabel("Disconnected")

        # Layout
        vbox = QVBoxLayout()
        vbox.addWidget(self.btn_connect)

        hbox = QHBoxLayout()
        hbox.addWidget(self.btn_onoff)
        hbox.addWidget(self.btn_color)
        vbox.addLayout(hbox)

        vbox.addWidget(QLabel("Brightness"))
        vbox.addWidget(self.slider_brightness)
        vbox.addWidget(self.lbl_status)

        self.setLayout(vbox)

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
