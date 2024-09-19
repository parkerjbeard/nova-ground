from src.utils.constants import LOG_DIR, TELEMETRY_LOG_FILE
from src.utils.telemetry_data import TelemetryData
from PyQt5.QtCore import QObject, pyqtSignal
from src.utils.logger import logger
import threading
import time
import csv


class DataPlayback(QObject):
    """
    Provides functionality to replay logged telemetry data.
    """
    playback_started = pyqtSignal()
    playback_stopped = pyqtSignal()
    telemetry_emitted = pyqtSignal(object)  # Emits TelemetryData objects

    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.log_file_path = LOG_DIR / TELEMETRY_LOG_FILE
        self.playback_thread = None
        self._is_playing = False
        self._playback_speed = 1.0  # 1x speed
        self._current_index = 0
        self.telemetry_data = []

    def load_log(self) -> bool:
        """
        Loads telemetry data from the log file.

        :return: True if loading is successful, False otherwise.
        """
        if not self.log_file_path.exists():
            logger.log_event(f"Log file {self.log_file_path} does not exist.", "ERROR")
            return False

        try:
            with open(self.log_file_path, mode='r') as csvfile:
                reader = csv.DictReader(csvfile)
                self.telemetry_data = []
                for row in reader:
                    telemetry = TelemetryData(
                        position=(float(row['position_x']), float(row['position_y']), float(row['position_z'])),
                        orientation=(float(row['orientation_pitch']), float(row['orientation_yaw']), float(row['orientation_roll'])),
                        velocity=(float(row['velocity_x']), float(row['velocity_y']), float(row['velocity_z'])),
                        acceleration=(float(row['acceleration_x']), float(row['acceleration_y']), float(row['acceleration_z'])),
                        voltage=int(row['voltage']),
                        status_flags={
                            'motor_failure': row['motor_failure'].lower() == 'true',
                            'sensor_error': row['sensor_error'].lower() == 'true',
                            'system_health': row['system_health'].lower() == 'true',
                            'sensor_status': row['sensor_status'].lower() == 'true',
                        },
                        timestamp=None  # Timestamp can be handled separately if needed
                    )
                    self.telemetry_data.append(telemetry)
            logger.log_event(f"Loaded {len(self.telemetry_data)} telemetry records from {self.log_file_path}", "INFO")
            return True
        except Exception as e:
            logger.log_event(f"Failed to load telemetry log: {str(e)}", "ERROR")
            return False

    def start_playback(self) -> None:
        """
        Starts the playback of telemetry data.
        """
        if self._is_playing:
            logger.log_event("Data playback is already in progress.", "WARNING")
            return

        if not self.telemetry_data:
            logger.log_event("No telemetry data loaded for playback.", "WARNING")
            return

        self._is_playing = True
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.playback_thread.start()
        self.playback_started.emit()
        logger.log_event("Data playback started.", "INFO")

    def _playback_loop(self) -> None:
        """
        Internal method to handle the playback loop.
        """
        try:
            previous_timestamp = None
            for telemetry in self.telemetry_data:
                if not self._is_playing:
                    break

                current_timestamp = telemetry.timestamp or time.time()
                if previous_timestamp:
                    # Calculate time difference and adjust sleep based on playback speed
                    time_diff = current_timestamp - previous_timestamp
                    adjusted_sleep = time_diff / self._playback_speed
                    if adjusted_sleep > 0:
                        time.sleep(adjusted_sleep)
                previous_timestamp = current_timestamp

                self.telemetry_emitted.emit(telemetry)
            self.stop_playback()
            logger.log_event("Data playback completed.", "INFO")
        except Exception as e:
            logger.log_event(f"Error during data playback: {str(e)}", "ERROR")
            self.stop_playback()

    def stop_playback(self) -> None:
        """
        Stops the telemetry data playback.
        """
        if not self._is_playing:
            logger.log_event("Data playback is not active.", "WARNING")
            return

        self._is_playing = False
        if self.playback_thread and self.playback_thread.is_alive():
            self.playback_thread.join()
        self.playback_thread = None
        self.playback_stopped.emit()
        logger.log_event("Data playback stopped.", "INFO")

    def set_playback_speed(self, speed: float) -> None:
        """
        Sets the playback speed.

        :param speed: Playback speed multiplier (e.g., 2.0 for double speed).
        """
        if speed <= 0:
            logger.log_event("Playback speed must be positive.", "WARNING")
            return
        self._playback_speed = speed
        logger.log_event(f"Playback speed set to {self._playback_speed}x.", "INFO")