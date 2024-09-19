from src.utils.data_parser import parse_telemetry_data
from src.utils.constants import ROCKETLINK_LIB_PATH
from src.utils.logger import logger
from typing import Dict, Any
from enum import Enum
import ctypes




class Command(Enum):
    START_MISSION = 1
    ABORT_MISSION = 2
    REQUEST_TELEMETRY = 3
    CALIBRATE_SENSORS = 4

class CommunicationError(Exception):
    pass

class RocketLinkInterface:
    def __init__(self):
        self.rocketlink_lib = None
        self.connection_established = False

    def initialize_connection(self) -> None:
        """
        Establishes and configures the connection with the RocketLink backend.
        """
        try:
            self.rocketlink_lib = ctypes.CDLL(ROCKETLINK_LIB_PATH)
            self.rocketlink_lib.initialize.restype = ctypes.c_int
            self.rocketlink_lib.send_command.argtypes = [ctypes.c_int]
            self.rocketlink_lib.send_command.restype = ctypes.c_int
            self.rocketlink_lib.receive_telemetry.restype = ctypes.c_char_p
            self.rocketlink_lib.close_connection.restype = ctypes.c_int

            result = self.rocketlink_lib.initialize()
            if result != 0:
                raise CommunicationError("Failed to initialize RocketLink connection")
            
            self.connection_established = True
            logger.log_event("RocketLink connection established", "INFO")
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
            result = self.rocketlink_lib.send_command(command.value)
            if result != 0:
                raise CommunicationError(f"Failed to send command: {command.name}")
            logger.log_event(f"Command sent: {command.name}", "INFO")
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
            raw_data = self.rocketlink_lib.receive_telemetry()
            if raw_data is None:
                raise CommunicationError("Failed to receive telemetry data")
            
            telemetry_data = parse_telemetry_data(raw_data.decode('utf-8'))
            logger.log_telemetry(telemetry_data)
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
            result = self.rocketlink_lib.close_connection()
            if result != 0:
                raise CommunicationError("Failed to close RocketLink connection")
            
            self.connection_established = False
            logger.log_event("RocketLink connection closed", "INFO")
        except Exception as e:
            logger.log_event(f"Error closing RocketLink connection: {str(e)}", "ERROR")
            raise CommunicationError(f"Failed to close RocketLink connection: {str(e)}")

# Global RocketLinkInterface instance
rocket_link = RocketLinkInterface()