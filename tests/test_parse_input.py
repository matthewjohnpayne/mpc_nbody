# -*- coding: utf-8 -*-
# mpc_nbody/tests/test_parse_input.py

'''
----------------------------------------------------------------------------
tests for mpc_nbody's pares_input module.

Mar 2020
Mike Alexandersen & Matthew Payne

----------------------------------------------------------------------------
'''

# import third-party packages
# -----------------------------------------------------------------------------
import sys
import os
from filecmp import cmp
#import numpy as np
import pytest

# Import neighbouring packages
# -----------------------------------------------------------------------------
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.realpath(__file__))))
from mpc_nbody import parse_input

# Default for caching stuff using lru_cache
# -----------------------------------------------------------------------------


# Convenience functions
# -----------------------------------------------------------------------------

def _get_junk_data():
    """Just make some junk data for saving."""
    junk = {}
    junk.update({'x_BaryEqu': float(3), 'dx_BaryEqu': float(0.3),
                 'y_BaryEqu': float(2), 'dy_BaryEqu': float(0.2),
                 'z_BaryEqu': float(1), 'dz_BaryEqu': float(0.1)})
    junk.update({'sigma_x_BaryEqu': 0.03, 'sigma_dx_BaryEqu': 0.003,
                 'sigma_y_BaryEqu': 0.02, 'sigma_dy_BaryEqu': 0.002,
                 'sigma_z_BaryEqu': 0.01, 'sigma_dz_BaryEqu': 0.001}
                )
    junk.update({'x_y_BaryEqu': 0.41, 'x_z_BaryEqu': 0.42,
                 'x_dx_BaryEqu': 0.43, 'x_dy_BaryEqu': 0.44,
                 'x_dz_BaryEqu': 0.45, 'y_z_BaryEqu': 0.46,
                 'y_dx_BaryEqu': 0.47, 'y_dy_BaryEqu': 0.48,
                 'y_dz_BaryEqu': 0.49, 'z_dx_BaryEqu': 0.50,
                 'z_dy_BaryEqu': 0.51, 'z_dz_BaryEqu': 0.52,
                 'dx_dy_BaryEqu': 0.53, 'dx_dz_BaryEqu': 0.54,
                 'dy_dz_BaryEqu': 0.55})
    return junk


# Constants & Test Data
# -----------------------------------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dev_data')
test_eq_files = ['30101.eq0_postfit', '30102.eq0_postfit']

# Tests
# -----------------------------------------------------------------------------


def test_instantiation():
    '''Test instantiation of the ParseElements class with no observations.'''
    assert isinstance(parse_input.ParseElements(), parse_input.ParseElements)


@pytest.mark.parametrize(('data_file'),
                         ['30101.eq0_postfit', '30102.eq0_postfit'])
def test_parse_orbfit(data_file):
    '''Test that OrbFit files get parsed correctly.'''
    P = parse_input.ParseElements()

    # call parse_orbfit
    P.parse_orbfit(os.path.join(DATA_DIR, data_file))
    elements_dictionary = P.heliocentric_ecliptic_cartesian_elements

    # check that the returned results are as expected
    assert isinstance(elements_dictionary, dict)
    for key in ['x_helio', 'dx_helio', 'y_helio', 'dy_helio',
                'z_helio', 'dz_helio']:
        assert key in elements_dictionary
        assert isinstance(elements_dictionary[key], float)
    for key in ['sigma_x_helio', 'sigma_dx_helio', 'sigma_y_helio',
                'sigma_dy_helio', 'sigma_z_helio', 'sigma_dz_helio',
                'x_y_helio', 'x_z_helio', 'x_dx_helio', 'x_dy_helio',
                'x_dz_helio', 'y_z_helio', 'y_dx_helio', 'y_dy_helio',
                'y_dz_helio', 'z_dx_helio', 'z_dy_helio', 'z_dz_helio',
                'dx_dy_helio', 'dx_dz_helio', 'dy_dz_helio']:
        assert key in elements_dictionary
        assert isinstance(elements_dictionary[key], str)


def test_save_elements():
    '''Test that saving elements works correctly.'''
    P = parse_input.ParseElements()
    P.barycentric_equatorial_cartesian_elements = _get_junk_data()
    P.save_elements()
    assert cmp('./holman_ic', os.path.join(DATA_DIR, 'holman_ic_junk'))


@pytest.mark.parametrize(('data_file', 'file_type', 'test_result'),
                         (['30101.eq0_postfit', 'eq', 'holman_ic_30101'],
                          ['30102.eq0_postfit', 'eq', 'holman_ic_30102']))
def test_instantiation_with_data(data_file, file_type, test_result_file):
    '''
    Test that instantiation with data functions (essentially test everything).
    '''
    parse_input.ParseElements(os.path.join(DATA_DIR, data_file), file_type)
    assert cmp('./holman_ic', os.path.join(DATA_DIR, test_result_file))


# End
