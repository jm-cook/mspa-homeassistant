# Custom Component Installation via HACS

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
    - Click **Download**.
    - Now restart homeassistant to load the new integration.

2. **Install the Integration:**
    - After adding the repository, search for the custom component in HACS.
    - Click **Install**.

3. **Restart Home Assistant:**
    - Go to **Settings** > **System** > **Restart** to apply the changes.

4. **Configure the Integration:**
    - Follow the documentation or configuration instructions specific to this component.

## Obtaining `device_id` and `product_id`

To control your MSPA hot tub, you will need the `device_id` and `product_id` associated with your device. Follow these steps to obtain them from the MSPA Link app:

1. Open the MSPA Link app on your mobile device and log in.
2. Go to the device list and select your hot tub.
3. Tap the device settings or information icon (found in the top left corner).
4. At the bottom of the main screen you will see the `device_id` displayed as a long alphanumeric string. Note this down ready to configure the integration.
5. To obtain the `product_id` you may need to look in the data on your network returned to the app when sending commands.
5. Note down these values for use in the integration configuration.

## Configuration

After installation, you will need to configure the integration in Home Assistant. Before carrying out these steps it is recommended to 
create a guest account on the MSPA Link app to avoid using your main account credentials.

1. Go to **Settings** > **Devices & Services**.
2. Click on **Add Integration**.
3. Search for **mspa** and select it.
4. Enter the required information:
   - `device_id`: The device ID you obtained from the MSPA Link app.
   - `product_id`: The product ID you obtained from the MSPA Link app.
   - `account_email`: Your guest email for the MSPA account.
   - `password`: The MSPA account password for the guest user.
5. Click **Submit** to complete the configuration.

![img.png](img/img.png)

## Troubleshooting

- Make sure you are running the latest version of HACS.
- Check the Home Assistant logs for any errors if the component does not load.

## Support

For issues or feature requests, please open an issue in this repository.