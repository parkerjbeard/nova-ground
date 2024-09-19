from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QAction, QMessageBox
from .mission_control_panel import MissionControlPanel
from src.panda3d_render.rocket_view import RocketView
from panda3d.core import loadPrcFileData
from .styles import MAIN_WINDOW_STYLE
from PyQt5.QtCore import QTimer
import logging

class MainWindow(QMainWindow):
    """
    MainWindow class inheriting from QMainWindow.
    Combines all UI components including rocket view, telemetry dashboard, and mission control panel.
    """
    def __init__(self, rocket_model_path: str = None):
        super(MainWindow, self).__init__()
        self.setWindowTitle("NovoGround Ground Control System")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet(MAIN_WINDOW_STYLE)
        
        # Configure Panda3D to use a child window
        loadPrcFileData("", "window-type none")
        
        self.init_ui()
        self.init_menu()
        self.show()
        
        # Initialize RocketView after the event loop has processed pending events
        QTimer.singleShot(0, lambda: self.initialize_rocket_view(model_path=rocket_model_path))

        # Set up a timer to update the 3D view
        self.render_timer = QTimer(self)
        self.render_timer.timeout.connect(self.update_3d_view)
        self.render_timer.start(16)  # ~60 FPS

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Left pane: Rocket View
        self.rocket_view_widget = QWidget()
        self.rocket_view_widget.setMinimumSize(800, 600)  # Ensure the widget has a size
        main_layout.addWidget(self.rocket_view_widget, 2)
        
        # Right pane: Dashboard and Controls
        right_pane = QVBoxLayout()
        
        # Mission Control Panel (now includes all telemetry)
        self.mission_control_panel = MissionControlPanel()
        right_pane.addWidget(self.mission_control_panel)
        
        main_layout.addLayout(right_pane, 1)
        
        central_widget.setLayout(main_layout)
        
        # Connect signals from mission control to backend commands
        self.mission_control_panel.launch_mission.connect(self.launch_mission)
        self.mission_control_panel.abort_mission.connect(self.abort_mission)
        self.mission_control_panel.arm_system.connect(self.arm_system)
        self.mission_control_panel.disarm_system.connect(self.disarm_system)
        
        # Set up a timer to update telemetry periodically
        self.telemetry_timer = QTimer(self)
        self.telemetry_timer.timeout.connect(self.update_telemetry)
        self.telemetry_timer.start(1000)  # Update every 1000 ms (1 second)

    def initialize_rocket_view(self, model_path: str = None):
        """
        Initializes the RocketView after the main window has been fully shown.
        This ensures that the parent widget's window handle is valid.
        """
        try:
            parent_handle = int(self.rocket_view_widget.winId())
            logging.info(f"Initializing RocketView with parent_handle: {parent_handle}")
            
            self.rocket_view = RocketView(parent_handle=parent_handle)
            logging.info("RocketView initialized successfully")
            
            # Force an update of the 3D view
            self.rocket_view.taskMgr.step()
            logging.info("Initial render step completed")
        except Exception as e:
            logging.exception("Failed to initialize RocketView.")
            QMessageBox.critical(self, "Initialization Error", f"Failed to initialize RocketView:\n{e}")
            self.close()

    def update_3d_view(self):
        if hasattr(self, 'rocket_view'):
            self.rocket_view.taskMgr.step()

    def init_menu(self):
        # Create menu bar
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('File')
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Help Menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def show_about(self):
        QMessageBox.about(self, "About NovoGround GCS",
                          "NovoGround Ground Control System\nVersion 1.0\nDeveloped with PyQt and Panda3D.")
    
    def launch_mission(self):
        """
        Handles the launch mission action.
        Sends launch command to the backend.
        """
        # Integrate with backend to launch mission
        self.mission_control_panel.update_status("Launching")
        QMessageBox.information(self, "Mission Control", "Mission Launched.")

    def abort_mission(self):
        """
        Handles the abort mission action.
        Sends abort command to the backend.
        """
        # Integrate with backend to abort mission
        self.mission_control_panel.update_status("Aborting")
        QMessageBox.warning(self, "Mission Control", "Mission Aborted!")

    def arm_system(self):
        """
        Handles the arm system action.
        Sends arm command to the backend.
        """
        # Integrate with backend to arm system
        self.mission_control_panel.update_status("Armed")
        QMessageBox.information(self, "Mission Control", "System Armed.")

    def disarm_system(self):
        """
        Handles the disarm system action.
        Sends disarm command to the backend.
        """
        # Integrate with backend to disarm system
        self.mission_control_panel.update_status("Disarmed")
        QMessageBox.information(self, "Mission Control", "System Disarmed.")
    
    def update_telemetry(self):
        """
        Updates telemetry in mission control panel with new data.
        """
        # Fetch the latest telemetry data from your backend
        # Example dummy data
        data = {
            'altitude': 1000,
            'velocity': 200,
            'acceleration': 9.8,
            'position': (0, 1000, 0),  # x, y, z
            'orientation': (0, 0, 0),  # pitch, yaw, roll
        }
        self.mission_control_panel.update_telemetry(data)
        
        # Update the rocket view with new position and orientation if initialized
        if hasattr(self, 'rocket_view'):
            self.rocket_view.update_telemetry(data)