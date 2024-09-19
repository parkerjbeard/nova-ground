from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import QTimer, pyqtSlot
from pyqtgraph import PlotWidget
from .styles import GRAPH_STYLE
from collections import deque



class GraphVisualization(QWidget):
    """
    GraphVisualization class inheriting from QWidget.
    Visualizes real-time telemetry data on graphs using PyQtGraph.
    """
    def __init__(self, parent=None):
        super(GraphVisualization, self).__init__(parent)
        self.init_ui()
        self.init_graphs()
        self.init_data_buffers()
        self.init_timer()
    
    def init_ui(self):
        self.setStyleSheet(GRAPH_STYLE)
        layout = QVBoxLayout()
        
        # Pitch Graph
        self.pitch_plot = PlotWidget(title="Pitch Over Time")
        self.pitch_plot.setLabel('left', 'Pitch', units='degrees')
        self.pitch_plot.setLabel('bottom', 'Time', units='s')
        self.pitch_curve = self.pitch_plot.plot(pen='y')
        layout.addWidget(self.pitch_plot)
        
        # Yaw Graph
        self.yaw_plot = PlotWidget(title="Yaw Over Time")
        self.yaw_plot.setLabel('left', 'Yaw', units='degrees')
        self.yaw_plot.setLabel('bottom', 'Time', units='s')
        self.yaw_curve = self.yaw_plot.plot(pen='c')
        layout.addWidget(self.yaw_plot)
        
        # Roll Graph
        self.roll_plot = PlotWidget(title="Roll Over Time")
        self.roll_plot.setLabel('left', 'Roll', units='degrees')
        self.roll_plot.setLabel('bottom', 'Time', units='s')
        self.roll_curve = self.roll_plot.plot(pen='m')
        layout.addWidget(self.roll_plot)
        
        # Position Graphs
        self.x_plot = PlotWidget(title="X Position Over Time")
        self.x_plot.setLabel('left', 'X Position', units='m')
        self.x_plot.setLabel('bottom', 'Time', units='s')
        self.x_curve = self.x_plot.plot(pen='r')
        layout.addWidget(self.x_plot)
        
        self.y_plot = PlotWidget(title="Y Position Over Time")
        self.y_plot.setLabel('left', 'Y Position', units='m')
        self.y_plot.setLabel('bottom', 'Time', units='s')
        self.y_curve = self.y_plot.plot(pen='g')
        layout.addWidget(self.y_plot)
        
        self.z_plot = PlotWidget(title="Z Position Over Time")
        self.z_plot.setLabel('left', 'Z Position', units='m')
        self.z_plot.setLabel('bottom', 'Time', units='s')
        self.z_curve = self.z_plot.plot(pen='b')
        layout.addWidget(self.z_plot)
        
        self.setLayout(layout)
    
    def init_graphs(self):
        # Initialize graph parameters if needed
        pass
    
    def init_data_buffers(self):
        # Deques to store data points for each parameter
        self.time_buffer = deque(maxlen=100)
        self.pitch_buffer = deque(maxlen=100)
        self.yaw_buffer = deque(maxlen=100)
        self.roll_buffer = deque(maxlen=100)
        self.x_buffer = deque(maxlen=100)
        self.y_buffer = deque(maxlen=100)
        self.z_buffer = deque(maxlen=100)
        self.start_time = None
    
    def init_timer(self):
        # Timer to update graphs periodically
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_graphs)
        self.timer.start(100)  # Update every 100 ms
    
    @pyqtSlot(dict)
    def receive_telemetry(self, data):
        """
        Receives telemetry data and updates buffers.
        
        Args:
            data (dict): Telemetry data containing orientation and position.
        """
        import time
        if self.start_time is None:
            self.start_time = time.time()
        
        current_time = time.time() - self.start_time
        self.time_buffer.append(current_time)
        
        orientation = data.get('orientation', {})
        position = data.get('position', {})
        
        self.pitch_buffer.append(orientation.get('pitch', 0.0))
        self.yaw_buffer.append(orientation.get('yaw', 0.0))
        self.roll_buffer.append(orientation.get('roll', 0.0))
        
        self.x_buffer.append(position.get('x', 0.0))
        self.y_buffer.append(position.get('y', 0.0))
        self.z_buffer.append(position.get('z', 0.0))
    
    def update_graphs(self):
        """
        Updates the graph plots with new data from buffers.
        """
        if not self.time_buffer:
            return
        
        times = list(self.time_buffer)
        
        self.pitch_curve.setData(times, list(self.pitch_buffer))
        self.yaw_curve.setData(times, list(self.yaw_buffer))
        self.roll_curve.setData(times, list(self.roll_buffer))
        
        self.x_curve.setData(times, list(self.x_buffer))
        self.y_curve.setData(times, list(self.y_buffer))
        self.z_curve.setData(times, list(self.z_buffer))