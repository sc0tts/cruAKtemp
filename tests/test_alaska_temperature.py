"""tests of the AlaskaTemperature component of permamodel"""

import datetime
import pathlib

import numpy as np
import pkg_resources
import pytest
from dateutil.relativedelta import relativedelta

from cru_alaska_temperature.utils import (
    write_gridfile, generate_default_temperature_run_cfg_file
)
from cru_alaska_temperature import AlaskaTemperature


data_directory = pathlib.Path(pkg_resources.resource_filename(
    "cru_alaska_temperature", "data")
)
examples_directory = pathlib.Path(
    pkg_resources.resource_filename("cru_alaska_temperature", "examples")
)


def test_write_gridfile(tmpdir):
    """ Test that can write a gridfile to disk """
    # Create a temperature grid with default structure
    write_gridfile("temperature")

    # Create a temperature grid with described shape and type
    write_gridfile("temperature", gridshape=(3, 4), gridtype=np.float64)

    # Fail when attempting to create a grid with non-shape shape
    with pytest.raises(ValueError):
        write_gridfile("temperature", gridshape="notashape")

    with tmpdir.as_cwd():
        write_gridfile("temperature", filename="temperature.grd")
        assert (tmpdir / "temperature.grd").isfile()


def test_write_default_temperature_cfg_file(tmpdir):
    """ test that util operation writes default cfg file """
    with tmpdir.as_cwd():
        generate_default_temperature_run_cfg_file(SILENT=True)


def test_initialize_opens_temperature_netcdf_file():
    """ Test that temperature netcdf file is opened """
    ct = AlaskaTemperature()
    ct.initialize_from_config_file()


def test_get_timestep_from_date():
    """ Test get timestep from a date """
    ct = AlaskaTemperature()
    ct.initialize_from_config_file()

    # Timestep should initialize to zero
    this_timestep = 0
    assert this_timestep == ct._current_timestep

    # Adding 10 years should make the current timestep 10
    number_of_years = 10
    ct.increment_date(number_of_years)
    assert ct._current_timestep == 10

    # ...and make the date 10 days later
    this_timedelta = relativedelta(years=number_of_years)
    assert ct._current_date == ct.first_date + this_timedelta


def test_time_index_yields_correct_values():
    """ Check that we get the expected index into the netcdf file
        for specified month and year """
    ct = AlaskaTemperature()
    ct.initialize_from_config_file()

    # Test that first month yields index zero
    month = 1
    year = 1901
    idx = ct.get_time_index(month, year)
    assert idx == 0

    # Test that a year later yields index 12
    month = 1
    year = 1902
    idx = ct.get_time_index(month, year)
    assert idx == 12

    # Test that a century and a year later yields index 1212
    month = 1
    year = 2002
    idx = ct.get_time_index(month, year)
    assert idx == 1212


def test_specific_netcdf_values():
    """ Test that indexing yields specific values chosen from file
        Values were hand-verified using panoply tables"""
    ct = AlaskaTemperature()
    ct.initialize_from_config_file()

    # Indexes here are based on the reduced-resolution grid, if used
    # Note: Panoply has 1-based indexes, so must add 1 to these
    #       to get Panoply equivalent
    t_idx = 0
    x_idx = 0
    y_idx = 0
    assert ct._temperature[t_idx, y_idx, x_idx] == pytest.approx(-26.1)
    # assert_almost_equal(ct._temperature[t_idx, y_idx, x_idx], -26.1, places=5)

    t_idx = 20
    x_idx = 0
    y_idx = 0
    assert ct._temperature[t_idx, y_idx, x_idx] == pytest.approx(-0.3)
    # assert_almost_equal(ct._temperature[t_idx, y_idx, x_idx], -0.3, places=5)

    t_idx = 20
    x_idx = 0
    y_idx = 6
    assert ct._temperature[t_idx, y_idx, x_idx] == pytest.approx(-1.9)


def test_getting_monthly_annual_temp_values():
    """ Test that prior_months and prior_year values are correct
        Values were hand-verified using panoply tables"""
    ct = AlaskaTemperature()
    ct.initialize_from_config_file()

    # Test prior months values
    # These are values starting from 2/1901
    # actualvalues = [-28.700001, -24.799999, -16.600000, -2.700000,
    #                 7.800000, 11.000000, 7.100000, -0.300000,
    #                -13.400000, -22.100000, -26.500000, -25.700001]
    # actualmean = -11.241668

    # These values start with 1/1902
    actualvalues = [
        -25.7,
        -27.0,
        -26.6,
        -16.9,
        -2.8,
        8.1,
        11.4,
        7.3,
        -0.3,
        -13.6,
        -22.1,
        -28.9,
    ]
    actualmean = -11.425

    vallist = []

    for i in np.arange(0, 12):
        vallist.append(ct.T_air_prior_months[i][0, 0])

    for i in np.arange(0, 12):
        assert vallist[i] == pytest.approx(actualvalues[i])

    # Test prior year value
    assert ct.T_air_prior_year[0, 0] == pytest.approx(actualmean)


def test_can_increment_to_end_of_run(tmpdir):
    """ Test that we can get values for last timestep """
    with tmpdir.as_cwd():
        ct = AlaskaTemperature()
        ct.initialize_from_config_file()

        number_of_years = ct._last_timestep - ct._first_timestep
        ct.increment_date(number_of_years)
        ct.update_temperature_values()
        ct.T_air.tofile("end_T_air.dat")
        # Note: nc time of 4000 corresponds to model date of Dec 15, 2010


def test_first_and_last_valid_dates():
    """ Test that first and last valid dates are read from netcdf file """
    ct = AlaskaTemperature()
    ct.initialize_from_config_file()
    assert datetime.date(1901, 1, 1) == ct._first_valid_date
    assert datetime.date(2009, 12, 31) == ct._last_valid_date


def test_jan_jul_arrays():
    """ test that AlaskaTemperature provides Jan and Jul values as individual arrays """
    ct = AlaskaTemperature()
    ct.initialize_from_config_file()
    expected_jan_val = -25.7
    expected_jul_val = 11.4

    assert ct.T_air_prior_jan[0, 0] == pytest.approx(expected_jan_val)
    assert ct.T_air_prior_jul[0, 0] == pytest.approx(expected_jul_val)
