from dataclasses import dataclass, field
from typing import Tuple, Dict, Any
from datetime import datetime



@dataclass
class TelemetryData:
    """
    Represents structured telemetry data received from the RocketLink C++ backend.
    """
    position: Tuple[float, float, float]
    orientation: Tuple[float, float, float]
    velocity: Tuple[float, float, float]
    acceleration: Tuple[float, float, float]
    voltage: int
    status_flags: Dict[str, bool]
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def update(self, new_data: Dict[str, Any]) -> None:
        """
        Updates the telemetry data attributes with new values received from the backend.

        :param new_data: Dictionary containing new telemetry data.
        :raises KeyError: If an invalid attribute is provided.
        """
        for key, value in new_data.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise KeyError(f"TelemetryData has no attribute named '{key}'")

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the telemetry data into a dictionary format for easier manipulation and logging.

        :return: Dictionary representation of the telemetry data.
        """
        return {
            'position': self.position,
            'orientation': self.orientation,
            'velocity': self.velocity,
            'acceleration': self.acceleration,
            'voltage': self.voltage,
            'status_flags': self.status_flags,
            'timestamp': self.timestamp.isoformat(),
        }