from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLCDNumber, QProgressBar
from .styles import LCD_NUMBER_STYLE, LABEL_STYLE, GAUGE_STYLE
from PyQt5.QtCore import pyqtSlot

class TelemetryDashboard(QWidget):
    """
    TelemetryDashboard class inheriting from QWidget.
    Displays real-time telemetry data in numerical and graphical formats.
    """
    def __init__(self, parent=None):
        super(TelemetryDashboard, self).__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Orientation Display
        orientation_label = QLabel("Orientation (Pitch, Yaw, Roll)")
        orientation_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(orientation_label)
        
        self.pitch_display = QLCDNumber()
        self.pitch_display.setStyleSheet(LCD_NUMBER_STYLE)
        self.pitch_display.setDigitCount(5)
        layout.addWidget(self.pitch_display)
        
        self.yaw_display = QLCDNumber()
        self.yaw_display.setStyleSheet(LCD_NUMBER_STYLE)
        self.yaw_display.setDigitCount(5)
        layout.addWidget(self.yaw_display)
        
        self.roll_display = QLCDNumber()
        self.roll_display.setStyleSheet(LCD_NUMBER_STYLE)
        self.roll_display.setDigitCount(5)
        layout.addWidget(self.roll_display)
        
        # Position Display
        position_label = QLabel("Position (X, Y, Z)")
        position_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(position_label)
        
        self.x_display = QLCDNumber()
        self.x_display.setStyleSheet(LCD_NUMBER_STYLE)
        self.x_display.setDigitCount(7)
        layout.addWidget(self.x_display)
        
        self.y_display = QLCDNumber()
        self.y_display.setStyleSheet(LCD_NUMBER_STYLE)
        self.y_display.setDigitCount(7)
        layout.addWidget(self.y_display)
        
        self.z_display = QLCDNumber()
        self.z_display.setStyleSheet(LCD_NUMBER_STYLE)
        self.z_display.setDigitCount(7)
        layout.addWidget(self.z_display)
        
        # Health Indicators (Example)
        health_label = QLabel("System Health")
        health_label.setStyleSheet(LABEL_STYLE)
        layout.addWidget(health_label)
        
        self.health_bar = QProgressBar()
        self.health_bar.setStyleSheet(GAUGE_STYLE)
        self.health_bar.setMaximum(100)
        self.health_bar.setValue(100)
        layout.addWidget(self.health_bar)
        
        self.setLayout(layout)
    
    @pyqtSlot(dict)
    def update_telemetry(self, data):
        """
        Slot to receive and display telemetry data.
        
        Args:
            data (dict): Telemetry data containing orientation and position.
        """
        orientation = data.get('orientation', {})
        position = data.get('position', {})
        health = data.get('health', 100)
        
        # Update orientation displays
        self.pitch_display.display(orientation.get('pitch', 0.0))
        self.yaw_display.display(orientation.get('yaw', 0.0))
        self.roll_display.display(orientation.get('roll', 0.0))
        
        # Update position displays
        self.x_display.display(position.get('x', 0.0))
        self.y_display.display(position.get('y', 0.0))
        self.z_display.display(position.get('z', 0.0))
        
        # Update health indicator
        self.health_bar.setValue(health)