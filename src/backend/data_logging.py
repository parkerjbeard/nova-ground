from src.utils.constants import LOG_DIR, TELEMETRY_LOG_FILE
from src.utils.telemetry_data import TelemetryData
from src.utils.logger import logger
import threading
import csv


class DataLogger:
    """
    Handles logging of telemetry data for post-mission analysis.
    Supports writing data to CSV format.
    """
    def __init__(self):
        self.log_file_path = LOG_DIR / TELEMETRY_LOG_FILE
        self._is_logging = False
        self._lock = threading.Lock()
        self._file = None
        self._csv_writer = None

    def start_logging(self) -> None:
        """
        Starts the telemetry data logging process.
        """
        with self._lock:
            if self._is_logging:
                logger.log_event("Data logging is already in progress.", "WARNING")
                return

            try:
                LOG_DIR.mkdir(parents=True, exist_ok=True)
                self._file = open(self.log_file_path, mode='w', newline='')
                self._csv_writer = csv.DictWriter(
                    self._file,
                    fieldnames=[
                        'timestamp',
                        'position_x',
                        'position_y',
                        'position_z',
                        'orientation_pitch',
                        'orientation_yaw',
                        'orientation_roll',
                        'velocity_x',
                        'velocity_y',
                        'velocity_z',
                        'acceleration_x',
                        'acceleration_y',
                        'acceleration_z',
                        'voltage',
                        'motor_failure',
                        'sensor_error',
                        'system_health',
                        'sensor_status'
                    ]
                )
                self._csv_writer.writeheader()
                self._is_logging = True
                logger.log_event(f"Started logging telemetry data to {self.log_file_path}", "INFO")
            except Exception as e:
                logger.log_event(f"Failed to start data logging: {str(e)}", "ERROR")
                self.stop_logging()

    def stop_logging(self) -> None:
        """
        Stops the telemetry data logging process.
        """
        with self._lock:
            if not self._is_logging:
                logger.log_event("Data logging is not active.", "WARNING")
                return

            try:
                if self._file:
                    self._file.close()
                self._is_logging = False
                logger.log_event("Stopped telemetry data logging.", "INFO")
            except Exception as e:
                logger.log_event(f"Failed to stop data logging: {str(e)}", "ERROR")

    def log_data(self, telemetry: TelemetryData) -> None:
        """
        Writes a telemetry data point to the log file.

        :param telemetry: TelemetryData object containing the data to log.
        """
        if not self._is_logging:
            return

        try:
            with self._lock:
                if not self._csv_writer:
                    raise ValueError("CSV writer is not initialized.")
                
                data_dict = telemetry.to_dict()
                # Flatten position, orientation, velocity, acceleration tuples
                flat_data = {
                    'timestamp': data_dict['timestamp'],
                    'position_x': data_dict['position'][0],
                    'position_y': data_dict['position'][1],
                    'position_z': data_dict['position'][2],
                    'orientation_pitch': data_dict['orientation'][0],
                    'orientation_yaw': data_dict['orientation'][1],
                    'orientation_roll': data_dict['orientation'][2],
                    'velocity_x': data_dict['velocity'][0],
                    'velocity_y': data_dict['velocity'][1],
                    'velocity_z': data_dict['velocity'][2],
                    'acceleration_x': data_dict['acceleration'][0],
                    'acceleration_y': data_dict['acceleration'][1],
                    'acceleration_z': data_dict['acceleration'][2],
                    'voltage': data_dict['voltage'],
                    'motor_failure': data_dict['status_flags'].get('motor_failure', False),
                    'sensor_error': data_dict['status_flags'].get('sensor_error', False),
                    'system_health': data_dict['status_flags'].get('system_health', False),
                    'sensor_status': data_dict['status_flags'].get('sensor_status', False),
                }
                self._csv_writer.writerow(flat_data)
                self._file.flush()
        except Exception as e:
            logger.log_event(f"Failed to log telemetry data: {str(e)}", "ERROR")
            self.stop_logging()