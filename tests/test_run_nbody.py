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
from test_parse_input import is_parsed_good_enough, compare_xyzv
try:  # Import ephem_forces from whereever REBX_DIR is set to live
    sys.path.append(os.environ['REBX_DIR'])
    from examples.ephem_forces import ephem_forces
except (KeyError, ModuleNotFoundError):
    from reboundx.examples.ephem_forces import ephem_forces
#sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath('.'))))
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))))
from mpc_nbody import mpc_nbody

# Default for caching stuff using lru_cache
# -----------------------------------------------------------------------------

# Convenience functions
# -----------------------------------------------------------------------------

# Constants & Test Data
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dev_data')


# Tests
# -----------------------------------------------------------------------------

def test_initialize_integration_function():
    '''
    If we put ANYTHING into the ephem_forces.integration_function,
    will it work or crash and burn?
    Most likely if there is a problem, it'll cause pytest to crash entirely,
    so might as well start with this.
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


# A @pytest.mark.parametrize basically defines a set of parameters that
# the test will loop through.
# Splitting the parameters into two @pytest.mark.parametrize statements
# essentially makes it a nested loop (so all combinations are tested).
@pytest.mark.parametrize(
    ('tstart', 'tstep', 'trange', 'geocentric', 'targets', 'id_type'),
    [
     (2456117.641933589, 20.0, 600, 0, ['30101'], ['smallbody']),
     (2456184.7528431923, 20.0, 600, 0, ['30102'], ['smallbody']),
     (2456142.5, 20.0, 60, 0, ['30101', '30102'],
      ['smallbody', 'smallbody']),
      ])
@pytest.mark.parametrize(
    ('threshold_xyz', 'threshold_v'),
    [
     (1e-10, 1e-11),  # 1e-10 au ~ 15m, 1e-11 au/day ~ 1.5 m/day
     (5e-11, 2e-13),  # 5e-11 au ~ 7.5m, 2e-13 au/day ~ 30 mm/day
      ])
def test_nbody_vs_Horizons(tstart, tstep, trange, geocentric,
                           targets, id_type, threshold_xyz, threshold_v):
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
            # Check whether position/v within threshold.
            error, good_tf = compare_xyzv(horizons_xyzv, mpc_xyzv,
                                          threshold_xyz, threshold_v)
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


def test_NbodySim_empty():
    '''
    Test the mpc_nbody.NbodySim class. Test empty initialization.
    '''
    assert isinstance(mpc_nbody.NbodySim(), mpc_nbody.NbodySim)


@pytest.mark.parametrize(
    ('data_file', 'file_type', 'holman_ic_test_file', 'nbody_test_file'),
    [
     pytest.param('30101.ele220', 'ele220', 'holman_ic_30101', 'nbody_30101',
                  marks=pytest.mark.xfail(reason='Not implemented yet.')),
     pytest.param('30102.ele220', 'ele220', 'holman_ic_30102', 'nbody_30102',
                  marks=pytest.mark.xfail(reason='Not implemented yet.')),
     ('30101.eq0_postfit', 'eq', 'holman_ic_30101', 'nbody_30101'),
     ('30102.eq0_postfit', 'eq', 'holman_ic_30102', 'nbody_30102'),
     ('30101.eq0_horizons', 'eq', 'holman_ic_30101_horizons',
      'nbody_30101_horizons'),
     ('30102.eq0_horizons', 'eq', 'holman_ic_30102_horizons',
      'nbody_30102_horizons'),
      ])
def test_NbodySim(data_file, file_type, holman_ic_test_file, nbody_test_file):
    '''
    Test the mpc_nbody.NbodySim class. Test empty initialization.
    '''
    Sim = mpc_nbody.NbodySim(os.path.join(DATA_DIR, data_file), file_type,
                             save_parsed=True, save_output=True)
    is_parsed_good_enough(os.path.join(DATA_DIR, holman_ic_test_file))
    is_nbody_output_good_enough(os.path.join(DATA_DIR, nbody_test_file))


# Non-test helper functions
# -----------------------------------------------------------------------------

def is_nbody_output_good_enough(results_file):
    '''
    Helper function for determining whether the saved output from an nbody
    integration is good enough. 
    '''
    pass


def nice_Horizons(target, centre, epochs, id_type):
    '''
    Only require the inputs I actually want to vary.
    Return in the format I actually want, not an astropy table.
    '''
    horizons_table = Horizons(target, centre, epochs=epochs, id_type=id_type)
    horizons_vector = horizons_table.vectors(refplane='earth')
    horizons_xyzv = horizons_vector['x', 'y', 'z', 'vx', 'vy', 'vz']
    return np.array(list(horizons_xyzv.as_array()[0]))


# End
