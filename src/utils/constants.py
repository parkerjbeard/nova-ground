from pathlib import Path
import os

# Telemetry Configuration
UPDATE_INTERVAL_MS = 100
DATA_FORMAT = 'AVC_SCALPEL'

# File Paths
# Use user's home directory for logs to avoid permission issues
LOG_DIR = Path.home() / '.novoground' / 'logs'
TELEMETRY_LOG_FILE = 'telemetry.log'
EVENT_LOG_FILE = 'events.log'
CONFIG_FILE_PATH = Path.home() / '.novoground' / 'config.yaml'

# Communication Parameters
RADIO_MODULE = 'XBeePro900HP'
PACKET_TIMEOUT = 5  # seconds

# Thresholds and Flags
MAX_VOLTAGE = 5000  # millivolts
CRITICAL_STATUS_FLAGS = ['motor_failure', 'sensor_error']

# Protocol-Specific Constants
START_BYTE = 170
COBS_BYTE = 0x00

# Logging Configuration
LOG_LEVEL = 'INFO'

# RocketLink Library Path
ROCKETLINK_LIB_PATH = '/usr/local/lib/librocketlink.so'

# 3D Model Configuration
ROCKET_MODEL_PATH = Path('/usr/share/novoground/models/rocket.obj')
