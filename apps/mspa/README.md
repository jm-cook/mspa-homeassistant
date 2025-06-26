# MSpa Hot Tub AppDaemon Integration

This AppDaemon app provides integration between Home Assistant and MSpa hot tubs using the MSpa API. It allows you to monitor and control your hot tub through Home Assistant.

## Prerequisites

- Home Assistant with AppDaemon installed
- Python 3.x
- MSpa hot tub with Wi-Fi capability
- `hot_tub.py` script (MSpa API interface)

## Installation

1. Copy the `mspa.py` file to your AppDaemon apps directory:
   ```
   config/appdaemon/apps/mspa/mspa.py
   ```

2. Add the following configuration to your `apps.yaml`:
   ```yaml
   mspa_hot_tub:
     module: mspa
     class: MSpaHotTub
     script_path: /path/to/your/hot_tub.py
   ```

   Replace `/path/to/your/hot_tub.py` with the actual path to your `hot_tub.py` script. An example would be:
   ```yaml
   mspa_hot_tub:
     module: mspa
     class: MSpaHotTub
     script_path: /homeassistant/appdaemon/apps/mspa/hot_tub.py   


# MSPA Hot Tub Control for AppDaemon

## Dependencies

This app requires the `python-dotenv` package to manage environment variables. To install it, you'll need to add it to your AppDaemon's Python packages.

### Installation

1. Add python-dotenv to your AppDaemon's configuration. Edit your `appdaemon.yaml` file and add:2. Restart AppDaemon to install the new package.

## Configuration

1. Create a `.env` file in your AppDaemon's `apps/mspa` directory:
   bash ACCOUNT_EMAIL=your_email@example.com PASSWORD=your_password_md5_hash DEVICE_ID=your_device_id PRODUCT_ID=your_product_id

2. Make sure the `.env` file has appropriate permissions:
   - AppDaemon user should have read access
   - Recommended: `chmod 600 .env` to restrict access to owner only

3. In your `apps.yaml`, include the path to your mspa application:
## Available Entities

The app creates the following entities in Home Assistant:

### Sensors
- `sensor.mspa_water_temperature`: Current water temperature
- `sensor.mspa_target_temperature`: Target temperature setting
- `binary_sensor.mspa_heater`: Heater status (on/off)
- `binary_sensor.mspa_filter`: Filter status (on/off)
- `binary_sensor.mspa_bubble`: Bubble feature status (on/off)
- `binary_sensor.mspa_jet`: Jet feature status (on/off)

All sensors are automatically updated every minute.

## Services

The app provides the following services that can be called from Home Assistant:

### Set Temperature
   ```yaml
   service: appdaemon.mspa/set_temperature
   data:
     temperature: 38  # Temperature in degrees (Celsius)
   ```

### Control Heater
```yaml
service: appdaemon.mspa/heater
data:
state: "on"  # or "off"
```

### Control Bubble Feature
```yaml
service: appdaemon.mspa/bubble
data:
  state: "on"  # or "off"
```

### Control Jet feature
```yaml
service: appdaemon.mspa/jet
data:
  state: "on"  # or "off"
```

### Control Filter
```yaml
# Turn on heater at specific time
automation:
  - alias: "Turn on hot tub heater in the morning"
    trigger:
      platform: time
      at: "06:00:00"
    action:
      - service: appdaemon.mspa/heater
        data:
          state: "on"
      - service: appdaemon.mspa/set_temperature
        data:
          temperature: 38
```

```yaml
# Turn off features when the water temperature is too low
automation:
  - alias: "Safety shutdown on low temperature"
    trigger:
      platform: numeric_state
      entity_id: sensor.mspa_water_temperature
      below: 10
    action:
      - service: appdaemon.mspa/heater
        data:
          state: "off"
      - service: appdaemon.mspa/bubble
        data:
          state: "off"
```

## Troubleshooting
1. Check AppDaemon logs for any error messages
2. Verify that the in your configuration points to the correct location `script_path`
3. Ensure AppDaemon has permission to execute the script `hot_tub.py`
4. Verify that the MSpa API script is working correctly by running it manually

## Notes
- Temperature values are handled in Celsius
- The app polls the hot tub status every minute
- All commands are executed through the script `hot_tub.py`
- The app creates and updates entities automatically in Home Assistant

## Support
If you encounter any issues:
1. Check the AppDaemon logs
2. Verify your configuration
3. Test the script independently `hot_tub.py`
4. Ensure your hot tub is connected to Wi-Fi and accessible

This documentation provides comprehensive information about setting up and using the MSpa Hot Tub AppDaemon integration, including installation instructions, available features, example automations, and troubleshooting tips.
