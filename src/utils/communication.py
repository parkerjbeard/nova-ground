from src.utils.data_parser import parse_telemetry_data
from src.utils.logger import logger
from src.backend.cplusplus_bindings import backend, Command, BackendMode
from typing import Dict, Any, Optional


class CommunicationError(Exception):
    pass


class RocketLinkInterface:
    """
    Interface for communication with the rocket backend.
    Uses the new backend bindings with automatic fallback to simulation mode.
    """
    
    def __init__(self):
        self.connection_established = False

    def initialize_connection(self) -> None:
        """
        Establishes and configures the connection with the RocketLink backend.
        Automatically falls back to simulation mode if real backend is unavailable.
        """
        try:
            # Backend is already initialized in cplusplus_bindings module
            status = backend.get_connection_status()
            self.connection_established = status["connected"]
            
            if self.connection_established:
                mode_str = "real backend" if status["backend_available"] else "simulation mode"
                logger.log_event(f"RocketLink connection established ({mode_str})", "INFO")
            else:
                raise CommunicationError("Failed to establish backend connection")
                
        except Exception as e:
            logger.log_event(f"Error initializing RocketLink connection: {str(e)}", "ERROR")
            raise CommunicationError(f"Failed to initialize RocketLink connection: {str(e)}")

    def send_command(self, command: Command) -> None:
        """
        Sends commands to the rocket via the RocketLink backend.

        :param command: Command enum representing the command to send
        """
        if not self.connection_established:
            raise CommunicationError("Connection not established. Call initialize_connection() first.")

        try:
            success = backend.send_command(command)
            if not success:
                raise CommunicationError(f"Failed to send command: {command.name}")
                
        except Exception as e:
            logger.log_event(f"Error sending command: {str(e)}", "ERROR")
            raise CommunicationError(f"Failed to send command: {str(e)}")

    def receive_telemetry(self) -> Dict[str, Any]:
        """
        Receives and returns telemetry data from the RocketLink backend.

        :return: Dictionary containing parsed telemetry data
        """
        if not self.connection_established:
            raise CommunicationError("Connection not established. Call initialize_connection() first.")

        try:
            telemetry_data = backend.receive_telemetry()
            if telemetry_data is None:
                raise CommunicationError("Failed to receive telemetry data")
            
            # Log the telemetry data
            logger.log_telemetry(telemetry_data)
            
            # Parse if needed (backend already returns parsed data in new implementation)
            if isinstance(telemetry_data, str):
                telemetry_data = parse_telemetry_data(telemetry_data)
                
            return telemetry_data
            
        except Exception as e:
            logger.log_event(f"Error receiving telemetry: {str(e)}", "ERROR")
            raise CommunicationError(f"Failed to receive telemetry: {str(e)}")

    def close_connection(self) -> None:
        """
        Gracefully terminates the connection with the backend.
        """
        if not self.connection_established:
            return

        try:
            backend.close_connection()
            self.connection_established = False
            logger.log_event("RocketLink connection closed", "INFO")
            
        except Exception as e:
            logger.log_event(f"Error closing RocketLink connection: {str(e)}", "ERROR")
            raise CommunicationError(f"Failed to close RocketLink connection: {str(e)}")
    
    def get_connection_mode(self) -> str:
        """
        Get the current connection mode (real or simulation).
        
        :return: String describing the connection mode
        """
        status = backend.get_connection_status()
        return "Real Backend" if status["backend_available"] else "Simulation Mode"
    
    def is_simulation_mode(self) -> bool:
        """
        Check if running in simulation mode.
        
        :return: True if in simulation mode, False if using real backend
        """
        status = backend.get_connection_status()
        return not status["backend_available"]


# Global RocketLinkInterface instance
rocket_link = RocketLinkInterface()