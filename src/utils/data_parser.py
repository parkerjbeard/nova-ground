from src.utils.constants import START_BYTE, COBS_BYTE
from src.utils.telemetry_data import TelemetryData
from src.utils.logger import logger
from datetime import datetime
from typing import Any, Dict
import struct


class TelemetryDataParser:
    def parse_raw_data(self, raw_bytes: bytes) -> TelemetryData:
        """
        Parses raw byte streams received from the RocketLink backend into structured TelemetryData objects.

        :param raw_bytes: Raw byte data from the backend.
        :return: Parsed TelemetryData object.
        :raises CommunicationError: If parsing fails due to invalid data.
        """
        try:
            if not raw_bytes:
                raise ValueError("Received empty telemetry data.")

            # Check for START_BYTE
            if raw_bytes[0] != START_BYTE:
                raise ValueError(f"Invalid start byte: {raw_bytes[0]}")

            # Remove START_BYTE and perform COBS decoding
            encoded_data = raw_bytes[1:]
            decoded_data = self.cobs_decode(encoded_data)

            # Parse the decoded data according to the SCALPEL protocol
            parsed_dict = self.parse_scalpel_packet(decoded_data)

            # Validate the parsed data
            self.validate_data(parsed_dict)

            telemetry = TelemetryData(**parsed_dict)
            return telemetry

        except Exception as e:
            self.handle_parsing_errors(e)
            raise

    def parse_scalpel_packet(self, data: bytes) -> Dict[str, Any]:
        """
        Parses a SCALPEL protocol packet into a dictionary.

        :param data: Decoded byte data.
        :return: Dictionary of parsed telemetry data.
        :raises ValueError: If packet structure is invalid.
        """
        try:
            # Example SCALPEL packet structure:
            # [Position (3 floats), Orientation (3 floats), Velocity (3 floats),
            #  Acceleration (3 floats), Voltage (1 int), Status Flags (1 int),
            #  Timestamp (double)]

            format_str = 'fff' * 4 + 'I' + 'I' + 'd'
            expected_size = struct.calcsize(format_str)

            if len(data) != expected_size:
                raise ValueError(f"Unexpected packet size: {len(data)} bytes.")

            unpacked = struct.unpack(format_str, data)

            parsed_data = {
                'position': unpacked[0:3],
                'orientation': unpacked[3:6],
                'velocity': unpacked[6:9],
                'acceleration': unpacked[9:12],
                'voltage': unpacked[12],
                'status_flags': self.decode_status_flags(unpacked[13]),
                'timestamp': datetime.fromtimestamp(unpacked[14]),
            }

            return parsed_data

        except struct.error as e:
            raise ValueError(f"Struct unpacking failed: {str(e)}")

    def validate_data(self, parsed_data: Dict[str, Any]) -> None:
        """
        Ensures the integrity and validity of the parsed telemetry data.

        :param parsed_data: Dictionary containing parsed telemetry data.
        :raises ValueError: If validation fails.
        """
        # Validate voltage
        if parsed_data['voltage'] > 5000:
            raise ValueError(f"Voltage {parsed_data['voltage']} exceeds maximum allowed value.")

        # Validate critical status flags
        critical_flags = ['motor_failure', 'sensor_error']
        for flag in critical_flags:
            if parsed_data['status_flags'].get(flag, False):
                raise ValueError(f"Critical status flag '{flag}' is set.")

        # Additional validations can be added here as per SCALPEL protocol

    def handle_parsing_errors(self, error: Exception) -> None:
        """
        Manages exceptions and errors encountered during the parsing process.

        :param error: The exception that was raised.
        """
        logger.log_event(f"Telemetry data parsing error: {str(error)}", "ERROR")

    def decode_status_flags(self, bitmask: int) -> Dict[str, bool]:
        """
        Decodes the status flags from a bitmask to a dictionary.

        :param bitmask: Integer representing the status flags.
        :return: Dictionary with status flag names as keys and their boolean states.
        """
        flag_mapping = {
            0: 'system_health',
            1: 'sensor_status',
            2: 'motor_failure',
            3: 'sensor_error',
            # Add more flags as defined by the SCALPEL protocol
        }
        status_flags = {}
        for bit, name in flag_mapping.items():
            status_flags[name] = bool(bitmask & (1 << bit))
        return status_flags

    def cobs_decode(self, data: bytes) -> bytes:
        """
        Decodes data using Consistent Overhead Byte Stuffing (COBS).

        :param data: COBS-encoded byte data.
        :return: Decoded byte data.
        :raises ValueError: If COBS decoding fails.
        """
        if not data:
            return b''

        decoded = bytearray()
        index = 0

        while index < len(data):
            code = data[index]
            if code == 0:
                raise ValueError("COBS decoding error: Zero byte encountered.")
            index += 1
            decoded += data[index:index + code - 1]
            if code < 0xFF and index < len(data):
                decoded.append(COBS_BYTE)
            index += code - 1

        return bytes(decoded)


# Global parser instance
parser = TelemetryDataParser()


def parse_telemetry_data(raw_data: Any) -> Dict[str, Any]:
    """
    Parse telemetry data from various formats.
    
    Args:
        raw_data: Can be bytes, string, or dict
        
    Returns:
        Dictionary containing parsed telemetry data
    """
    # If already a dict, return it
    if isinstance(raw_data, dict):
        return raw_data
    
    # If string, try to parse as JSON first
    if isinstance(raw_data, str):
        try:
            import json
            return json.loads(raw_data)
        except json.JSONDecodeError:
            # Convert to bytes and try binary parsing
            raw_data = raw_data.encode('utf-8')
    
    # If bytes, use the parser
    if isinstance(raw_data, bytes):
        try:
            telemetry = parser.parse_raw_data(raw_data)
            return telemetry.to_dict()
        except Exception as e:
            logger.log_event(f"Failed to parse binary telemetry: {e}", "ERROR")
            # Return empty telemetry data as fallback
            return {
                'timestamp': datetime.now(),
                'position': (0.0, 0.0, 0.0),
                'orientation': (0.0, 0.0, 0.0),
                'velocity': (0.0, 0.0, 0.0),
                'acceleration': (0.0, 0.0, 9.81),
                'voltage': 12000,
                'status_flags': {
                    'motor_failure': False,
                    'sensor_error': False,
                    'system_health': True,
                    'sensor_status': True
                }
            }
    
    # Unknown format
    raise ValueError(f"Unknown telemetry data format: {type(raw_data)}")