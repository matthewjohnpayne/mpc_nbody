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
import numpy as np
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
    (P.barycentric_equatorial_cartesian_elements, P.jd_utc
     ) = parse_input._get_junk_data('BaryEqu')
    P.save_elements()
    assert cmp('./holman_ic', os.path.join(DATA_DIR, 'holman_ic_junk'))


@pytest.mark.parametrize(
    ('input_xyz', 'jd_utc', 'expected_output_xyz'),
    [
     (  # Test 0: Geocenter at 2020-Mar-28 11:58:50.814329 UTC, equatorial
      [-9.885802285735691E-01, -1.274351089341763E-01, -5.523815439049384E-02,
       2.118089949176372E-03, -1.569453627583853E-02, -6.804080975920086E-03],
      2458937.000000000 - 69.185671 / 3.154e+7,
      [-9.931015634277218E-01, -1.208194503624936E-01, -5.232297101050443E-02,
       2.109883420735295E-03, -1.569721932419286E-02, -6.804992970946320E-03]
     ),
     (  # Test 1: Geocenter at 2020-May-28 11:58:50.815007 UTC, equatorial
      [-3.904609686332465E-01, -8.581207697769445E-01, -3.719949439907977E-01,
       1.560066535010230E-02, -6.135691724146630E-03, -2.660314977551842E-03],
      2458998.000000000 - 69.184993 / 3.154e+7,
      [-3.954807255875652E-01, -8.516881747767834E-01, -3.691437289321969E-01,
       1.559254759272704E-02, -6.139028655755465E-03, -2.661507925459652E-03]
     )
    ])
def test_helio_to_bary(input_xyz, jd_utc, expected_output_xyz):
    '''
    Test that heliocentric cartesian coordinates taken from Horizons
    is converted to barycentric cartesian and still agrees with Horizons.
    '''
    output_xyz = parse_input.helio_to_bary(input_xyz, jd_utc)
    exp_xyz = np.array(expected_output_xyz)
    # Each element should be within 0.0001% of expected:  ### Edit threshold
    error = np.abs((exp_xyz - output_xyz) / exp_xyz)
    print(error)
    assert np.all(error < 0.000001)


# I'm not really sure whether ecliptic_to_equatorial is supposed to have
# barycentric or heliocentric inputs, hence all the tests below.
# It seems to not make any difference, which I find a little peculiar.
# This should get replaced with some astroquery.jplhorizons queries.
@pytest.mark.parametrize(
    ('input_xyz', 'jd_utc', 'expected_output_xyz'),
    [
     (  # Test 0: Geocenter at 2020-Mar-28 11:58:50.814329 UTC, heliocentric
      [-9.885802285735691E-01, -1.388919024773175E-01, 1.075940262414155E-05,
       2.118089949176372E-03, -1.710596348490784E-02, 3.057592004481207E-07],
      2458937.000000000 - 69.185671 / 3.154e+7,
      [-9.885802285735691E-01, -1.274351089341763E-01, -5.523815439049384E-02,
       2.118089949176372E-03, -1.569453627583853E-02, -6.804080975920086E-03]
     ),
     (  # Test 1: Geocenter at 2020-Mar-28 11:58:50.814329 UTC, barycentric
      [-9.931015634277218E-01, -1.316625610551122E-01, 5.383001014609073E-05,
       2.109883420735295E-03, -1.710878790443237E-02, 5.362754667958403E-07],
      2458937.000000000 - 69.185671 / 3.154e+7,
      [-9.931015634277218E-01, -1.208194503624936E-01, -5.232297101050443E-02,
       2.109883420735295E-03, -1.569721932419286E-02, -6.804992970946320E-03]
     ),
     (  # Test 2: Geocenter at 2020-May-28 11:58:50.815007 UTC, heliocentric
      [-3.904609686332465E-01, -9.352815042010558E-01, 4.215095599060576E-05,
       1.560066535010230E-02, -6.687599620944508E-03, -1.532676517666701E-07],
      2458998.000000000 - 69.184993 / 3.154e+7,
      [-3.904609686332465E-01, -8.581207697769445E-01, -3.719949439907977E-01,
       1.560066535010230E-02, -6.135691724146630E-03, -2.660314977551842E-03]
     ),
     (  # Test 3: Geocenter at 2020-May-28 11:58:50.815007 UTC, barycentric
      [-3.954807255875652E-01, -9.282455654588916E-01, 9.935028293246270E-05,
       1.559254759272704E-02, -6.691135723263909E-03, 7.957920673580264E-08],
      2458998.000000000 - 69.184993 / 3.154e+7,
      [-3.954807255875652E-01, -8.516881747767834E-01, -3.691437289321969E-01,
       1.559254759272704E-02, -6.139028655755465E-03, -2.661507925459652E-03]
     ),
     (  # Test 4: Pluto at 1989-Sep-05 11:59:03.817425 UTC, heliocentric
      [-2.025461047950155E+01, -2.012465469047205E+01, 8.012582560787127E+00,
       2.384906089943138E-03, -2.566190812083806E-03, -4.165830038869900E-04],
      2447775.000000000 - 56.182575 / 3.154e+7,
      [-2.025461047950155E+01, -2.165123198654408E+01, -6.537271365172815E-01,
       2.384906089943138E-03, -2.188726835437898E-03, -1.402979516238514E-03]
     ),
     (  # Test 5: Pluto at 1989-Sep-05 11:59:03.817425 UTC, barycentric
      [-2.025461047950155E+01, -2.012465469047205E+01, 8.012582560787127E+00,
       2.384906089943138E-03, -2.566190812083806E-03, -4.165830038869900E-04],
      2447775.000000000 - 56.182575 / 3.154e+7,
      [-2.025461047950155E+01, -2.165123198654408E+01, -6.537271365172815E-01,
       2.384906089943138E-03, -2.188726835437898E-03, -1.402979516238514E-03]
     )
    ])
def test_ecliptic_to_equatorial(input_xyz, jd_utc, expected_output_xyz):
    '''
    Test that heliocentric cartesian coordinates taken from Horizons
    is converted to barycentric cartesian and still agrees with Horizons.
    '''
    output_xyz = parse_input.ecliptic_to_equatorial(input_xyz)
    # Why is the JD not used for this?
    exp_xyz = np.array(expected_output_xyz)
    # Each element should be within 0.0001% of expected:  ### Edit threshold
    error = np.abs((exp_xyz - output_xyz) / exp_xyz)
    print(error)
    assert np.all(error < 0.000001)


@pytest.mark.parametrize(
    ('data_file', 'file_type', 'test_result_file'),
    [('30101.eq0_postfit', 'eq', 'holman_ic_30101'),
     ('30102.eq0_postfit', 'eq', 'holman_ic_30102'),
     pytest.param('30101.ele220', 'ele220', 'holman_ic_30101',
                  marks=pytest.mark.xfail(reason='Not implemented yet.')),
     pytest.param('30102.ele220', 'ele220', 'holman_ic_30102',
                  marks=pytest.mark.xfail(reason='Not implemented yet.')),
     ('30101.eq0_horizons', 'eq', 'holman_ic_30101'),
     ('30102.eq0_horizons', 'eq', 'holman_ic_30102'),
     ])
def test_instantiation_with_data(data_file, file_type, test_result_file):
    '''
    Test that instantiation with data functions (essentially test everything).
    '''
    parse_input.ParseElements(os.path.join(DATA_DIR, data_file), file_type)
    assert cmp('./holman_ic', os.path.join(DATA_DIR, test_result_file))


# End
