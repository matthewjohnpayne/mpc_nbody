# -*- coding: utf-8 -*-
# mpc_nbody/mpc_nbody/mpc_nbody.py

'''
----------------------------------------------------------------------------
mpc_nbody's wrapper module that calls the parser to parse an orbit,
and the reboundx/examples/ephem_forces n-body integrator.

Apr 2020
Mike Alexandersen & Matthew Payne & Matthew Holman

This module provides functionalities to
(a)
(b)
(c)

The output is then either saved to a file or passed to the orbit_cheby routine.
----------------------------------------------------------------------------
'''


# Import third-party packages
# -----------------------------------------------------------------------------
import sys
import os
import numpy as np


# Import neighbouring packages
# -----------------------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
try:  # Import ephem_forces from whereever REBX_DIR is set to live
    sys.path.append(os.environ['REBX_DIR'])
    from examples.ephem_forces import ephem_forces
except (KeyError, ModuleNotFoundError):
    from reboundx.examples.ephem_forces import ephem_forces
from mpc_nbody import parse_input

# Default for caching stuff using lru_cache
# -----------------------------------------------------------------------------


# Constants and stuff
# -----------------------------------------------------------------------------
DATA_PATH = os.path.realpath(os.path.dirname(__file__))
DATA_DIR = os.path.join(os.path.dirname(DATA_PATH), 'dev_data')
au_km = 149597870.700  # This is now a definition


# Data classes/methods
# -----------------------------------------------------------------------------
class NbodySim():
    '''
    Class for containing all of the N-body related stuff.
    '''

    def __init__(self, input_file=None, filetype=None, save_parsed=False,
                 save_output=False):
        #If input filename provided, process it:
        if isinstance(input_file, str) & isinstance(filetype, str):
            P = parse_input.ParseElements(input_file, filetype,
                                          save_parsed=save_parsed)
            self.run_nbody(P)
        else:
            print("Keywords 'input_file' and/or 'filetype' missing; "
                  "initiating empty object.")

    def run_nbody(self, parsed_input, geocentric=False):
        '''
        Run the reboundx ephem_forces nbody integrator with the parsed input.
        Input:
        parsed_input = Either ParseElements object,
                       list of ParseElements objects,
                       or numpy array of elements.
        geocentric = boolean, use geo- (True) or heliocentric (False)
        '''
        # First get input (3 types allowed) into a useful format:
        reparsed_input = self._fix_input(parsed_input)

    def _fix_input(self, pinput):
        '''
        Convert the input to a useful format.
        Input:
        input = Either ParseElements object,
                list of ParseElements objects,
                or numpy array of elements.
        output = numpy array of elements.
        '''
        if isinstance(pinput, parse_input.ParseElements):
            els = pinput.barycentric_equatorial_cartesian_elements
            reparsed = np.array([els[i] for i in ['x_BaryEqu', 'y_BaryEqu',
                                                  'z_BaryEqu', 'dx_BaryEqu',
                                                  'dy_BaryEqu', 'dz_BaryEqu']])
        elif isinstance(pinput, list):
            if isinstance(pinput[0], parse_input.ParseElements):
                reparsed = []
                for particle in pinput:
                    els = particle.barycentric_equatorial_cartesian_elements
                    _ = [reparsed.append(els[i])
                         for i in ['x_BaryEqu', 'y_BaryEqu', 'z_BaryEqu',
                                   'dx_BaryEqu', 'dy_BaryEqu', 'dz_BaryEqu']]
        elif isinstance(pinput, np.ndarray):
            if (len(np.shape(pinput)) == 1) & (len(pinput) % 6 == 0):
                reparsed = pinput
        else:
            raise(TypeError('"pinput" not understood.\n'
                            'Must be ParseElements object, '
                            'list of ParseElements or numpy array.'))
        return reparsed

# Functions
# -----------------------------------------------------------------------------


# End
