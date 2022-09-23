The smjx file in this example contains the gps pdop and absolute maximum sysclock error lambda where

lambda = abs(theta) + epsilon + delta / 2

See [RFC 5905](https://www.rfc-editor.org/rfc/rfc5905) for definition of these parameters.

Timing parameters are obtained using `chronyc tracking`.

PDOP obtained from the gps via gpsd.

```
{
    "duration": 8.0,
    "firmwareVersion": "ECO2105rc13-10.0.13.78533-1p5",
    "friendlyName": "SCP-00-BNG-8319",
    "friendlyNumber": -1,
    "geolocation": {
        "elevation": 246.110218750725,
        "latitude": 41.290157,
        "longitude": -82.22648
    },
    "lambda": 2.4072e-05,
    "pdop": 2.0,
    "recordStatus": -1,
    "sensorType": "Scepter2",
    "serialNumber": "SCP-00-BNG-8319",
    "spoolFormat": 10,
    "startTimeUTC": "2022-10-19T18:10:15.000Z",
    (...)
```