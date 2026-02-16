# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2026-02-16

### Summary
This release significantly improves power cycle detection and state restoration, addressing the MSpa hardware's tendency to reset to Fahrenheit and default settings after power cycles.

For a complete list of all bug fixes, improvements, and detailed feature descriptions, please refer to the [full CHANGELOG on GitHub](https://github.com/DTekNO/mspa-homeassistant/blob/main/CHANGELOG.md).

### Added
- **Enhanced Power Cycle Detection** - Multiple detection methods for reliable power cycle detection
  - is_online transition detection (original method)
  - Multi-parameter change detection (catches quick power cycles)
  - Temperature unit reset detection (monitors F/C unit changes)
  - Improved logging with emoji indicators and detection method information

- **Always Enforce Temperature Unit** - New configuration option
  - Continuously enforces temperature unit on every update
  - For devices that frequently forget unit without full power cycles
  - Independent from power-cycle-only tracking option

- **State Restoration After Power Outage** - Automatic restoration of device settings
  - Saves state before power loss (temperature, heater, filter, ozone, UVC)
  - Optionally restores saved states when power returns
  - Includes delays between commands for reliable execution
  - Detailed logging of each restoration step

### Changed
- **Temperature Unit Management** - Improved temperature unit handling
  - Automatic unit tracking now optional (power-up only)
  - New "always enforce" option for continuous monitoring
  - Works independently - no manual unit selector needed
  - Both options can be used together or separately

- **Logging & Diagnostics** - Enhanced logging for troubleshooting
  - Clear power ON/OFF detection messages with emoji indicators
  - State saving confirmations with values
  - Individual restoration step status
  - Warnings for potential false positives

### Configuration
Three optional settings available in integration configuration:
1. **Track temperature unit**: Set device unit to match HA system unit on power-up
2. **Always enforce unit**: Continuously enforce temperature unit on every update
3. **Restore previous states after power outage**: Restore device states when MSpa powers back on

**Note**: All features are disabled by default to maintain backward compatibility. Visit Settings → Devices & Services → MSpa → Configure to enable new features after upgrading

---

## [2.0.0] - 2026-01

### Summary
This major release introduces multi-region support and comprehensive energy monitoring capabilities for your MSpa hot tub.

### Added
- **Multi-Region Support (Experimental)** - Support for ROW, US, and CH regions
  - Auto-detection based on Home Assistant country setting
  - Manual region override during setup
  - Regional endpoints: ROW (Europe), US (United States/Canada), CH (China/Hong Kong/Macau)
  - Fallback to ROW region for maximum compatibility
  - Region endpoints identified from [openHAB MSpa binding](https://github.com/weymann/openhab-addons/tree/main/bundles/org.openhab.binding.mspa)

- **Power and Energy Monitoring** - Comprehensive power tracking
  - Individual power sensors for pump, bubble blower, and heater
  - Total power sensor with component breakdown in attributes
  - Energy dashboard integration with built-in total energy sensor (kWh)
  - Configurable power values for each component
  - Persistent energy tracking across Home Assistant restarts
  - Trapezoidal integration for accurate energy measurements
  - Default values based on MSpa Comfort C-BE061 specifications

- **Adaptive Polling** - Smart polling frequency
  - Automatically increases to 1 second when changes pending or during preheat
  - Timeout protection returns to 60-second polling after 15 seconds
  - Improved responsiveness for state updates
  - Reduced API load during idle periods

### Changed
- **Offline Detection** - Entities now correctly show as unavailable when hot tub is offline
- **HVAC Action States** - Added `preheating` state to climate entity for better visibility
- **Input Handling** - Strips leading/trailing whitespace from username/password (copy/paste friendly)

### Documentation
- Comprehensive power/energy monitoring documentation with calibration guide
- Multi-region setup instructions with visual guides
- Updated screenshots with meaningful filenames

**Note**: Multi-region support is experimental. ROW region is well-tested; US and CH have had limited testing

---

## [1.0.11] - 2025

### Changed
- **Input Handling** - Improved username and password handling for whitespace from copy/paste
- **Logging** - Enhanced diagnostic logging for authentication and token management

### Fixed
- Minor bug fixes and stability improvements

---

## [1.0.10] - 2025

### Changed
- **Error Handling** - Improved error handling and logging for API failures and connection issues
- **Documentation** - Updated to reflect new features and configuration options

### Fixed
- Minor bug fixes and performance improvements

---

## [1.0.9] - 2025

### Added
- **Diagnostic Sensors** - Filter status, heater timer, and fault sensors (disabled by default)
- **HVAC Actions** - Included `hvac_actions` in climate entity

### Changed
- **Device Info** - Improved device info and entity naming for better Home Assistant integration

### Fixed
- Code cleanup and minor bug fixes

**Note**: If upgrading, review new diagnostic entities in the entity registry and enable if needed

