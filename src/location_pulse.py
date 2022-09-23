"""
Zac Plett 07/24/2018 - ShotSpotter

location_pulse.py: This class is fed the converted cloud_pulse object data and this class is
                   used for location finding computations.

Usage: Keep this file in your working directory and add:
       from location_pulse import location_pulse
"""

import numpy as np


class location_pulse:
    
    def __init__(self, pulse_id, serial_number, arrival_time, utm_location, elevation):
        # Sets class variables given the input fields
        self.pulse_id = pulse_id
        self.serial_number = serial_number
        self.arrival_time = arrival_time
        self.location = np.array([utm_location[0], utm_location[1], elevation])
        self.zone_number = utm_location[2]
        self.zone_letter = utm_location[3]
        