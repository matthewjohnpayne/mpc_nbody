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
#import numpy as np

# Import neighbouring packages
# -----------------------------------------------------------------------------

# Default for caching stuff using lru_cache
# -----------------------------------------------------------------------------

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
        """Save the barycentric equatorial cartesian elements to file."""
        ### For now, just fake it!
        self.barycentric_equatorial_cartesian_elements = _get_junk_data()
        self.tstart = 2458849.5
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
        if felfile is None:
            raise TypeError ("Required argument 'ele220file'"
                             " (pos 1) not found")
        self.barycentric_ecliptic_keplarian_elements
        return 0, 0, 0, 0, 0, 0

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
            raise TypeError ("Required argument 'felfile' (pos 1) not found")

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
            obj.update({'x_helio' : float(car_x), 'dx_helio' : float(car_dx),
                        'y_helio' : float(car_y), 'dy_helio' : float(car_dy),
                        'z_helio' : float(car_z), 'dz_helio' : float(car_dz)})
            # Cartesian Covariance
            (cart_err, sig_x, x_y, x_z, x_dx, x_dy, x_dz, sig_y, y_z, y_dx,
             y_dy, y_dz, sig_z, z_dx, z_dy, z_dz, sig_dx, dx_dy, dx_dz,
             sig_dy, dy_dz, sig_dz) = self._get_Covariance_List(carEls)
            if cart_err == "":
                obj.update({'sigma_x_helio' : sig_x, 'sigma_dx_helio' : sig_dx,
                            'sigma_y_helio' : sig_y, 'sigma_dy_helio' : sig_dy,
                            'sigma_z_helio' : sig_z, 'sigma_dz_helio' : sig_dz}
                           )
                obj.update({'x_y_helio' : x_y, 'x_z_helio' : x_z,
                            'x_dx_helio' : x_dx, 'x_dy_helio' : x_dy,
                            'x_dz_helio' : x_dz, 'y_z_helio' : y_z,
                            'y_dx_helio' : y_dx, 'y_dy_helio' : y_dy,
                            'y_dz_helio' : y_dz, 'z_dx_helio' : z_dx,
                            'z_dy_helio' : z_dy, 'z_dz_helio' : z_dz,
                            'dx_dy_helio' : dx_dy, 'dx_dz_helio' : dx_dz,
                            'dy_dz_helio' : dy_dz})
        self.heliocentric_ecliptic_cartesian_elements = obj


# Functions
# -----------------------------------------------------------------------------

def _get_junk_data():
    """Just make some junk data for saving."""
    junk = {}
    junk.update({'x_BaryEqu' : float(3), 'dx_BaryEqu' : float(0.3),
                 'y_BaryEqu' : float(2), 'dy_BaryEqu' : float(0.2),
                 'z_BaryEqu' : float(1), 'dz_BaryEqu' : float(0.1)})
    junk.update({'sigma_x_BaryEqu' : 0.03, 'sigma_dx_BaryEqu' : 0.003,
                 'sigma_y_BaryEqu' : 0.02, 'sigma_dy_BaryEqu' : 0.002,
                 'sigma_z_BaryEqu' : 0.01, 'sigma_dz_BaryEqu' : 0.001}
                )
    junk.update({'x_y_BaryEqu' : 0.41, 'x_z_BaryEqu' : 0.42,
                 'x_dx_BaryEqu' : 0.43, 'x_dy_BaryEqu' : 0.44,
                 'x_dz_BaryEqu' : 0.45, 'y_z_BaryEqu' : 0.46,
                 'y_dx_BaryEqu' : 0.47, 'y_dy_BaryEqu' : 0.48,
                 'y_dz_BaryEqu' : 0.49, 'z_dx_BaryEqu' : 0.50,
                 'z_dy_BaryEqu' : 0.51, 'z_dz_BaryEqu' : 0.52,
                 'dx_dy_BaryEqu' : 0.53, 'dx_dz_BaryEqu' : 0.54,
                 'dy_dz_BaryEqu' : 0.55})
    return junk

# End
