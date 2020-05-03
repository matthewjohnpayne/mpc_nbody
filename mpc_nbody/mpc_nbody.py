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

    def run_nbody(self, parsed_input):
        '''
        Run the reboundx ephem_forces nbody integrator with the parsed input.
        '''
        pass

# Functions
# -----------------------------------------------------------------------------


# End
