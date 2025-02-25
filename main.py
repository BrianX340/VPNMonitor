import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from ping3 import ping

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

    def check_ping(self):
        response = ping(self.host, timeout=1)
        if response is not None:
            self.window.update_message("VPN Conectada")
        else:
            self.window.update_message("VPN Desconectada")

if __name__ == "__main__":
    host = "192.111.1.1" # Ip con la que intentara comunicarse
    message = "VPN Conectada" # Mensaje personalizable
    app = PingMonitorApp(sys.argv, host, message)
    sys.exit(app.exec_())
