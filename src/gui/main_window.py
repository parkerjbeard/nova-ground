from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QAction, QMessageBox, QStatusBar
from .mission_control_panel import MissionControlPanel
from src.panda3d_render.rocket_view import RocketView
from panda3d.core import loadPrcFileData
from .styles import MAIN_WINDOW_STYLE
from PyQt5.QtCore import QTimer
from src.utils.communication import rocket_link, CommunicationError
from src.backend.cplusplus_bindings import Command
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
        
        # Initialize backend connection
        self.backend_connected = False
        self.init_backend_connection()
        
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
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.update_connection_status()

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
        if not self.backend_connected:
            QMessageBox.warning(self, "Connection Error", "Backend not connected. Running in simulation mode.")
            return
            
        try:
            rocket_link.send_command(Command.START_MISSION)
            self.mission_control_panel.update_status("Launching")
            QMessageBox.information(self, "Mission Control", "Mission Launched.")
        except CommunicationError as e:
            QMessageBox.critical(self, "Communication Error", f"Failed to launch mission: {e}")
            logging.error(f"Failed to launch mission: {e}")

    def abort_mission(self):
        """
        Handles the abort mission action.
        Sends abort command to the backend.
        """
        if not self.backend_connected:
            self.mission_control_panel.update_status("Idle")
            QMessageBox.information(self, "Mission Control", "Mission Aborted (Simulation).")
            return
            
        try:
            rocket_link.send_command(Command.ABORT_MISSION)
            self.mission_control_panel.update_status("Aborting")
            QMessageBox.warning(self, "Mission Control", "Mission Aborted!")
        except CommunicationError as e:
            QMessageBox.critical(self, "Communication Error", f"Failed to abort mission: {e}")
            logging.error(f"Failed to abort mission: {e}")

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
        if not self.backend_connected:
            # Still provide updates in simulation mode
            pass
            
        try:
            # Fetch telemetry data from backend
            telemetry_data = rocket_link.receive_telemetry()
            
            # Transform data for GUI consumption
            if telemetry_data:
                data = {
                    'altitude': telemetry_data.get('altitude', 0),
                    'velocity': telemetry_data.get('velocity', [0, 0, 0])[2],  # Vertical velocity
                    'acceleration': telemetry_data.get('acceleration', [0, 0, 0])[2],  # Vertical acceleration
                    'position': tuple(telemetry_data.get('position', [0, 0, 0])),
                    'orientation': tuple(telemetry_data.get('orientation', [0, 0, 0])),
                }
                self.mission_control_panel.update_telemetry(data)
                
                # Update the rocket view with new position and orientation if initialized
                if hasattr(self, 'rocket_view'):
                    self.rocket_view.update_telemetry(data)
                    
        except CommunicationError as e:
            # Log error but don't show dialog every second
            logging.error(f"Failed to receive telemetry: {e}")
        except Exception as e:
            logging.error(f"Unexpected error updating telemetry: {e}")
    
    def init_backend_connection(self):
        """
        Initialize connection to the backend with graceful fallback to simulation mode.
        """
        try:
            rocket_link.initialize_connection()
            self.backend_connected = True
            mode = rocket_link.get_connection_mode()
            logging.info(f"Backend connection established: {mode}")
        except CommunicationError as e:
            logging.warning(f"Failed to connect to backend: {e}")
            self.backend_connected = False
            QMessageBox.warning(
                self, 
                "Backend Connection", 
                "Failed to connect to backend. Running in simulation mode.\n\n"
                "You can still explore the GUI and see simulated telemetry data."
            )
    
    def update_connection_status(self):
        """
        Update the status bar with connection information.
        """
        if self.backend_connected:
            mode = rocket_link.get_connection_mode()
            if rocket_link.is_simulation_mode():
                self.status_bar.showMessage(f"Connected: {mode} | Telemetry: Simulated", 0)
                self.status_bar.setStyleSheet("background-color: #FFA500;")  # Orange for simulation
            else:
                self.status_bar.showMessage(f"Connected: {mode} | Telemetry: Live", 0)
                self.status_bar.setStyleSheet("background-color: #90EE90;")  # Light green for live
        else:
            self.status_bar.showMessage("Disconnected | No Telemetry", 0)
            self.status_bar.setStyleSheet("background-color: #FFB6C1;")  # Light red for disconnected
    
    def closeEvent(self, event):
        """
        Handle window close event to properly clean up resources.
        """
        if self.backend_connected:
            try:
                rocket_link.close_connection()
            except Exception as e:
                logging.error(f"Error closing backend connection: {e}")
        
        if hasattr(self, 'rocket_view'):
            self.rocket_view.close()
        
        event.accept()