"""
C++ Backend Bindings Module

This module provides the interface between the Python GUI and the C++ backend.
It includes both real backend integration and a simulation mode for development/testing.
"""

import ctypes
import json
import random
import time
import threading
from typing import Dict, Any, Optional
from pathlib import Path
from enum import Enum
import logging

from src.utils.constants import ROCKETLINK_LIB_PATH
from src.utils.logger import logger


class BackendMode(Enum):
    REAL = "real"
    SIMULATION = "simulation"


class Command(Enum):
    START_MISSION = 1
    ABORT_MISSION = 2
    REQUEST_TELEMETRY = 3
    CALIBRATE_SENSORS = 4
    PAUSE_MISSION = 5
    RESUME_MISSION = 6


class BackendBindings:
    """
    Provides interface to C++ backend with automatic fallback to simulation mode.
    """
    
    def __init__(self, mode: BackendMode = BackendMode.REAL):
        self.mode = mode
        self.backend_lib = None
        self.is_connected = False
        self.simulation_thread = None
        self.simulation_running = False
        self.simulation_data = self._initialize_simulation_data()
        self._lock = threading.Lock()
        
        # Try to initialize real backend, fallback to simulation if it fails
        if mode == BackendMode.REAL:
            try:
                self._initialize_real_backend()
            except Exception as e:
                logger.log_event(f"Failed to initialize real backend: {e}. Falling back to simulation mode.", "WARNING")
                self.mode = BackendMode.SIMULATION
        
        if self.mode == BackendMode.SIMULATION:
            self._initialize_simulation()
    
    def _initialize_simulation_data(self) -> Dict[str, Any]:
        """Initialize simulation data with realistic values."""
        return {
            "timestamp": time.time(),
            "position": [0.0, 0.0, 0.0],  # x, y, z in meters
            "orientation": [0.0, 0.0, 0.0],  # pitch, yaw, roll in degrees
            "velocity": [0.0, 0.0, 0.0],  # vx, vy, vz in m/s
            "acceleration": [0.0, 0.0, 9.81],  # ax, ay, az in m/s^2
            "voltage": 12000,  # millivolts
            "status_flags": {
                "motor_failure": False,
                "sensor_error": False,
                "system_health": True,
                "sensor_status": True
            },
            "mission_state": "idle",  # idle, launching, ascending, descending, landed
            "altitude": 0.0,
            "max_altitude": 0.0,
            "flight_time": 0.0,
            "mission_start_time": None
        }
    
    def _initialize_real_backend(self):
        """Initialize connection to real C++ backend library."""
        if not Path(ROCKETLINK_LIB_PATH).exists():
            raise FileNotFoundError(f"RocketLink library not found at {ROCKETLINK_LIB_PATH}")
        
        self.backend_lib = ctypes.CDLL(ROCKETLINK_LIB_PATH)
        
        # Define function signatures
        self.backend_lib.initialize.restype = ctypes.c_int
        self.backend_lib.send_command.argtypes = [ctypes.c_int]
        self.backend_lib.send_command.restype = ctypes.c_int
        self.backend_lib.receive_telemetry.restype = ctypes.c_char_p
        self.backend_lib.close_connection.restype = ctypes.c_int
        
        # Initialize connection
        result = self.backend_lib.initialize()
        if result != 0:
            raise RuntimeError("Failed to initialize backend connection")
        
        self.is_connected = True
        logger.log_event("Real backend connection established", "INFO")
    
    def _initialize_simulation(self):
        """Initialize simulation mode."""
        self.is_connected = True
        self.simulation_running = True
        self.simulation_thread = threading.Thread(target=self._simulation_loop, daemon=True)
        self.simulation_thread.start()
        logger.log_event("Simulation mode initialized", "INFO")
    
    def _simulation_loop(self):
        """Main simulation loop that updates telemetry data."""
        while self.simulation_running:
            with self._lock:
                self._update_simulation_data()
            time.sleep(0.1)  # 10 Hz update rate
    
    def _update_simulation_data(self):
        """Update simulation data based on current mission state."""
        data = self.simulation_data
        current_time = time.time()
        
        if data["mission_state"] == "launching":
            # Simulate launch acceleration
            data["acceleration"][2] = 30.0 + random.uniform(-2, 2)  # ~3g acceleration
            data["velocity"][2] += data["acceleration"][2] * 0.1
            data["position"][2] += data["velocity"][2] * 0.1
            data["altitude"] = data["position"][2]
            
            # Add some lateral movement
            data["position"][0] += random.uniform(-0.1, 0.1)
            data["position"][1] += random.uniform(-0.1, 0.1)
            
            # Update orientation (slight wobble)
            data["orientation"][0] += random.uniform(-1, 1)
            data["orientation"][1] += random.uniform(-1, 1)
            data["orientation"][2] += random.uniform(-0.5, 0.5)
            
            # Transition to ascending after burn
            if current_time - data["mission_start_time"] > 3.0:  # 3 second burn
                data["mission_state"] = "ascending"
        
        elif data["mission_state"] == "ascending":
            # Coasting phase
            data["acceleration"][2] = -9.81  # Gravity only
            data["velocity"][2] += data["acceleration"][2] * 0.1
            data["position"][2] += data["velocity"][2] * 0.1
            data["altitude"] = data["position"][2]
            
            # Track max altitude
            if data["altitude"] > data["max_altitude"]:
                data["max_altitude"] = data["altitude"]
            
            # Transition to descending at apogee
            if data["velocity"][2] <= 0:
                data["mission_state"] = "descending"
        
        elif data["mission_state"] == "descending":
            # Falling with drag
            data["acceleration"][2] = -9.81 + 2.0  # Gravity minus drag
            data["velocity"][2] += data["acceleration"][2] * 0.1
            data["position"][2] += data["velocity"][2] * 0.1
            data["altitude"] = data["position"][2]
            
            # Land when altitude reaches 0
            if data["altitude"] <= 0:
                data["altitude"] = 0
                data["position"][2] = 0
                data["velocity"] = [0.0, 0.0, 0.0]
                data["acceleration"] = [0.0, 0.0, 0.0]
                data["mission_state"] = "landed"
        
        # Update timestamp and flight time
        data["timestamp"] = current_time
        if data["mission_start_time"] and data["mission_state"] != "idle":
            data["flight_time"] = current_time - data["mission_start_time"]
        
        # Simulate battery drain
        if data["mission_state"] != "idle":
            data["voltage"] -= random.uniform(0.5, 1.5)
            data["voltage"] = max(data["voltage"], 10000)  # Min 10V
        
        # Random sensor glitches (rare)
        if random.random() < 0.001:
            data["status_flags"]["sensor_error"] = True
        else:
            data["status_flags"]["sensor_error"] = False
    
    def send_command(self, command: Command) -> bool:
        """
        Send command to backend (real or simulated).
        
        Args:
            command: Command enum to send
            
        Returns:
            bool: True if command was successful
        """
        if not self.is_connected:
            logger.log_event("Cannot send command: not connected", "ERROR")
            return False
        
        try:
            if self.mode == BackendMode.REAL:
                result = self.backend_lib.send_command(command.value)
                success = result == 0
            else:
                # Simulate command handling
                success = self._handle_simulation_command(command)
            
            if success:
                logger.log_event(f"Command sent successfully: {command.name}", "INFO")
            else:
                logger.log_event(f"Command failed: {command.name}", "ERROR")
            
            return success
            
        except Exception as e:
            logger.log_event(f"Error sending command {command.name}: {e}", "ERROR")
            return False
    
    def _handle_simulation_command(self, command: Command) -> bool:
        """Handle commands in simulation mode."""
        with self._lock:
            if command == Command.START_MISSION:
                if self.simulation_data["mission_state"] == "idle":
                    self.simulation_data["mission_state"] = "launching"
                    self.simulation_data["mission_start_time"] = time.time()
                    self.simulation_data["flight_time"] = 0.0
                    self.simulation_data["max_altitude"] = 0.0
                    return True
                return False
            
            elif command == Command.ABORT_MISSION:
                self.simulation_data["mission_state"] = "idle"
                self.simulation_data["velocity"] = [0.0, 0.0, 0.0]
                self.simulation_data["acceleration"] = [0.0, 0.0, 9.81]
                return True
            
            elif command == Command.CALIBRATE_SENSORS:
                # Reset orientation
                self.simulation_data["orientation"] = [0.0, 0.0, 0.0]
                return True
            
            elif command == Command.PAUSE_MISSION:
                # In real system, this might pause data recording
                return True
            
            elif command == Command.RESUME_MISSION:
                # In real system, this might resume data recording
                return True
            
            return True
    
    def receive_telemetry(self) -> Optional[Dict[str, Any]]:
        """
        Receive telemetry data from backend.
        
        Returns:
            Dict containing telemetry data or None if error
        """
        if not self.is_connected:
            return None
        
        try:
            if self.mode == BackendMode.REAL:
                raw_data = self.backend_lib.receive_telemetry()
                if raw_data is None:
                    return None
                # Parse the raw data (assuming JSON format)
                telemetry_data = json.loads(raw_data.decode('utf-8'))
            else:
                # Return copy of simulation data
                with self._lock:
                    telemetry_data = self.simulation_data.copy()
            
            return telemetry_data
            
        except Exception as e:
            logger.log_event(f"Error receiving telemetry: {e}", "ERROR")
            return None
    
    def close_connection(self):
        """Close connection to backend."""
        if self.mode == BackendMode.REAL and self.backend_lib:
            try:
                self.backend_lib.close_connection()
            except Exception as e:
                logger.log_event(f"Error closing backend connection: {e}", "ERROR")
        
        if self.mode == BackendMode.SIMULATION:
            self.simulation_running = False
            if self.simulation_thread:
                self.simulation_thread.join(timeout=1.0)
        
        self.is_connected = False
        logger.log_event("Backend connection closed", "INFO")
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get current connection status and mode."""
        return {
            "connected": self.is_connected,
            "mode": self.mode.value,
            "backend_available": self.mode == BackendMode.REAL
        }
    
    def __del__(self):
        """Cleanup on deletion."""
        if self.is_connected:
            self.close_connection()


# Global backend instance with automatic mode selection
backend = BackendBindings()