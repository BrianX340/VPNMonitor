import sys
import threading
from PyQt5 import QtWidgets, QtCore, QtGui
from ping3 import ping
from pystray import Icon, MenuItem, Menu
from PIL import Image

class WatermarkLabel(QtWidgets.QLabel):
    def __init__(self, message, parent=None):
        super().__init__(message, parent)
        self.setStyleSheet("""
            color: rgba(0, 255, 0, 10); /* texto blanco semitransparente */
            font-size: 40pt;
            font-weight: bold;
        """)
        self.setAlignment(QtCore.Qt.AlignCenter)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        shadow = QtGui.QColor(0, 0, 0, 100)
        painter.setPen(shadow)
        painter.drawText(self.rect().translated(2, 2), self.alignment(), self.text())
        painter.setPen(self.palette().color(QtGui.QPalette.WindowText))
        painter.drawText(self.rect(), self.alignment(), self.text())

class WatermarkWindow(QtWidgets.QWidget):
    def __init__(self, message):
        super().__init__()
        
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | 
                            QtCore.Qt.WindowStaysOnTopHint | 
                            QtCore.Qt.Tool |
                            QtCore.Qt.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 200)  

        self.label = WatermarkLabel(message, self)
        self.label.setGeometry(0, 0, 500, 200)

        screen_geometry = QtWidgets.QApplication.primaryScreen().availableGeometry()
        x = screen_geometry.width() - self.width() - 20
        y = screen_geometry.height() - self.height() - 20
        self.move(x, y)

    def update_message(self, message):
        self.label.setText(message)
        self.label.repaint()

class PingMonitorApp(QtWidgets.QApplication):
    def __init__(self, args, host, message):
        super().__init__(args)
        self.host = host
        self.message = message
        self.window = WatermarkWindow(message)
        self.window.show()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.check_ping)
        self.timer.start(1000)

        # Agregar icono en la bandeja del sistema
        self.create_system_tray()

    def check_ping(self):
        response = ping(self.host, timeout=1)
        if response is not None:
            self.window.update_message("VPN Conectada")
            if not self.window.isVisible():
                self.window.show()
        else:
            self.window.hide()

    def create_system_tray(self):
        """Crea un icono en la bandeja del sistema con opciones para salir."""
        image = Image.new("RGB", (64, 64), (0, 255, 0))  # Un icono verde básico

        menu = Menu(
            MenuItem("Salir", self.quit_app)
        )

        self.tray_icon = Icon("VPN Monitor", image, "VPN Monitor", menu)

        # Ejecutar el icono en un hilo separado
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        self.quit()

if __name__ == "__main__":
    host = "192.111.1.1"  # IP a la que se intentará comunicar
    message = "VPN Conectada"  # Mensaje personalizable
    app = PingMonitorApp(sys.argv, host, message)
    sys.exit(app.exec_())

# Para hacerlo ejecutable
# python -m PyInstaller --onefile --windowed .\main.py
