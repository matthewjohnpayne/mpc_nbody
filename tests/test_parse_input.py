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
from astroquery.jplhorizons import Horizons

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


# Tests
# -----------------------------------------------------------------------------

def test_instantiation():
    '''Test instantiation of the ParseElements class with no observations.'''
    assert isinstance(parse_input.ParseElements(), parse_input.ParseElements)


@pytest.mark.parametrize(('data_file'),
                         ['30101.eq0_postfit', '30102.eq0_postfit',
                          '30101.eq0_horizons', '30102.eq0_horizons'])
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
    (P.barycentric_equatorial_cartesian_elements, P.time
     ) = parse_input._get_junk_data('BaryEqu')
    P.save_elements()
    assert cmp('./holman_ic', os.path.join(DATA_DIR, 'holman_ic_junk'))


@pytest.mark.parametrize(
    ('target', 'jd_tdb', 'id_type'),
    [
     (  # Test 0: Geocenter at 2020-Mar-28 12:00:00 TDB, equatorial
      'Geocenter', 2458937.000000000, 'majorbody'),
     (  # Test 1: Geocenter at 2020-May-28 12:00:00 TDB, equatorial
      'Geocenter', 2458998.000000000, 'majorbody'),
     (  # Test 2: 30101 at 2020-Mar-28 12:00:00 TDB, equatorial
      '30101', 2458937.000000000, 'smallbody'),
     (  # Test 3: 30102 at 2020-Mar-28 12:00:00 TDB, equatorial
      '30102', 2458937.000000000, 'smallbody'),
    ])
def test_equatorial_helio2bary(target, jd_tdb, id_type):
    '''
    Test that heliocentric cartesian coordinates taken from Horizons
    is converted to barycentric cartesian and still agrees with Horizons.
    '''
    hor_in_table = Horizons(target, '500@10', epochs=jd_tdb, id_type=id_type
                            ).vectors(refplane='earth'
                                      )['x', 'y', 'z', 'vx', 'vy', 'vz']
    hor_out_table = Horizons(target, '500@0', epochs=jd_tdb, id_type=id_type
                             ).vectors(refplane='earth'
                                       )['x', 'y', 'z', 'vx', 'vy', 'vz']
    input_xyz = list(hor_in_table.as_array()[0])
    expected_output_xyz = np.array(list(hor_out_table.as_array()[0]))
    output_xyz = parse_input.equatorial_helio2bary(input_xyz, jd_tdb)
    # Each element should be within 15mm or 15mm/day
    error = np.abs(expected_output_xyz - output_xyz)
    print(error)
    assert np.all(error[:3] < 1e-13)  # XYZ accurate to 15 milli-metres
    assert np.all(error[3:6] < 1e-14)  # V accurate to 1.5 milli-metres/day


# I'm not really sure whether ecliptic_to_equatorial is supposed to have
# barycentric or heliocentric inputs, hence all the tests below.
# It seems to not make any difference, which I find a little peculiar.
@pytest.mark.parametrize(
    ('target', 'jd_tdb', 'id_type', 'centre'),
    [
     (  # Test 0: Geocenter at 2020-Mar-28 12:00:00 TDB, helio
      'Geocenter', 2458937.000000000, 'majorbody', '500@10'),
     (  # Test 0: Geocenter at 2020-Mar-28 12:00:00 TDB, bary
      'Geocenter', 2458937.000000000, 'majorbody', '500@0'),
     (  # Test 1: Geocenter at 2020-May-28 12:00:00 TDB, helio
      'Geocenter', 2458998.000000000, 'majorbody', '500@10'),
     (  # Test 1: Geocenter at 2020-May-28 12:00:00 TDB, bary
      'Geocenter', 2458998.000000000, 'majorbody', '500@0'),
     (  # Test 2: 30101 at 2020-Mar-28 12:00:00 TDB, helio
      '30101', 2458937.000000000, 'smallbody', '500@10'),
     (  # Test 2: 30101 at 2020-Mar-28 12:00:00 TDB, bary
      '30101', 2458937.000000000, 'smallbody', '500@0'),
     (  # Test 3: 30102 at 2020-Mar-28 12:00:00 TDB, helio
      '30102', 2458937.000000000, 'smallbody', '500@10'),
     (  # Test 3: 30102 at 2020-Mar-28 12:00:00 TDB, bary
      '30102', 2458937.000000000, 'smallbody', '500@0'),
     (  # Test 4: Geocenter at 2020-Mar-28 12:00:00 TDB, helio
      'Mercury Barycenter', 2458937.000000000, 'majorbody', '500@10'),
     (  # Test 4: Geocenter at 2020-Mar-28 12:00:00 TDB, bary
      'Mercury Barycenter', 2458937.000000000, 'majorbody', '500@0'),
     (  # Test 5: Geocenter at 2020-May-28 12:00:00 TDB, helio
      'Jupiter Barycenter', 2458998.000000000, 'majorbody', '500@10'),
     (  # Test 5: Geocenter at 2020-May-28 12:00:00 TDB, bary
      'Jupiter Barycenter', 2458998.000000000, 'majorbody', '500@0'),
    ])
def test_ecliptic_to_equatorial(target, jd_tdb, id_type, centre):
    '''
    Test that heliocentric cartesian coordinates taken from Horizons
    is converted to barycentric cartesian and still agrees with Horizons.
    jd_tdb isn't actually used for this, but it seemed useful to record it.
    '''
    hor_table = Horizons(target, centre, epochs=jd_tdb, id_type=id_type)
    hor_in_table = hor_table.vectors(refplane='ecliptic'
                                     )['x', 'y', 'z', 'vx', 'vy', 'vz']
    hor_out_table = hor_table.vectors(refplane='earth'
                                      )['x', 'y', 'z', 'vx', 'vy', 'vz']
    input_xyz = list(hor_in_table.as_array()[0])
    expected_output_xyz = np.array(list(hor_out_table.as_array()[0]))
    output_xyz = parse_input.ecliptic_to_equatorial(input_xyz)
    # Each element should be within 15mm or 1.5mm/day
    error = np.abs(expected_output_xyz - output_xyz)
    print(error)
    assert np.all(error[:3] < 1e-13)  # XYZ accurate to 15 milli-metres
    assert np.all(error[3:6] < 1e-14)  # V accurate to 1.5 milli-metres/day


@pytest.mark.parametrize(
    ('data_file', 'file_type', 'test_result_file'),
    [
     pytest.param('30101.ele220', 'ele220', 'holman_ic_30101',
                  marks=pytest.mark.xfail(reason='Not implemented yet.')),
     pytest.param('30102.ele220', 'ele220', 'holman_ic_30102',
                  marks=pytest.mark.xfail(reason='Not implemented yet.')),
     ('30101.eq0_postfit', 'eq', 'holman_ic_30101'),
     ('30102.eq0_postfit', 'eq', 'holman_ic_30102'),
     ('30101.eq0_horizons', 'eq', 'holman_ic_30101_horizons'),
     ('30102.eq0_horizons', 'eq', 'holman_ic_30102_horizons'),
      ])
def test_instantiation_with_data(data_file, file_type, test_result_file):
    '''
    Test that instantiation with data works (essentially test everything).
    '''
    parse_input.ParseElements(os.path.join(DATA_DIR, data_file), file_type)
    if cmp('./holman_ic', os.path.join(DATA_DIR, test_result_file)):
        assert True  # If files are identical, no further testing needed.
    else:  # If files not identical, investigate further:
        fileA = open('./holman_ic', 'r')
        fileB = open(os.path.join(DATA_DIR, test_result_file), 'r')
        five_tf = []
        for _ in range(0, 5):  # First five lines should be identical
            lineA = fileA.readline()
            lineB = fileB.readline()
            five_tf.append(lineA == lineB)
        xyzA = np.array(fileA.readline().split(), dtype=float)
        xyzB = np.array(fileB.readline().split(), dtype=float)
        xyz_offset = np.abs(xyzA - xyzB)
        xyz_tf = np.all(xyz_offset < 1e-13)  # Position accurate to 15 mm
        vA = np.array(fileA.readline().split(), dtype=float)
        vB = np.array(fileB.readline().split(), dtype=float)
        v_offset = np.abs(vA - vB)
        v_tf = np.all(v_offset < 1e-14)  # Position accurate to 1.5 mm/day
        if xyz_tf & v_tf & np.all(five_tf):
            print('Awesome!')
        else:
            print(f'First five lines identical: {five_tf:}')
            print(f'Position off by: {xyz_offset:}')
            print(f'Velocity off by: {v_offset:}')
        assert xyz_tf & v_tf & np.all(five_tf)


# End
