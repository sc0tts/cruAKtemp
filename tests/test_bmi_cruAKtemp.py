"""
test_bmi_cruAKtemp.py
  tests of the cruAKtemp component of permamodel using bmi API
"""

import datetime

import pathlib

import pkg_resources

import cruAKtemp


default_config_filename = (
    pathlib.Path(pkg_resources.resource_filename("cruAKtemp", "examples"))
    / "default_temperature.cfg"
)


# ---------------------------------------------------
# Tests that ensure we have bmi functionality
# ---------------------------------------------------
def test_cruAKtemp_has_initialize():
    # Can we call an initialize function?
    ct = cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)


def test_initialize_sets_times():
    # Can we call an initialize function?
    ct = cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    assert ct._model.first_date == datetime.date(1902, 12, 15)


def test_att_map():
    ct = cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    assert "PermaModel_cruAKtemp" == ct.get_attribute("model_name")
    assert "days" == ct.get_attribute("time_units")


def test_get_input_var_names():
    ct = cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    input_vars = ct.get_input_var_names()
    # no input variables for cruAKtemp
    assert len(input_vars) == 0


def test_get_output_var_names():
    ct = cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    output_vars = ct.get_output_var_names()
    output_list = (
        "atmosphere_bottom_air__temperature",
        "atmosphere_bottom_air__temperature_mean_jan",
        "atmosphere_bottom_air__temperature_mean_jul",
        "atmosphere_bottom_air__temperature_year",
    )
    # In the future, we may include the start and end datetimes as outputs
    # output_list = ('atmosphere_bottom_air__temperature', 'datetime__start',
    #               'datetime__end')
    assert output_vars == output_list


def test_get_var_name():
    ct = cruAKtemp.BmiCruAKtempMethod()
    ct.initialize(cfg_file=default_config_filename)
    this_var_name = ct.get_var_name("atmosphere_bottom_air__temperature")
    assert this_var_name == "T_air"
    this_var_name = ct.get_var_name("atmosphere_bottom_air__temperature_mean_jul")
    assert this_var_name == "T_air_prior_jul"
