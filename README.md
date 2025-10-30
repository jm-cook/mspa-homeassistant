# MSpa Custom Component Integration and Installation via HACS

[![hacs][hacs-badge]][hacs-url]
![Maintenance][maintenance-badge]
[![release][release-badge]][release-url]
![downloads][downloads-badge]



This repository contains a custom Home Assistant component. You can easily install it using [HACS](https://hacs.xyz/).

## Overview

This custom Home Assistant integration implements a device to control an MSPA hot tub.  
It allows users to monitor and control various functions of their MSPA hot tub directly from Home Assistant, enabling automation and remote management.

Key features:
- Turn the hot tub on or off
- Adjust temperature settings
- Control bubbles and filtration
- Monitor current status and temperature

Refer to the installation and configuration instructions below to get started.

## Installation

1. **Add this repository to HACS:**
    - In Home Assistant, go to **HACS**.
    - Click the three dots in the top right and select **Custom repositories**.
    - Enter the URL of this repository and select **Integration** as the category.
    - Click **ADD**.

2. **Install the Integration:**
    - After adding the repository, search for the custom component "MSPA Hot Tub integration" in HACS.
    - Click **Download** in the 3-dots menu, or click on the entry in HACS and click the blue **DOWNLOAD** button.

3. **Restart Home Assistant:**
    - Go to **Settings** > **System** > **Restart** to apply the changes.
    - Alternatively Home Assistant will provide a "repair" in settings that you may click on to restart Home Assistant. 

4. **Configure the Integration:**
    - Follow the documentation or configuration instructions specific to this component below.



## Configuration

After installation, you will need to configure the integration in Home Assistant. Before carrying out these steps it is recommended to 
create a guest account on the MSPA Link app to avoid using your main account credentials. Refer to the article here 
to create a guest account: [Creating a Guest Account in the MSPA Link App](MSPA_LINK.md).

To configure the MSPA integration in Home Assistant:

1. Go to **Settings** > **Devices & Services**.
2. Click on **Add Integration**.
3. Search for **mspa** and select it.
4. Enter the required information:
    - `email`: Your guest email for the MSPA account.
    - `password`: The MSPA account password for the guest user.

    ![img.png](img/img3.png)

5. Click **Submit** to complete the configuration.
6. If the registration is successful, you will see your device and some entities for monitoring and controlling it.
7. You can now add the entities to your dashboard or use them in automations.

   - **Example Entities:**
     - `switch.mspa_hot_tub_heater`: To turn the hot tub on or off.
     - `sensor.mspa_hot_tub_water_temperature`: To monitor the current temperature.
     - `sensor.mspa_hot_tub_heater_power`: To monitor the current power consumption.
     - `switch.mspa_hot_tub_bubbles`: To control the bubbles.
     - `switch.mspa_hot_tub_filter`: To control the filtration system.
     - `sensor.mspa_hot_tub_fault`: To monitor the current fault status.

## Integration page

![img.png](img/img6.png)

## Device page

![img.png](img/img.png)

## Enabling the Filter status Sensor

If your MSpa device supports filter status monitoring, a `Filter status` sensor will be available in Home Assistant after installing or upgrading this integration.  
By default, diagnostic sensors like the Filter state sensor are disabled in the entity registry. It should state in
the manual for your mspa whether your mspa supports filter status monitoring.

To enable it:

1. Go to **Settings** > **Devices & Services** > **Entities** in Home Assistant.
2. Search for `Filter status` under your MSpa device.
3. Click the `Filter status` sensor and enable it.

The Filter status sensor will show `OK` when the filter is clean, and `Dirty` if the filter needs to be changed (when the warning code is `A0`).

## Heating action (hvac_action)

The integration also provides `hvac_action` as part of the climate sensor that indicates the current heating state of the hot tub.
The climate entity will show the following states:
- `off`: The hot tub is turned off.
- `idle`: The hot tub is on but not actively heating. This would normally be the state when the water is at or above the desired temperature.
- `heating`: The hot tub is actively heating the water.

## Heater Power Sensor

The integration provides a `Heater Power` sensor that reports the current power consumption of the heater in watts. This sensor allows you to:
- Monitor real-time power usage based on the heating state
- Create energy consumption tracking using Home Assistant's built-in Riemann Sum Integral helper
- Set up automations based on power consumption

The sensor reports power consumption based on the heater state:
- **Preheat mode**: 1500W
- **Heating mode**: 2000W
- **Idle mode**: 0W
- **Heater off**: 0W

### Creating an Energy Sensor

To track total energy consumption, you can create a Riemann Sum Integral helper:

1. Go to **Settings** > **Devices & Services** > **Helpers**
2. Click **Create Helper** and select **Riemann sum integral**
3. Configure the helper:
   - **Input sensor**: Select your `Heater Power` sensor
   - **Name**: Choose a name like "Hot Tub Energy"
   - **Integration method**: Left
   - **Precision**: 2
   - **Metric prefix**: k (kilo)
   - **Time unit**: Hours
4. Click **Submit**

This will create an energy sensor that shows total energy consumption in kWh, which you can add to your Energy dashboard or use in automations.

## Thermostat popup

![img.png](img/img2.png)

## Example dashboard using mushroom cards:

![img.png](img/img7.png)

## Limitations

- **Regional Restriction:** The integration currently only works with MSPA installations in the European region. Installations outside Europe are not supported at this time.
- It is not currently possible to determine which features your specific MSPA hot tub supports. If you find that some features, such as jet or ozone, do not work, it may be due to the specific model of your hot tub. You can disable the relevant entities in the Home Assistant UI.
- The safety lock feature is not available in this integration. You can still operate the safety lock through the MSPA Link app.


## Troubleshooting

- Make sure you are running the latest version of HACS.
- Check the Home Assistant logs for any errors if the component does not load.
- Ensure that you have created and are using a guest account for Home Assistant with its own email and password in the MSPA Link app.
- you can only have one mspa integration per Home Assistant instance. If you have multiple MSPA hot tubs, you will need to set up separate instances of Home Assistant for each one.


## Support

For issues or feature requests, please open an issue in this repository.

<!-- Badges -->
[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=flat-square
[release-badge]: https://img.shields.io/github/v/release/jm-cook/mspa-homeassistant?style=flat-square
[downloads-badge]: https://img.shields.io/github/downloads/jm-cook/mspa-homeassistant/total?style=flat-square
[hacs-url]: https://github.com/hacs/integration

[maintenance-badge]: https://img.shields.io/maintenance/yes/2025.svg?style=flat-square
[release-url]: https://github.com/jm-cook/mspa-homeassistant/releases
