"""
Zac Plett 07/19/2018 - ShotSpotter
Scott Lamkin 10/03/2022 - ShotSpotter, edits

location.py: Rewritten Loc2D algorithm using multilateration in python.
             Location class operates on numpy arrays of pulse locations, corresponding arrival 
             times, and the speed of sound. Computing a location if one is possible.
"""

from datetime import datetime
from enum import Enum
import logging

import numpy as np


class Algorithm(str, Enum):
    Reddi2DPositiveRoot = "Reddi2DPositiveRoot"
    Reddi2DNegativeRoot = "Reddi2DNegativeRoot"


class location:

    def compute_speed(self, temp):
        kelvin = temp + 273.15
        speed = 20.03 * np.sqrt(kelvin)
        return speed

    """
    The main algorithm for computing a location. Takes in two corresponding arrays, one with
    numpy arrays containing the x, y, and z positions of the pulses, and another with corresponding
    arrival times of those pulses, and as a third parameter, takes in the speed of sound.
    Given a valid array of sensor data, the algorithm outputs a list of 0, 1, or 2 locations.
    0 locations will be output when there are no real roots in the solution, meaning the input data
    could not produce a viable solution. 1 or 2 locations will be output for viable solutions
    depending on the number of sensors reporting. For 4 or more there should only be 1 possible
    solution.

    The error logging will instinctively append to a file called error.log unless the user passes
    in a specific log file name. 
    """
    def loc2D(self, locations, arrivals, speed, log_name="error.log"):
        # The error log file to write to given faulty input or unwanted behavior when computing
        # potential locations
        logging.basicConfig(filename=log_name, level=logging.ERROR, filemode="a")
        # We need at least 3 pulses to compute a location, if there are fewer than 3 we throw an
        # error and return.
        if len(locations) < 3:
            error_string = "Insufficient number of pulses, 3 or more needed to compute a location. Error occurred at "\
                           "time: {0}".format(datetime.now())
            logging.error(error_string)
            # Using -1 as an error code to indicate to any outside callers that this instance could
            # not be solved for a location. 
            return -1
        output = []
        # Loc2D routine, translated from Murphey's Java code:
        m = len(locations) - 1
        rSquared = np.zeros(shape=(m, 1))
        a = np.zeros(shape=(m, 2))
        d = np.zeros(shape=(m, 1))
        w = np.zeros(shape=(m, 1))
        for i in range(m):
            tempVector = locations[i+1] - locations[0]
            rSquared[i][0] = ((tempVector[0]**2) + (tempVector[1]**2))
            a[i][0] = tempVector[0]
            a[i][1] = tempVector[1]
            d[i][0] = speed * (arrivals[i+1] - arrivals[0]).total_seconds()
            w[i][0] = float(rSquared[i][0] - (d[i][0] * d[i][0])) / 2
        A = a 
        D = d
        W = w 
        B = None
        try:
            B = np.linalg.pinv(A)
        except Exception as e:
            logging.error("Tried to invert matrix: {0} but received the following error:\n {1}".format(A, e))
        if type(B) is np.ndarray:
            C = B.dot(D) 
            Y = B.dot(W) 
            Ctran = C.T
            Ytran = Y.T
            c = (C[0, 0], C[1, 0])
            y = (Y[0, 0], Y[1, 0])
            qA = (Ctran.dot(C))[0, 0] - 1
            if qA != 0:
                qB = float(((Ctran.dot(Y)) + (Ytran.dot(C)))[0, 0])
                qC = float((Ytran.dot(Y))[0, 0])
                radicand = float(qB * qB - 4 * qA * qC)
                root = 0.0
                if radicand > 0:
                    root = radicand**(1/2)
                elif radicand < 0:
                    return output
                if qB >= 0:
                    qQ = -0.5 * (qB + root)
                    posVector = [i * (float(qC) / qQ) for i in c]
                    negVector = [i * (float(qQ) / qA) for i in c]
                else:
                    qQ = -0.5 * (qB - root)
                    posVector = [i * (float(qQ) / qA) for i in c]
                    negVector = [i * (float(qC) / qQ) for i in c]
                posVector = [sum(x) for x in zip(posVector, y)]
                posDischargeTime = datetime.utcfromtimestamp(
                    arrivals[0].timestamp() - (np.linalg.norm(posVector)/speed)).strftime('%Y-%m-%d %H:%M:%S.%f')
                negVector = [sum(x) for x in zip(negVector, y)]
                negDischargeTime = datetime.utcfromtimestamp(
                    arrivals[0].timestamp() - (np.linalg.norm(negVector)/speed)).strftime('%Y-%m-%d %H:%M:%S.%f')
                posVector = [sum(x) for x in zip(posVector, locations[0])]
                negVector = [sum(x) for x in zip(negVector, locations[0])]
                output.append((posVector, posDischargeTime, Algorithm.Reddi2DPositiveRoot))
                output.append((negVector, negDischargeTime, Algorithm.Reddi2DNegativeRoot))
        return output
