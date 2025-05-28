# Description
A simple script for requesting the MSpa API through reverse-engineering the MSpa Link App. At the moment it does only provide a section of all possible requests.

## Usage

``python3 hot_tub.py <command>``

## Commands:
### status
Example return value: 
```json
{
  "wifivertion": 0,
  "otastatus": 0,
  "mcuversion": "",
  "trdversion": "0.0.0",
  "ConnectType": "online",
  "heater_state": 0,
  "filter_state": 0,
  "bubble_state": 0,
  "ozone_state": 0,
  "uvc_state": 0,
  "jet_state": 0,
  "temperature_unit": 0,
  "temperature_setting": 80,
  "water_temperature": 80,
  "auto_inflate": 0,
  "filter_current": 0,
  "safety_lock": 0,
  "heat_time_switch": 0,
  "heat_state": 0,
  "bubble_level": 3,
  "is_online": true,
  "fault": "",
  "warning": "",
  "device_heat_perhour": 0
}
```
Note: As the API does not use floating point numbers and works in .5 steps, temperature is represented x2.
### heater_on / heater_off
Example return value: 
```json
{
  "code": 0,
  "message": "SUCCESS",
  "request_id": "123456789012345567890",
  "data": { }
}
```
### set_temp {temp}
Note: temp must be 2x the desired temperature as the system does not allow floating point numbers. Only use .5 steps!
Example return value: 
```json
{
  "code": 0,
  "message": "SUCCESS",
  "request_id": "123456789012345567890",
  "data": { }
}
```
### bubble_on / bubble_off
Example return value: 
```json
{
  "code": 0,
  "message": "SUCCESS",
  "request_id": "123456789012345567890",
  "data": { }
}
```
### jet_on / jet_off
Example return value: 
```json
{
  "code": 0,
  "message": "SUCCESS",
  "request_id": "123456789012345567890",
  "data": { }
}
```
### filter_on / filter_off
Example return value: 
```json
{
  "code": 0,
  "message": "SUCCESS",
  "request_id": "123456789012345567890",
  "data": { }
}
```

