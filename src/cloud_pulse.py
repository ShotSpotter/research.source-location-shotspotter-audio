"""
Zac Plett 07/24/2018 - ShotSpotter

cloud_pulse.py: This class will be fed JSON data from the array of pulses and convert each pulse
                into a cloud_pulse object.

Usage: Keep this file in your working directory and add:
       from cloud_pulse import cloud_pulse
"""

from dateutil.parser import parse
import uuid

import conversion as utm
from location_pulse import location_pulse


class cloud_pulse:

    def __init__(self, json_data):
        # The JSON data
        self.json_data = json_data
        # Sets class variables given the input fields
        self.pulse_id = uuid.UUID(json_data["pulseId"])
        self.serial_number = json_data["serialNumber"]
        self.arrival_time = json_data["arrivalTime"]
        self.location = {"latitude": json_data["location"]["latitude"],
                         "longitude": json_data["location"]["longitude"],
                         "elevation": json_data["location"]["elevation"]}

    """
    Converts cloud_pulse object to a location_pulse object. 
    """
    def cloud_to_location(self):
        # Converts the ISO 8601 arrival time to a python datetime object.
        arrival_time_obj = parse(self.arrival_time)
        # Converts the lat / lon coordinates to UTM before creating the location pulse.
        return location_pulse(self.pulse_id, self.serial_number, arrival_time_obj, 
                              utm.from_latlon(self.location["latitude"], 
                              self.location["longitude"]), self.location["elevation"])
