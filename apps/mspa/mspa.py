import hassapi as hass
import json
import subprocess
from datetime import datetime, timedelta
from datetime import UTC as dtUTC
import os

class MSpaHotTub(hass.Hass):
    """AppDaemon app for controlling MSpa hot tub."""
    
    def initialize(self):
        """Initialize the app."""
        self.log("Initializing MSpa Hot Tub App")
        
        # Path to the hot_tub.py script
        self.script_path = self.args.get("script_path", "hot_tub.py")
        
        # Register callbacks for services
        self.register_service("mspa/set_temperature", self.set_temperature)
        self.register_service("mspa/heater", self.heater_control)
        self.register_service("mspa/bubble", self.bubble_control)
        self.register_service("mspa/jet", self.jet_control)
        self.register_service("mspa/filter", self.filter_control)
        self.log(f"script_path {self.script_path}:  {os.path.isfile(self.script_path)}")
        # Set up periodic status update
        # self.run_every(self.update_status, "now", 60)  # Update every minute
        self.run_every(self.update_status, datetime.now()+timedelta(seconds=5), 600)


    def _run_command(self, command):
        """Run hot_tub.py with specified command."""
        try:
            result = subprocess.run(
                ["python3", self.script_path, command],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except Exception as e:
            self.log(f"Error running command {command}: {str(e)}", level="ERROR")
            return None
    
    def update_status(self, kwargs):
        """Update hot tub status in Home Assistant."""
        status = self._run_command("status")
        if status:
            # Update sensor states
            self.set_state("sensor.mspa_water_temperature", 
                          state=status["water_temperature"] / 2)
            self.set_state("sensor.mspa_target_temperature", 
                          state=status["temperature_setting"] / 2)
            self.set_state("binary_sensor.mspa_heater", 
                          state="on" if status["heater_state"] else "off")
            self.set_state("binary_sensor.mspa_filter", 
                          state="on" if status["filter_state"] else "off")
            self.set_state("binary_sensor.mspa_bubble", 
                          state="on" if status["bubble_state"] else "off")
            self.set_state("binary_sensor.mspa_jet", 
                          state="on" if status["jet_state"] else "off")
    
    def set_temperature(self, entity, attribute, old, new, kwargs):
        """Set hot tub temperature."""
        temp = float(kwargs.get("temperature", 0))
        # Convert to API format (multiply by 2)
        temp_setting = int(temp * 2)
        result = self._run_command(f"set_temp {temp_setting}")
        if result and result.get("code") == 0:
            self.log(f"Temperature set to {temp}°C")
    
    def heater_control(self, entity, attribute, old, new, kwargs):
        """Control heater."""
        command = "heater_on" if kwargs.get("state") == "on" else "heater_off"
        result = self._run_command(command)
        if result and result.get("code") == 0:
            self.log(f"Heater turned {kwargs.get('state')}")
    
    def bubble_control(self, entity, attribute, old, new, kwargs):
        """Control bubble feature."""
        command = "bubble_on" if kwargs.get("state") == "on" else "bubble_off"
        result = self._run_command(command)
        if result and result.get("code") == 0:
            self.log(f"Bubble turned {kwargs.get('state')}")
    
    def jet_control(self, entity, attribute, old, new, kwargs):
        """Control jet feature."""
        command = "jet_on" if kwargs.get("state") == "on" else "jet_off"
        result = self._run_command(command)
        if result and result.get("code") == 0:
            self.log(f"Jet turned {kwargs.get('state')}")
    
    def filter_control(self, entity, attribute, old, new, kwargs):
        """Control filter."""
        command = "filter_on" if kwargs.get("state") == "on" else "filter_off"
        result = self._run_command(command)
        if result and result.get("code") == 0:
            self.log(f"Filter turned {kwargs.get('state')}")