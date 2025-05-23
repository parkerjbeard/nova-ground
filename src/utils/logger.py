from src.utils.constants import LOG_DIR, TELEMETRY_LOG_FILE, EVENT_LOG_FILE, LOG_LEVEL
from datetime import datetime
from typing import Dict, Any
import logging

class Logger:
    def __init__(self):
        # Ensure log directory exists before setting up loggers
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        self.telemetry_logger = self._setup_logger('telemetry', TELEMETRY_LOG_FILE)
        self.event_logger = self._setup_logger('event', EVENT_LOG_FILE)

    def _setup_logger(self, name: str, log_file: str) -> logging.Logger:
        logger = logging.getLogger(name)
        logger.setLevel(LOG_LEVEL)

        file_handler = logging.FileHandler(LOG_DIR / log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def log_telemetry(self, data: Dict[str, Any]) -> None:
        """
        Logs incoming telemetry data.
        
        :param data: Dictionary containing telemetry data
        """
        timestamp = datetime.now().isoformat()
        telemetry_str = f"{timestamp} - {data}"
        self.telemetry_logger.info(telemetry_str)

    def log_event(self, event: str, level: str = 'INFO') -> None:
        """
        Logs significant system events or errors.
        
        :param event: Description of the event
        :param level: Log level (INFO, WARNING, ERROR, CRITICAL)
        """
        log_method = getattr(self.event_logger, level.lower())
        log_method(event)

    def configure_logging(self) -> None:
        """
        Sets up logging configurations such as log levels, formats, and destinations.
        """
        # Ensure log directory exists
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        # Configure root logger
        logging.basicConfig(level=LOG_LEVEL)

        # Add console handler to both loggers for real-time monitoring
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)

        self.telemetry_logger.addHandler(console_handler)
        self.event_logger.addHandler(console_handler)

        self.log_event("Logging system initialized")

# Global logger instance
logger = Logger()
