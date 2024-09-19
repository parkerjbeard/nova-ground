from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, 
                             QGridLayout, QTabWidget, QTextEdit)
from .styles import BUTTON_STYLE, LABEL_STYLE
from pyqtgraph import PlotWidget, mkPen
from PyQt5.QtCore import pyqtSignal
import numpy as np

class MissionControlPanel(QWidget):
    """
    MissionControlPanel class inheriting from QWidget.
    Provides user controls for mission management.
    """
    # Update signals
    launch_mission = pyqtSignal()
    abort_mission = pyqtSignal()
    arm_system = pyqtSignal()
    disarm_system = pyqtSignal()
    
    def __init__(self, parent=None):
        super(MissionControlPanel, self).__init__(parent)
        self.max_data_points = 1000  # Adjust this value based on your needs
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Add status label
        self.status_label = QLabel("Status: N/A")
        self.status_label.setStyleSheet(LABEL_STYLE)
        main_layout.addWidget(self.status_label)

        # Create tabs for main and secondary data
        tab_widget = QTabWidget()
        tab_widget.addTab(self.create_main_telemetry_tab(), "Main Telemetry")
        tab_widget.addTab(self.create_secondary_telemetry_tab(), "Secondary Telemetry")
        
        main_layout.addWidget(tab_widget)
        
        # Control buttons
        control_layout = QHBoxLayout()
        
        # Arm Button
        self.arm_button = QPushButton("Arm System")
        self.arm_button.setStyleSheet(BUTTON_STYLE)
        self.arm_button.clicked.connect(self.arm_system.emit)
        control_layout.addWidget(self.arm_button)
        
        # Disarm Button
        self.disarm_button = QPushButton("Disarm System")
        self.disarm_button.setStyleSheet(BUTTON_STYLE)
        self.disarm_button.clicked.connect(self.disarm_system.emit)
        control_layout.addWidget(self.disarm_button)
        
        # Launch Button
        self.launch_button = QPushButton("Launch Mission")
        self.launch_button.setStyleSheet(BUTTON_STYLE)
        self.launch_button.clicked.connect(self.launch_mission.emit)
        control_layout.addWidget(self.launch_button)
        
        # Abort Button
        self.abort_button = QPushButton("Abort Mission")
        self.abort_button.setStyleSheet(BUTTON_STYLE + "background-color: #ff4444;")
        self.abort_button.clicked.connect(self.abort_mission.emit)
        control_layout.addWidget(self.abort_button)
        
        main_layout.addLayout(control_layout)
        
        self.setLayout(main_layout)
    
    def create_main_telemetry_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Telemetry grid
        telemetry_grid = QGridLayout()
        
        # Flight Phase Status
        self.flight_phase_label = QLabel("Flight Phase: N/A")
        self.flight_phase_label.setStyleSheet(LABEL_STYLE)
        telemetry_grid.addWidget(self.flight_phase_label, 0, 0)
        
        # Motor Status
        self.motor_status_label = QLabel("Motor Status: N/A")
        self.motor_status_label.setStyleSheet(LABEL_STYLE)
        telemetry_grid.addWidget(self.motor_status_label, 0, 1)
        
        # GPS Position
        self.gps_position_label = QLabel("GPS: N/A")
        self.gps_position_label.setStyleSheet(LABEL_STYLE)
        telemetry_grid.addWidget(self.gps_position_label, 1, 0)
        
        # Battery Voltage
        self.battery_voltage_label = QLabel("Battery: N/A")
        self.battery_voltage_label.setStyleSheet(LABEL_STYLE)
        telemetry_grid.addWidget(self.battery_voltage_label, 1, 1)
        
        layout.addLayout(telemetry_grid)
        
        # Graphs
        self.altitude_graph = self.create_graph("Altitude (m)")
        self.velocity_graph = self.create_graph("Vertical Velocity (m/s)")
        self.acceleration_graph = self.create_graph("Acceleration (G)")
        
        layout.addWidget(self.altitude_graph)
        layout.addWidget(self.velocity_graph)
        layout.addWidget(self.acceleration_graph)
        
        tab.setLayout(layout)
        return tab

    def create_secondary_telemetry_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        # Secondary telemetry grid
        secondary_grid = QGridLayout()

        self.rate_of_climb_label = QLabel("Rate of Climb/Descent: N/A")
        secondary_grid.addWidget(self.rate_of_climb_label, 0, 0)

        self.barometric_altitude_label = QLabel("Barometric Altitude: N/A")
        secondary_grid.addWidget(self.barometric_altitude_label, 0, 1)

        self.telemetry_latency_label = QLabel("Telemetry Latency: N/A")
        secondary_grid.addWidget(self.telemetry_latency_label, 1, 0)

        self.power_metrics_label = QLabel("Power Metrics: N/A")
        secondary_grid.addWidget(self.power_metrics_label, 1, 1)

        self.radio_metrics_label = QLabel("Radio Metrics: N/A")
        secondary_grid.addWidget(self.radio_metrics_label, 2, 0)

        layout.addLayout(secondary_grid)

        # System Logs
        self.system_logs = QTextEdit()
        self.system_logs.setReadOnly(True)
        layout.addWidget(QLabel("System Logs:"))
        layout.addWidget(self.system_logs)

        tab.setLayout(layout)
        return tab

    def create_graph(self, title):
        graph = PlotWidget(title=title)
        graph.setBackground('w')
        graph.setLabel('left', title)
        graph.setLabel('bottom', 'Time (s)')
        graph.showGrid(x=True, y=True)
        return graph
    
    def update_status(self, status):
        """
        Updates the flight status indicator.
        
        Args:
            status (str): Current mission status.
        """
        self.status_label.setText(f"Status: {status}")
    
    def update_connectivity(self, connected):
        """
        Updates the connectivity indicator.
        
        Args:
            connected (bool): Connectivity status.
        """
        status = "Connected" if connected else "Disconnected"
        self.connectivity_label.setText(f"Connectivity: {status}")
    
    def update_telemetry(self, data):
        # Update main telemetry
        # ... existing code ...

        # Update secondary telemetry
        self.rate_of_climb_label.setText(f"Rate of Climb/Descent: {data.get('rate_of_climb', 'N/A')} m/s")
        self.barometric_altitude_label.setText(f"Barometric Altitude: {data.get('barometric_altitude', 'N/A')} m")
        self.telemetry_latency_label.setText(f"Telemetry Latency: {data.get('telemetry_latency', 'N/A')} ms")
        self.power_metrics_label.setText(f"Power Metrics: {data.get('power_metrics', 'N/A')}")
        self.radio_metrics_label.setText(f"Radio Metrics: {data.get('radio_metrics', 'N/A')}")

        # Update system logs
        if 'system_logs' in data:
            self.system_logs.append(data['system_logs'])

    def update_graph(self, graph, x, y):
        if not hasattr(graph, 'data_line'):
            graph.data_line = graph.plot(pen=mkPen('b', width=2))
            graph.data = {'x': np.zeros(self.max_data_points), 'y': np.zeros(self.max_data_points)}

        # Roll the data arrays to make room for new data
        graph.data['x'] = np.roll(graph.data['x'], -1)
        graph.data['y'] = np.roll(graph.data['y'], -1)

        # Add new data point
        graph.data['x'][-1] = x
        graph.data['y'][-1] = y

        # Update the plot data
        graph.data_line.setData(graph.data['x'], graph.data['y'])

        # Adjust X axis range to show all data
        graph.setXRange(max(0, x - self.max_data_points), x)