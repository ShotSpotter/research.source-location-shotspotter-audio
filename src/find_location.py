"""
Zac Plett 07/27/2018 - ShotSpotter
Scott Lamkin 09/13/2022 - ShotSpotter, edits

find_location.py: Class that takes in an array of location_pulses and coerces them to a common UTM 
                  zone and then computes their location using the loc2D algorithm.

Usage: Add this file to your working directory and then include it in your import statements with
       the following:

       from find_location import find_location

Reference: Reddi, S. S., “An Exact Solution to Range Computation with Time Delay Information for 
Arbitrary Array Geometries,” IEEE Transactions on Signal Processing, 41(1), pp. 485–486, 1993.
"""

import argparse
from dateutil.parser import parse
import json
import pathlib
import sys

import numpy as np

from cloud_pulse import cloud_pulse
import conversion as utm
from location import location
from location_pulse import location_pulse


def parse_json(file_name):
    with open(file_name) as data:
        return json.load(data)


def parse_arguments():
    parser = argparse.ArgumentParser(description=".json file generated by find_pulses.py to \
                                     locate with")
    parser.add_argument('json_path', type=pathlib.Path, help="path to .json")
    args = parser.parse_args()
    return args


class location_result:

    def __init__(self, geolocation, discharge_time, self_consistent_error, algorithm, reference_sensor):
        self.geolocation = geolocation
        self.discharge_time = discharge_time
        self.self_consistent_error = self_consistent_error
        self.algorithm = algorithm
        self.reference_sensor = reference_sensor


class find_location:

    """
    Initialization function that takes in an array of location_pulses and then calls the coerce
    operation on them.
    """
    def __init__(self, json_file):
        # Class variables
        self.json_file = json_file
        self.json = parse_json(self.json_file)
        self.json_pulses = self.json["pulses"]
        self.weather = self.json["weather"]
        self.temp = self.weather["temperature"]
        self.loc = location()
        self.speed = self.loc.compute_speed(self.temp)
        self.computed_locations = self.compute_loc2D()
        self.computed_locations.sort(key=lambda x: x.self_consistent_error)


    """
    Uses the coerced pulses and computes a location using loc2D.
    """
    def compute_loc2D(self):
        # Empty pulse and arrival time lists
        uncoerced_pulses = []
        arrivals = []
        # Iterates through the pulses loaded as json objects and creates a cloud pulse object from
        # each pulse and then a location pulse from the resulting cloud pulse. The data fields of
        # the location pulse are then loaded into the respective lists
        for pulse in self.json_pulses:
            cp = cloud_pulse(pulse)
            lp = cp.cloud_to_location()
            arrivals.append(lp.arrival_time)
            uncoerced_pulses.append(lp)
        # Coerces the pulses to a common UTM zone
        coerced_pulses = self.coerce_utm(uncoerced_pulses)
        # We take the zone letter and number from the first element in the pulses list but could
        # take them from any arbitrary element in the list as they have all been coerced to the
        # same UTM zone 
        # The common zone number
        zone_number = coerced_pulses[0].zone_number
        # The common zone letter
        zone_letter = coerced_pulses[0].zone_letter
        # The pulses we'll send to loc2D to compute
        compute_pulses = []
        for pulse in coerced_pulses:
            pulse.location[2] = 0.0
            compute_pulses.append(pulse.location)
        compute_pulses = np.array(compute_pulses)
        arrivals = np.array(arrivals)
        best_index = 0
        best_error = 10000
        for i in range(len(arrivals)):
            # The output from Loc2D
            loc2D_out = self.loc.loc2D(compute_pulses, arrivals, self.speed)
            for position_vector, discharge_time, algorithm in loc2D_out:
                easting = position_vector[0]
                northing = position_vector[1]
                elevation = 0.0
                mse_error = self.compute_mse(compute_pulses, (easting, northing, elevation), arrivals, discharge_time)
                if mse_error < best_error:
                    best_error = mse_error
                    best_index = i
            compute_pulses = np.roll(compute_pulses, 3)
            arrivals = np.roll(arrivals, 1)
        out = []
        if best_error < 10000:
            compute_pulses = np.roll(compute_pulses, 3 * best_index)
            arrivals = np.roll(arrivals, best_index)
            loc2D_out = self.loc.loc2D(compute_pulses, arrivals, self.speed)
            for position_vector, discharge_time, algorithm in loc2D_out:
                easting = position_vector[0]
                northing = position_vector[1]
                elevation = 0.0
                mse_error = self.compute_mse(compute_pulses, (easting, northing, elevation), arrivals, discharge_time)
                latlon = utm.to_latlon(easting, northing, zone_number, zone_letter)
                out.append(location_result([latlon[0], latlon[1], elevation], discharge_time, mse_error,
                                           algorithm, self.json_pulses[best_index]["serialNumber"]))
        return out 

    """
    Since some of the sensor arrays can span multiple UTM zones, we want to make sure that all of
    our calculations are done within the same UTM zone. This is done by first iterating over all
    of the UTM locations and creating a dictionary whose keys are UTM zones and values are
    individual locations. We then examine the dictionary and evaluate whether or not it has
    multiple keys. If it doesn't, then all locations correspond to one UTM zone and we're done. If
    it doesn't, then we coerce all applicable zones to the zone with the majority of the locations.
    Similarly, we must ensure that our locations are all within the same zone designator (letter),
    we replicate the same process as for UTM zones within the coercion process.
    """
    def coerce_utm(self, utm_before_coerce):
        # The dictionary to keep track of zone counts
        zone_dictionary = {}
        # The dictionary to keep track of designator counts
        designator_dictionary = {}
        # Iterates over the dictionary and adds the location <--> zone pairs
        for loc in utm_before_coerce:
            zone = loc.zone_number
            designator = loc.zone_letter
            if zone not in zone_dictionary:
                zone_dictionary[zone] = [loc]
            else:
                zone_dictionary[zone].append(loc)
            if designator not in designator_dictionary:
                designator_dictionary[designator] = [loc]
            else:
                designator_dictionary[designator].append(loc)
        # If all of our locations correspond to the same zone number and letter
        if len(zone_dictionary) == 1 and len(designator_dictionary) == 1:
            return list(zone_dictionary.values())[0]
        # Finds the UTM zone key(s) with the most values
        max_zone_count = max(len(v) for v in zone_dictionary.values())
        max_zones = [k for k, v in zone_dictionary.items() if len(v) == max_zone_count]
        # If there are multiple max zones, it doesn't matter which we choose
        max_zone = max_zones[0]
        # Finds the designator key(s) with the most values
        max_designator_count = max(len(v) for v in designator_dictionary.values())
        max_designators = [k for k, v in designator_dictionary.items() if len(v) == max_designator_count]
        # If there are multiple max designators, it doesn't matter which we choose
        max_designator = max_designators[0]
        coerced_locations = []
        # Iterates through the dictionaries entries and coerces the necessary locations,
        # ignoring those whose inherent zone are 2 or more apart from the computed max_zone value
        # and stores and returns the resulting coerced locations
        for zone in zone_dictionary.values():
            for loc in zone:
                # If this loc has the correct zone already, we just add it to the list and
                # move on
                if loc["zone_number"] == max_zone and loc["zone_letter"] == max_designator:
                    coerced_locations.append(loc)
                    continue
                # If the current loc is 2 or more UTM zones away from the coerce zone, we skip
                # this loc
                elif loc["zone_number"] == max_zone - 2 or loc["zone_number"] == max_zone + 2:
                    continue
                # Otherwise, if this loc's zone is within +/- 1 of the max_zone, we coerce it
                # and add it to the list
                else:
                    lat_lon = utm.to_latlon(loc["latitude"], loc["longitude"], loc["zone_number"], 
                                            loc["zone_letter"])
                    coerced_locations.append(location_pulse(loc["pulse_id"], loc["serial_number"], 
                                             loc["arrival_time"], utm.from_latlon(lat_lon[0], 
                                             lat_lon[1], max_zone, max_designator), 
                                             loc["elevation"]))
       
        return coerced_locations

    def compute_mse(self, compute_pulses, computed_location, arrival_times, discharge_time):
        xyz_diff = compute_pulses - np.array(computed_location)
        discharge_diffs = np.array([(a.replace(tzinfo=None)-parse(discharge_time)).total_seconds()
                                    for a in arrival_times])
        distance = np.sqrt(np.sum(np.square(xyz_diff), axis=1))
        discharge_distance = np.array([t*self.speed for t in discharge_diffs])
        diff_sum = np.square(discharge_distance-distance).sum()
        return diff_sum/discharge_distance.shape[0]


def main():
    args = parse_arguments()
    json_path = args.json_path
    location_obj = find_location(json_path)
    return json.dumps([x.__dict__ for x in location_obj.computed_locations],
                      sort_keys=True, indent=4)


if __name__ == '__main__':
    sys.exit(main())