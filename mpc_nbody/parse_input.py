# -*- coding: utf-8 -*-
# mpc_nbody/mpc_nbody/parse_input.py

'''
----------------------------------------------------------------------------
mpc_nbody's module for parsing OrbFit + ele220 elements

Mar 2020
Mike Alexandersen & Matthew Payne

This module provides functionalities to
(a) read an OrbFit .fel/.eq file with heliocentric ecliptic cartesian els
(b) read ele220 element strings
(c) convert the above to barycentric equatorial cartesian elements

This is meant to prepare the elements for input into the n-body integrator
----------------------------------------------------------------------------
'''

# Import third-party packages
# -----------------------------------------------------------------------------
import os
import numpy as np
from mpcpp import MPC_library as mpc
from jplephem.spk import SPK

# Import neighbouring packages
# -----------------------------------------------------------------------------

# Default for caching stuff using lru_cache
# -----------------------------------------------------------------------------

# Constants and stuff
# -----------------------------------------------------------------------------
DATA_PATH = os.path.realpath(os.path.dirname(__file__))
au_km = 149597870.700 # This is now a definition

# Data classes/methods
# -----------------------------------------------------------------------------


class ParseElements():
    '''
    Class for parsing elements and returning them in the correct format.
    '''

    def __init__(self, input_file=None, filetype=None):
        #If input filename provided, process it:
        if isinstance(input_file, str):
            if filetype == 'ele220':
                self.parse_ele220(input_file)
            if (filetype == 'fel') | (filetype == 'eq'):
                self.parse_orbfit(input_file)
            self.make_bary_equatorial()
            self.save_elements()

    def _get_Covariance_List(self, Els):
        '''
        Convenience function for reading and splitting the covariance
        lines of an OrbFit file.
        Not intended for user usage.
        '''
        ElCov = []
        covErr = ""
        for El in Els:
            if El[:4] == ' COV':
                ElCov.append(El)
        if len(ElCov) == 7:
            _, c11, c12, c13 = ElCov[0].split()
            _, c14, c15, c16 = ElCov[1].split()
            _, c22, c23, c24 = ElCov[2].split()
            _, c25, c26, c33 = ElCov[3].split()
            _, c34, c35, c36 = ElCov[4].split()
            _, c44, c45, c46 = ElCov[5].split()
            _, c55, c56, c66 = ElCov[6].split()
        if len(ElCov) != 7:
            c11, c12, c13, c14, c15, c16, c22 = "", "", "", "", "", "", ""
            c23, c24, c25, c26, c33, c34, c35 = "", "", "", "", "", "", ""
            c36, c44, c45, c46, c55, c56, c66 = "", "", "", "", "", "", ""
            covErr = ' Empty covariance Matrix for '
        return (covErr, c11, c12, c13, c14, c15, c16, c22, c23, c24, c25, c26,
                c33, c34, c35, c36, c44, c45, c46, c55, c56, c66)

    def save_elements(self, output_file='holman_ic'):
        """
        Save the barycentric equatorial cartesian elements to file.
        """
        self.tstart = 2458849.5  # Need to carry this through from input file
        # Below should be good
        outfile = open(output_file, 'w')
        outfile.write(f"tstart {self.tstart:}\n")
        outfile.write("tstep +20.0\n")
        outfile.write("trange 600.\n")
        outfile.write("geocentric 0\n")
        outfile.write("state\n")
        els = self.barycentric_equatorial_cartesian_elements
        for prefix in ['', 'd']:
            for el in ['x_BaryEqu', 'y_BaryEqu', 'z_BaryEqu']:
                outfile.write(f"{els[prefix + el]:e} ")
            outfile.write("\n")

    def parse_ele220(self, ele220file=None):
        '''
        Parse a file containing a single ele220 line.
        Currently returns junk data.
        '''
        if ele220file is None:
            raise TypeError("Required argument 'ele220file'"
                            " (pos 1) not found")
        self.heliocentric_ecliptic_cartesian_elements = _get_junk_data('helio')

    def parse_orbfit(self, felfile=None):
        '''
        Parse a file containing OrbFit elements for a single object & epoch.
        Currently returns junk data.

        Inputs:
        -------
        felfile : string, filename of fel/eq formatted OrbFit output

        Returns:
        --------
`        Heliocentric ecliptic cartesian coordinates and epoch.
        '''
        if felfile is None:
            raise TypeError("Required argument 'felfile' (pos 1) not found")

        obj = {}
        el = open(felfile).readlines()
        cart_head = '! Cartesian position and velocity vectors\n'
        cart = el.count(cart_head)

        # Only do this if the file actually has cartesian coordinates.
        if cart > 0:
            # get Cartesian Elements
            carLoc = len(el) - 1 - list(reversed(el)).index(cart_head)
            carEls = el[carLoc:carLoc + 25]
            (car, car_x, car_y, car_z, car_dx, car_dy, car_dz
             ) = carEls[1].split()
            obj.update({'x_helio': float(car_x), 'dx_helio': float(car_dx),
                        'y_helio': float(car_y), 'dy_helio': float(car_dy),
                        'z_helio': float(car_z), 'dz_helio': float(car_dz)})
            # Cartesian Covariance
            (cart_err, sig_x, x_y, x_z, x_dx, x_dy, x_dz, sig_y, y_z, y_dx,
             y_dy, y_dz, sig_z, z_dx, z_dy, z_dz, sig_dx, dx_dy, dx_dz,
             sig_dy, dy_dz, sig_dz) = self._get_Covariance_List(carEls)
            if cart_err == "":
                obj.update({'sigma_x_helio': sig_x, 'sigma_dx_helio': sig_dx,
                            'sigma_y_helio': sig_y, 'sigma_dy_helio': sig_dy,
                            'sigma_z_helio': sig_z, 'sigma_dz_helio': sig_dz}
                           )
                obj.update({'x_y_helio': x_y, 'x_z_helio': x_z,
                            'x_dx_helio': x_dx, 'x_dy_helio': x_dy,
                            'x_dz_helio': x_dz, 'y_z_helio': y_z,
                            'y_dx_helio': y_dx, 'y_dy_helio': y_dy,
                            'y_dz_helio': y_dz, 'z_dx_helio': z_dx,
                            'z_dy_helio': z_dy, 'z_dz_helio': z_dz,
                            'dx_dy_helio': dx_dy, 'dx_dz_helio': dx_dz,
                            'dy_dz_helio': dy_dz})
        self.heliocentric_ecliptic_cartesian_elements = obj

    def make_bary_equatorial(self):
        '''
        Convert whatever elements to barycentric equatorial cartesian.
        '''
        if hasattr(self, 'heliocentric_ecliptic_cartesian_elements'):
            xyzv_hel_ecl = [self.heliocentric_ecliptic_cartesian_elements[key]
                            for key in ['x_helio', 'y_helio', 'z_helio',
                                        'dx_helio', 'dy_helio', 'dz_helio']]
            xyzv_bar_ecl = ecliptic_helio2bary(xyzv_hel_ecl, 2450000.0)
            xyzv_bar_equ = ecliptic_to_equatorial(xyzv_bar_ecl)
            obj = {}
            obj.update({'x_BaryEqu': float(xyzv_bar_equ[0]),
                        'y_BaryEqu': float(xyzv_bar_equ[1]),
                        'z_BaryEqu': float(xyzv_bar_equ[2]),
                        'dx_BaryEqu': float(xyzv_bar_equ[3]),
                        'dy_BaryEqu': float(xyzv_bar_equ[4]),
                        'dz_BaryEqu': float(xyzv_bar_equ[5])})
            self.barycentric_equatorial_cartesian_elements = obj
        elif 0:  # if different input format
            pass
        else:
            raise TypeError("There does not seem to be any valid elements")


# Functions
# -----------------------------------------------------------------------------

def ecliptic_to_equatorial(input_xyz, backwards=False):
    '''
    Convert a cartesian vector from mean ecliptic to mean equatorial.
    backwards=True converts backwards, from equatorial to ecliptic.
    input:
        input_xyz - np.array length 3 or 6
        backwards - boolean
    output:
        output_xyz - np.array length 3 or 6

    ### Is this HELIOCENTRIC or BARYCENTRIC??? Either way seems to work...
    '''
    direction = -1 if backwards else +1
    if isinstance(input_xyz, list):
        input_xyz = np.array(input_xyz)
    rotation_matrix = mpc.rotate_matrix(mpc.Constants.ecl * direction)
    output_xyz = np.zeros_like(input_xyz)
    output_xyz[:3] = np.dot(rotation_matrix,
                            input_xyz[:3].reshape(-1, 1)).flatten()
    if len(output_xyz) == 6:
        output_xyz[3:6] = np.dot(rotation_matrix,
                                 input_xyz[3:6].reshape(-1, 1)).flatten()
    return output_xyz


def ecliptic_helio2bary(input_xyz, jd_utc, backwards=False):
    '''
    Convert from heliocentric to barycentic cartesian coordinates.
    backwards=True converts backwards, from bary to helio.
    input:
        input_xyz - np.array length 3 or 6
        backwards - boolean
    output:
        output_xyz - np.array length 3 or 6

    input_xyz MUST BE EQUATORIAL!!!
    '''
    direction = -1 if backwards else +1
    if isinstance(input_xyz, list):
        input_xyz = np.array(input_xyz)
    jd_tdb = mpc.EOP.jdTDB(jd_utc)
    delta, delta_vel = mpc.jpl_kernel[0, 10].compute_and_differentiate(jd_tdb)
    output_xyz = np.zeros_like(input_xyz)
    output_xyz[:3] = input_xyz[:3] + delta * direction / au_km
    if len(output_xyz) == 6:
        output_xyz[3:6] = input_xyz[3:6] + delta_vel * direction / au_km
    return output_xyz


def _get_junk_data(coordsystem='BaryEqu'):
    """Just make some junk data for saving."""
    junk = {}
    junk.update({'x_' + coordsystem: float(3), 'dx_' + coordsystem: float(0.3),
                 'y_' + coordsystem: float(2), 'dy_' + coordsystem: float(0.2),
                 'z_' + coordsystem: float(1), 'dz_' + coordsystem: float(0.1)})
    junk.update({'sigma_x_' + coordsystem: 0.03, 'sigma_dx_' + coordsystem: 0.003,
                 'sigma_y_' + coordsystem: 0.02, 'sigma_dy_' + coordsystem: 0.002,
                 'sigma_z_' + coordsystem: 0.01, 'sigma_dz_' + coordsystem: 0.001}
                )
    junk.update({'x_y_' + coordsystem: 0.41, 'x_z_' + coordsystem: 0.42,
                 'x_dx_' + coordsystem: 0.43, 'x_dy_' + coordsystem: 0.44,
                 'x_dz_' + coordsystem: 0.45, 'y_z_' + coordsystem: 0.46,
                 'y_dx_' + coordsystem: 0.47, 'y_dy_' + coordsystem: 0.48,
                 'y_dz_' + coordsystem: 0.49, 'z_dx_' + coordsystem: 0.50,
                 'z_dy_' + coordsystem: 0.51, 'z_dz_' + coordsystem: 0.52,
                 'dx_dy_' + coordsystem: 0.53, 'dx_dz_' + coordsystem: 0.54,
                 'dy_dz_' + coordsystem: 0.55})
    return junk


# End
