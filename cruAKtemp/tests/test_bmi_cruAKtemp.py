"""
test_bmi_cruAKtemp.py
  tests of the cruAKtemp component of permamodel using bmi API
"""

#from cruAKtemp import cruAKtempMethod
import cruAKtemp
#import bmi_cruAKtemp
import os
import numpy as np
from ..tests import data_directory, examples_directory
from nose.tools import (assert_is_instance, assert_greater_equal,
                        assert_less_equal, assert_almost_equal,
                        assert_greater, assert_in, assert_true,
                        assert_equal)
import datetime

default_config_filename = os.path.join(examples_directory,
                                       'default_temperature.cfg')

# ---------------------------------------------------
# Tests that ensure we have bmi functionality
# ---------------------------------------------------
def test_cruAKtemp_has_initialize():
    # Can we call an initialize function?
    ct = cruAKtemp.bmi_cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)

def test_initialize_sets_times():
    # Can we call an initialize function?
    ct = cruAKtemp.bmi_cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    #assert_equal(ct._model.first_date, datetime.date(1902, 1, 1))
    assert_equal(ct._model.first_date, datetime.date(1902, 12, 15))

def test_att_map():
    ct = cruAKtemp.bmi_cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    assert_equal('PermaModel_cruAKtemp', ct.get_attribute('model_name'))
    assert_equal('days', ct.get_attribute('time_units'))

def test_get_input_var_names():
    ct = cruAKtemp.bmi_cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    input_vars = ct.get_input_var_names()
    # no input variables for cruAKtemp
    assert_equal(0, len(input_vars))

def test_get_output_var_names():
    ct = cruAKtemp.bmi_cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    output_vars = ct.get_output_var_names()
    output_list = ('atmosphere_bottom_air__temperature',
                   'atmosphere_bottom_air__temperature_months',
                   'atmosphere_bottom_air__temperature_year')
    # In the future, we may include the start and end datetimes as outputs
    #output_list = ('atmosphere_bottom_air__temperature', 'datetime__start',
    #               'datetime__end')
    assert_equal(output_vars, output_list)

def test_get_var_name():
    ct = cruAKtemp.bmi_cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    this_var_name = ct.get_var_name('atmosphere_bottom_air__temperature')
    assert_equal(this_var_name, 'T_air')

