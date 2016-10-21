"""
test_cruAKtemp.py
  tests of the cruAKtemp component of permamodel
"""

#from permamodel.components import frost_number
#from permamodel.components import bmi_frost_number
#from cruAKtemp import *
#import cruAKtemp.cruAKtemp as cruAKtemp
import cruAKtemp
import cruAKtemp.cruAKtemp_utils as cu
#from .cruAKtemp_utils import *
import os
import numpy as np
from ..tests import data_directory, examples_directory
from nose.tools import (assert_is_instance, assert_greater_equal,
                        assert_less_equal, assert_almost_equal,
                        assert_greater, assert_in, assert_true,
                        assert_equal)
import datetime


# ---------------------------------------------------
# Tests that ensure we are reaching this testing file
# ---------------------------------------------------
def test_testing():
    # This should pass as long as this routine is getting called
    # and all the import statements above are working
    assert(True)

# ---------------------------------------------------
# Tests that the frost_number module is importing
# ---------------------------------------------------
def test_can_initialize_cruAKtemp_class():
    ct = cruAKtemp.cruAKtemp.CruAKtempMethod

def test_for_cruAKtemp_utils():
    ct = cu

def test_write_gridfile():
    # Create a temperature grid with default structure
    grid_desc = cruAKtemp.cruAKtemp_utils.write_gridfile('temperature')

    # Create a temperature grid with described shape and type
    grid_desc = cruAKtemp.cruAKtemp_utils.write_gridfile('temperature',
                                                         gridshape=(3,4),
                                                        gridtype=np.float64)

    # Fail when attempting to create a grid with non-shape shape
    try:
        grid_desc = cruAKtemp.cruAKtemp_utils.write_gridfile('temperature',
                                                         gridshape='notashape')
    except ValueError:
        pass

def test_write_default_temperature_cfg_file():
    cruAKtemp.cruAKtemp_utils.generate_default_temperature_run_cfg_file(\
        SILENT=True)

def test_initialize_opens_temperature_netcdf_file():
    ct = cruAKtemp.cruAKtemp.CruAKtempMethod()
    ct.initialize_from_config_file()

def test_get_timestep_from_date():
    ct = cruAKtemp.cruAKtemp.CruAKtempMethod()
    ct.initialize_from_config_file()

    # Timestep should initialize to zero
    this_timestep = 0
    assert_equal(this_timestep, ct._current_timestep)

    # Adding 100 days should make the current timestep 100
    number_of_days = 100
    this_timedelta = datetime.timedelta(days=number_of_days)
    ct.increment_date(this_timedelta)
    assert_equal(this_timestep+number_of_days, ct._current_timestep)

    #...and make the date 100 days later
    assert_equal(ct.first_date+this_timedelta, ct._current_date)

def test_can_increment_by_fractions_of_days():
    ct = cruAKtemp.cruAKtemp.CruAKtempMethod()
    ct.initialize_from_config_file()

    # Adding 1.8 days twice should add 3.6 days to the date
    # which truncates to 3.0 days to the timestep
    this_timestep = 0
    number_of_days = 1.8
    this_timedelta = datetime.timedelta(days=number_of_days)
    ct.increment_date(this_timedelta)
    ct.increment_date(this_timedelta)
    assert_equal(ct.first_date+2*this_timedelta, ct._current_date)
    assert_equal(int(this_timestep+2*number_of_days), ct._current_timestep)

def test_can_increment_to_end_of_run():
    ct = cruAKtemp.cruAKtemp.CruAKtempMethod()
    ct.initialize_from_config_file()

    # Adding 1.8 days twice should add 3.6 days to the date
    # which truncates to 3.0 days to the timestep
    number_of_days = ct._last_timestep
    this_timedelta = datetime.timedelta(days=number_of_days)
    ct.increment_date(this_timedelta)
    ct.update_temperature_values()
    ct._T_air.tofile("end_T_air.dat")
    # Note: nc time of 4000 corresponds to model date of Dec 15, 2010

