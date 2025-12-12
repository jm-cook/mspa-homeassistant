# Release Notes

## v2.1.0

This release addresses the MSpa hardware's tendency to reset to Fahrenheit and default settings after power cycles, providing automatic temperature unit management and state restoration.

### 🌡️ Temperature Unit Control
- **Temperature Unit Selector**: New select entity to choose between Celsius and Fahrenheit
  - Intuitive dropdown selection (no more ON/OFF confusion)
  - Direct control over MSpa's temperature_unit setting (0=Celsius, 1=Fahrenheit)
  - Integrated with adaptive polling for fast confirmation
- **Automatic Unit Tracking**: Optional feature to automatically set temperature unit based on Home Assistant's unit system
  - Enable via integration configuration options
  - Automatically applies when MSpa powers on
  - Eliminates manual unit switching after power outages

### 🔄 State Restoration After Power Outage
- **Power Cycle Detection**: Automatically detects when MSpa is powered off and on using the `is_online` field
- **State Saving**: Captures current state before power loss:
  - Temperature unit (Celsius/Fahrenheit)
  - Target temperature
  - Heater state
  - Filter state
  - Ozone state
  - UVC state
- **Automatic Restoration**: Optionally restores saved states when power returns
  - Enable via integration configuration options
  - Restores temperature unit first, then temperature, then features
  - Includes delays between commands for reliable execution
  - Eliminates need to manually reconfigure after power outages

### 🔧 Technical Improvements
- **Dynamic Climate Unit**: Climate entity now uses dynamic temperature_unit from device payload instead of static TEMP_UNIT constant
- **Enhanced Coordinator**: Added power cycle detection and state restoration logic with is_online tracking
- **API Extension**: Added `set_temperature_unit(unit)` method to mspa_api for temperature unit control

### 📝 Configuration Options
Two new optional settings available in integration configuration (⚙️ cog wheel):
1. **Track temperature unit based on Home Assistant unit system**: Automatically sets MSpa unit to match HA
2. **Restore previous states after power outage**: Automatically restores settings when MSpa powers back on

**Upgrade Notes**: 
- After upgrading, you'll see a new "Temperature Unit" selector in your MSpa entities
- Visit the integration configuration to enable automatic unit tracking and/or state restoration if desired
- These features are disabled by default to maintain backward compatibility

---

## v2.0.0

This major release introduces multi-region support and comprehensive energy monitoring capabilities for your MSpa hot tub.

### 🌍 Multi-Region Support (Experimental)
- **Auto-detection**: Automatically selects the correct regional API endpoint based on your Home Assistant country setting
- **Regional endpoints**: Support for ROW (Rest of World/Europe), US (United States/Canada), and CH (China/Hong Kong/Macau)
- **Manual override**: Ability to manually select your region during setup if auto-detection is incorrect
- **Fallback protection**: Defaults to ROW (Europe) region for maximum compatibility
- Region endpoints identified from the [openHAB MSpa binding](https://github.com/weymann/openhab-addons/tree/main/bundles/org.openhab.binding.mspa)

**Note**: Multi-region support is experimental. While the ROW region is well-tested, US and CH regions have had limited testing. User feedback is welcomed!

### ⚡ Power and Energy Monitoring
- **Individual power sensors**: Separate sensors for pump, bubble blower, and heater power consumption
- **Total power sensor**: Automatically calculates combined power usage with component breakdown in attributes
- **Energy dashboard integration**: Built-in total energy sensor (kWh) compatible with Home Assistant's Energy dashboard
- **Configurable power values**: Customize power consumption values for each component to match your specific hot tub model
- **Persistent tracking**: Energy consumption persists across Home Assistant restarts
- **Accurate calculation**: Uses trapezoidal integration for precise energy measurements
- Default values based on MSpa Comfort C-BE061 specifications (60W pump, 900W bubbles, 1500W/2000W heater)

### 🚀 Adaptive Polling
- **Smart polling**: Automatically increases polling frequency to 1 second when changes are pending or during preheat
- **Timeout protection**: Returns to normal 60-second polling after 15 seconds
- **Improved responsiveness**: Faster state updates when you make changes through Home Assistant
- **Reduced API load**: Normal polling during idle periods to minimize unnecessary API calls

### 🔧 Improvements
- **Better offline detection**: Entities now correctly show as unavailable when the hot tub is offline
- **HVAC action states**: Added `preheating` state to climate entity for better heating status visibility
- **Robust input handling**: Improved username/password handling to strip leading/trailing whitespace from copy/paste operations

### 📝 Documentation
- Comprehensive documentation for power/energy monitoring with calibration guide
- Multi-region setup instructions with visual guides
- Updated screenshots with meaningful filenames
- Configuration instructions with emoji indicators

**Breaking Changes**: None - this release is fully backward compatible with v1.x configurations.

**Upgrade Notes**: 
- After upgrading, visit the integration configuration (⚙️ cog wheel) to set custom power consumption values if desired
- Add the Total Energy sensor to your Energy dashboard for consumption tracking
- If outside Europe, verify the correct region is selected in the integration configuration

---

## v1.0.11

- Improved username and password handling to be more robust with whitespace from copy/paste operations
- Enhanced diagnostic logging for authentication and token management
- Minor bug fixes and stability improvements

---

## v1.0.10

This release brings improved reliability and usability to the MSPA Home Assistant integration.

- Improved error handling and logging for API failures and connection issues.
- Updated documentation to reflect new features and configuration options.
- Minor bug fixes and performance improvements.

---

## v1.0.9

- Improved diagnostic sensors: filter status, heater timer, and fault sensors now available (diagnostic entities are disabled by default).
- Improved device info and entity naming for better Home Assistant integration.
- Minor bug fixes and code cleanup.
- Included `hvac_actions` in the climate entity.

**Note:**
If you are upgrading, please review the new diagnostic entities in the entity registry and enable them if needed. For best security, use a guest account as described in the documentation.

---

## Future Releases

- [Placeholder for future release notes]

