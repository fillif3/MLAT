# -*- mode: python; indent-tabs-mode: nil -*-

# Part of mlat-server: a Mode S multilateration server
# Copyright (C) 2015  Oliver Jowett <oliver@mutability.co.uk>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
The bit where all the magic happens: take a list of receive timestamps and
produce a position.
"""

import math

import scipy.optimize

import geodesy
#import constants
MIN_NUC = 6

# absolute maximum receiver range for sync messages, metres
MAX_RANGE = 500e3

# maximum distance between even/odd DF17 messages, metres
MAX_INTERMESSAGE_RANGE = 10e3

# absolute maximum altitude, metres
MAX_ALT = 50000 * 0.3038

# how long to wait to accumulate messages before doing multilateration, seconds
MLAT_DELAY = 2.5

# maxfev (maximum function evaluations) for the solver
SOLVER_MAXFEV = 50000000

Cair = 299792458 / 1.0003


# The core of it all. Not very big, is it?
# (Admittedly the entire least-squares solver is hidden within scipy..)

#glogger = logging.getLogger("solver")


def _residuals(x_guess, pseudorange_data, altitude, altitude_error,base_time):
    """Return an array of residuals for a position guess at x_guess versus
    actual measurements pseudorange_data and altitude."""

    position_guess = x_guess

    res = []

    # compute pseudoranges at the current guess vs. measured pseudorange
    for receiver_position, pseudorange, error in pseudorange_data:
        pseudorange_guess = geodesy.ecef_distance(receiver_position, position_guess)
        res.append((pseudorange - pseudorange_guess) / error)

    # compute altitude at the current guess vs. measured altitude
    if altitude is not None:
        _, _, altitude_guess = geodesy.ecef2llh(position_guess)
        res.append((altitude - altitude_guess) / altitude_error)

    return res


def solveKnownTime(measurements, altitude, altitude_error, initial_guess,base_timestamp):
    """Given a set of receive timestamps, multilaterate the position of the transmitter.
    measurements: a list of (receiver, timestamp, error) tuples. Should be sorted by timestamp.
      receiver.position should be the ECEF position of the receiver
      timestamp should be a reception time in seconds (with an arbitrary epoch)
      variance should be the estimated variance of timestamp
    altitude: the reported altitude of the transmitter in _meters_, or None
    altitude_error: the estimated error in altitude in meters, or None
    initial_guess: an ECEF position to start the solver from
    Returns None on failure, or (ecef, ecef_cov) on success, with:
    ecef: the multilaterated ECEF position of the transmitter
    ecef_cov: an estimate of the covariance matrix of ecef
    """

    if len(measurements) + (0 if altitude is None else 1) < 3:
        raise ValueError('Not enough measurements available')

    pseudorange_data = [(receiver.position,
                         (timestamp - base_timestamp) * Cair,
                         math.sqrt(variance) * Cair)
                        for receiver, timestamp, variance in measurements]
    x_guess = [initial_guess[0], initial_guess[1], initial_guess[2]]
    x_est, cov_x, infodict, mesg, ler = scipy.optimize.leastsq(
        _residuals,
        x_guess,
        args=(pseudorange_data, altitude, altitude_error,base_timestamp),
        full_output=True,
        maxfev=SOLVER_MAXFEV)

    if ler in (1, 2, 3, 4):
        #glogger.info("solver success: {0} {1}".format(ler, mesg))

        # Solver found a result. Validate that it makes
        # some sort of physical sense.
        position_est= x_est


       # if offset_est < 0 or offset_est > MAX_RANGE:
            #glogger.info("solver: bad offset: {0}".formaT(offset_est))
            # implausible range offset to closest receiver
       #     return None, None

        #for receiver, timestamp, variance in measurements:
        #    d = geodesy.ecef_distance(receiver.position, position_est)
        #    if d > MAX_RANGE:
                # too far from this receiver
                #glogger.info("solver: bad range: {0}".format(d))
        #        return None, None

        if cov_x is None:
            return position_est, None
        else:
            return position_est, cov_x[0:3, 0:3]

    else:
        # Solver failed
        #glogger.info("solver: failed: {0} {1}".format(ler, mesg))
        return None, None


