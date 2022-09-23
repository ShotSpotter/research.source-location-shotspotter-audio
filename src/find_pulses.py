"""
Scott Lamkin 09/13/2022 - ShotSpotter

find_pulses.py: Creates .json file at json_filename containing the locations of the sensors along 
                with the user selected arrivalTime of the pulses. 

Usage: This file should only be used as a script by pointing to a folder containing ShotSpotter 
       WAV files. arrivalTime is calculated from the user entered sample number and the sample 
       rate read from the wav specification.
"""

import argparse
from datetime import datetime, timedelta
import glob as gl
import json
import os
import pathlib
import sys
import uuid
import subprocess
import platform

from find_location import find_location
import smjx_reader


json_filename = "wav_pulse_start.json"


def parse_arguments():
    parser = argparse.ArgumentParser(description="Searches in wavs_path for ShotSpotter .wav "
                                     "files, reads the smjx out of them and prepares file for "
                                     "user input.")
    parser.add_argument('wavs_path', type=pathlib.Path, help="path to folder")
    args = parser.parse_args()
    return args


"""
Iterates over globbed wav files with the expectation that the user uses Audacity as system default 
to verify the exact pulse sample they wish to define as the start of the impulse.
Only takes in one shot at a time, with expectation that you enter the impulse start sample in the 
terminal. Like production, makes the assumption of uniform weather across the array.
"""


def manually_locate_pulses(smjxs):
    pulse_sample = {"pulses": [], "weather": {}}
    for wavpath, (sr, smjx) in smjxs:
        # cross-platform way to open default app for .wav from https://stackoverflow.com/questions/434597
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', wavpath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(wavpath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', wavpath))
        user_input = input("{0} \nEnter shot impulse start sample or enter nothing to skip "
                           "file: ".format(wavpath)).split(",")
        if user_input != [""]:
            pulse = {"serialNumber": smjx["serialNumber"]}
            startTimeUTC = datetime.strptime(smjx["startTimeUTC"], "%Y-%m-%dT%H:%M:%S.%fZ")
            pulse["user_input"] = int(user_input[0])
            pulse_offset = pulse["user_input"]/sr
            offset = timedelta(seconds=pulse_offset)
            pulse["arrivalTime"] = (startTimeUTC+offset).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            pulse["location"] = smjx["geolocation"]
            pulse["pulseId"] = str(uuid.uuid3(uuid.NAMESPACE_DNS, "{0}{1}".format(wavpath.name, 
                                   pulse["arrivalTime"])))
            pulse_sample["pulses"].append(pulse)
            pulse_sample["weather"]["temperature"] = smjx["weather"]["temperature"]
            pulse_sample["weather"]["windspeed"] = smjx["weather"]["speed"]
            pulse_sample["weather"]["winddir"] = smjx["weather"]["direction"]
        with open(json_filename, "w") as f:
            f.write(json.dumps(pulse_sample, indent=4, sort_keys=True))
    return pulse_sample


def main():
    args = parse_arguments()
    gl_wavs_path = [pathlib.Path(x) for x in gl.glob(os.path.join(args.wavs_path, "*.wav"))]
    if gl_wavs_path:
        wavdata = []
        for wavpath in gl_wavs_path:
            wavdata.append((wavpath, smjx_reader.read_smjx_from_file(wavpath)))
        manually_locate_pulses(wavdata)
    loc_3d_obj = find_location(json_filename)
    return json.dumps([x.__dict__ for x in loc_3d_obj.computed_locations], sort_keys=True,
                      indent=4)


if __name__ == '__main__':
    sys.exit(main())
