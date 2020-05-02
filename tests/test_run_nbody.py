# -*- coding: utf-8 -*-
# mpc_nbody/tests/test_run_nbody.py

'''
----------------------------------------------------------------------------
tests for mpc_nbody's run_nbody module.

Mar 2020
Mike Alexandersen & Matthew Payne & Matthew Holman

----------------------------------------------------------------------------
'''

# import third-party packages
# -----------------------------------------------------------------------------
import sys
import os
import numpy as np
import pytest
from astroquery.jplhorizons import Horizons

# Import neighbouring packages
# -----------------------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
#from mpc_nbody import run_nbody
try:  # Import ephem_forces from whereever REBX_DIR is set to live
    sys.path.append(os.environ['REBX_DIR'])
    from examples.ephem_forces import ephem_forces
except (KeyError, ModuleNotFoundError):
    from reboundx.examples.ephem_forces import ephem_forces

# Default for caching stuff using lru_cache
# -----------------------------------------------------------------------------

# Convenience functions
# -----------------------------------------------------------------------------

# Constants & Test Data
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dev_data')


# Tests
# -----------------------------------------------------------------------------

#def test_instantiation():
#    '''Test instantiation of  with no .'''
#    assert isinstance(, )

#def test_instantiation_with_data(data_file, file_type, test_result_file):


def test_initialize_integration_function():
    '''
    If we put ANYTHING into the ephem_forces.integration_function,
    will it work or crash and burn.
    Most likely if there is a problem, it'll cause pytest to crash entirely.
    '''
    tstart, tstep, trange = 2456184.7, 20.0, 600
    geocentric = 0
    n_particles = 1
    instates = np.array([-3.1, 2.7, 3.6, -0.006, -0.004, -0.002])
    (times, states, n_out, n_particles_out
     ) = ephem_forces.integration_function(tstart, tstep, trange, geocentric,
                                           n_particles, instates)
    assert n_particles_out == n_particles
    assert isinstance(n_particles_out, int)
    assert isinstance(n_out, int)
    assert isinstance(states, np.ndarray)
    assert isinstance(times, np.ndarray)


@pytest.mark.parametrize(
    ('tstart', 'tstep', 'trange', 'geocentric', 'targets', 'id_type'),
    [
     (2456117.641933589, 20.0, 600, 0, ['30101'], ['smallbody']),
     (2456184.7528431923, 20.0, 600, 0, ['30102'], ['smallbody']),
     (2456142.5, 20.0, 60, 0, ['30101', '30102'],
      ['smallbody', 'smallbody']),
      ])
def test_nbody_vs_Horizons(tstart, tstep, trange, geocentric,
                           targets, id_type):
    '''
    Test that putting input from Horizons in gives Horizons consistent output.
    '''
    centre = '500' if geocentric else '500@0'
    # Make the single array with 6 elements for each particle.
    horizons_in = []
    for i, targi in enumerate(targets):
        horizons_in = np.concatenate([horizons_in, nice_Horizons(targi, centre,
                                      tstart, id_type[i])])
    # Run nbody integrator
    (times, states, n_times, n_particles_out
     ) = ephem_forces.integration_function(tstart, tstep, trange, geocentric,
                                           len(targets), horizons_in)
    # Check 20 time steps (or less if there are many)
    for j in set(np.linspace(0, n_times - 1, 20).astype(int)):
        # Get Horizons positions for that time and compare
        for i, targi in enumerate(targets):
            horizons_xyzv = nice_Horizons(targi, centre, times[j], id_type[i])
            mpc_xyzv = states[j, i, :]
            # Check whether position within 15 mm, velocity within 1.5 mm/day
            # Check whether position within 15 m, velocity within 1.5 m/day
            error, good_tf = compare_xyzv(horizons_xyzv, mpc_xyzv, 1e-10, 1e-11)
            if np.all(good_tf):
                print('Awesome!')
            else:
                print(f'Time, timestep: {times[j]:}, {j:}')
                print(f'Horizons : {horizons_xyzv:}')
                print(f'N-body   : {mpc_xyzv:}')
                print(f'Position off by [au]: {error[:3]:}')
                print(f'Velocity off by [au/day]: {error[3:6]:}')
            assert np.all(good_tf)
    assert n_particles_out == len(targets)


def nice_Horizons(target, centre, epochs, id_type):
    '''
    Only require the inputs I actually want to vary.
    Return in the format I actually want, not an astropy table.
    '''
    horizons_table = Horizons(target, centre, epochs=epochs, id_type=id_type)
    horizons_vector = horizons_table.vectors(refplane='earth')
    horizons_xyzv = horizons_vector['x', 'y', 'z', 'vx', 'vy', 'vz']
    return np.array(list(horizons_xyzv.as_array()[0]))


def compare_xyzv(xyzv0, xyzv1, threshold_xyz, threshold_v):
    '''
    Calculate the difference between two sets of cartesian coordinates.
    '''
    if isinstance(xyzv0, list):
        xyzv0 = np.array(xyzv0)
    if isinstance(xyzv1, list):
        xyzv1 = np.array(xyzv1)
    error = xyzv0 - xyzv1
    good_tf = np.abs(error) < np.array([threshold_xyz] * 3 + [threshold_v] * 3)
    return error, good_tf


# End
