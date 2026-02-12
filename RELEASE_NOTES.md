# Release Notes

## v2.1.0 (February 2026)

This release significantly improves power cycle detection and state restoration, addressing the MSpa hardware's tendency to reset to Fahrenheit and default settings after power cycles.

### 🔍 Enhanced Power Cycle Detection
The integration now uses **multiple detection methods** to catch power cycles more reliably:

1. **is_online Transition Detection** (original method)
   - Detects when device goes offline and comes back online
   - Works for extended power outages

2. **Multi-Parameter Change Detection** (NEW)
   - Detects when multiple settings change simultaneously
   - Catches quick power cycles (few seconds) that might be missed by polling
   - Looks for patterns like: heater OFF + filter OFF + temperature unit reset to F
   - Helps detect brief power interruptions

3. **Temperature Unit Reset Detection** (NEW)
   - Specifically monitors for temperature unit reverting to Fahrenheit (default)
   - Common indicator of a power reset

### 🌡️ Temperature Unit Management
- **Automatic Unit Tracking**: Optional feature to set MSpa device temperature unit to match Home Assistant's system unit on power-up
  - Enable via integration configuration options
  - Works independently - no manual unit selector needed
  - Eliminates the annoyance of MSpa resetting to Fahrenheit after power outages
  
- **Always Enforce Unit** (NEW): Optional feature to continuously enforce temperature unit
  - Enable if your device frequently forgets temperature unit even without full power cycles
  - Checks and corrects unit on every update (if mismatch detected)
  - More aggressive than power-cycle-only tracking

### 🔄 State Restoration After Power Outage
- **State Saving**: Captures current state before power loss:
  - Target temperature
  - Heater state
  - Filter state
  - Ozone state
  - UVC state
  
- **Automatic Restoration**: Optionally restores saved states when power returns
  - Enable via integration configuration options (independent of temperature unit tracking)
  - Includes delays between commands for reliable execution
  - Detailed logging of each restoration step
  - Eliminates need to manually reconfigure after power outages

### 📊 Enhanced Logging & Diagnostics
All power cycle and restoration events now include:
- 🔌 Clear power ON/OFF detection messages with emoji indicators
- 💾 State saving confirmations with values
- ⚡ Detection method used (helps identify which method caught the power cycle)
- 🌡️ Temperature unit changes with clear indication
- ♨️ Individual restoration steps with success/failure status
- ⚠️ Warnings for potential false positives
- 💡 Tips for reporting issues

**Example log output:**
```
🔌 MSpa power OFF detected (is_online: True → False)
💾 Saved state for restoration: {'heater': 'on', 'target_temperature': 38.0, ...}
⚡ MSpa power ON detected via is_online transition (False → True)
🔧 Config: track_temperature_unit=True, restore_state=True
🌡️ Setting MSpa temperature unit to Celsius to match HA system
♻️ Starting state restoration after power cycle
🌡️ Restoring target temperature to 38.0°C
♨️ Restoring heater to ON
💨 Restoring filter to ON
✅ State restoration completed: temperature=38.0°C, heater=ON, filter=ON
```

### 🔧 Configuration Options
Three optional settings available in integration configuration (⚙️ cog wheel):

1. **Track temperature unit**: Set MSpa device unit to match HA system unit on power-up
2. **Always enforce unit** (NEW): Continuously enforce temperature unit on every update
3. **Restore previous states after power outage**: Restore device states when MSpa powers back on

**Upgrade Notes**: 
- After upgrading, visit Settings → Devices & Services → MSpa → Configure to enable new features
- All features are disabled by default to maintain backward compatibility
- "Always enforce unit" is independent from "Track temperature unit" - you can use either or both
- Enhanced logging helps diagnose power cycle detection issues

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

