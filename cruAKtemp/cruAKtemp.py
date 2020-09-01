# -*- coding: utf-8 -*-
"""
cruAKtemp.py

Reads average monthly temperature in Alaska from an upscaled version of
CRU NCEP data for Alaska
"""
from __future__ import print_function

import calendar
import datetime as dt
import os
import pathlib
import pkg_resources

import numpy as np
import yaml
from dateutil.relativedelta import relativedelta

# Using netcdf3
# from scipy.io.netcdf import NetCDFFile as Dataset
# Using netcdf4
from netCDF4 import Dataset
from nose.tools import assert_greater_equal, assert_less_equal, assert_true


data_directory = pathlib.Path(pkg_resources.resource_filename("cruAKtemp", "data"))
examples_directory = pathlib.Path(pkg_resources.resource_filename("cruAKtemp", "examples"))


def assert_between(value, minval, maxval):
    """Fail if value is not between minval and maxval"""
    assert_greater_equal(value, minval)
    assert_less_equal(value, maxval)


class CruAKtempMethod:
    def __init__(self):
        self._cru_temperature_nc_filename = None  # Name of input netcdf file
        self._cru_temperature_nc_filename_default = data_directory / "cruAKtemp.nc"
        # Default name of input netcdf file
        self._cru_temperature_ncfile = Dataset  # netCDF file handle
        self._cru_temperature = None  # This will point to the nc file data
        self._current_date = None  # Current num days since _start_date
        self._date_at_timestep0 = None  # this could be overwritten with set()
        self._latitude = None  # Will point to this model's latitude grid
        self._longitude = None  # Will point to this model's longitude grid
        self._temperature = None  # Will point to this model's temperature grid
        self.T_air = None  # Temperature grid
        self.T_air_prior_months = None  # Temperature grid each prior 12 months
        self.T_air_prior_jan = None  # Temperature grid prior January
        self.T_air_prior_jul = None  # Temperature grid prior July
        self.T_air_prior_year = None  # Temperature grid average prior 12 months
        self._time_units = "years"  # Timestep is in years
        self._timestep_duration = 0

        # The following are defined in config file
        self.cfg_file = ""
        self._nc_xdim = 0
        self._nc_ydim = 0
        self._nc_tdim = 0
        self._nc_i0 = 0
        self._nc_j0 = 0
        self._nc_i1 = 0
        self._nc_j1 = 0
        self._nc_iskip = 0
        self._nc_jskip = 0
        self._first_valid_date = dt.date(2000, 1, 1)
        self._last_valid_date = dt.date(1900, 1, 1)
        self._current_timestep = 0.0
        self._first_timestep = 0.0
        self._last_timestep = 0.0
        self.first_date = dt.date(1900, 1, 1)
        self.last_date = dt.date(1900, 1, 1)
        self._grid_shape = (1, 1)
        self.case_prefix = ""
        self.site_prefix = ""

        # Month day for 'canonical' date-of-year
        self.month = 12
        self.day = 15

    def verify_config_for_uniform_rectilinear_run(self, cfg):
        # Need at least one grid
        if len(cfg["grids"]) < 1:
            raise ValueError("at least one grid is required")

        # All grids need a valid data type
        # name is a string, type is a type
        for k, v in cfg["grids"].items():
            if not isinstance(k, str):
                raise ValueError("grid keys must be a string")
            if not isinstance(type(v), type):
                raise ValueError("grid values must be a type")

        # Grid shape can be used to create a numpy array
        assert_true(isinstance(cfg["grid_shape"], tuple))
        try:
            test_array = np.zeros(cfg["grid_shape"], dtype=np.uint8)
            assert_true(test_array is not None)
        except:
            print(
                "Grid shape can't be used for numpy array: %s" % str(cfg["grid_shape"])
            )
            raise

    def verify_config_for_rectilinear_run(self, cfg):
        # Need at least one grid
        assert_greater_equal(len(cfg["grids"]), 1)

        # All grids need a valid data type
        # name is a string, type is a type
        for k, v in cfg["grids"].items():
            assert_true(isinstance(k, str))
            assert_true(isinstance(type(v), type))

        # Grid shape can be used to create a numpy array
        assert_true(isinstance(cfg["grid_shape"], tuple))
        try:
            test_array = np.zeros(cfg["grid_shape"], dtype=np.uint8)
            assert_true(test_array is not None)
        except:
            print(
                "Grid shape can't be used for numpy array: %s" % str(cfg["grid_shape"])
            )
            raise

    def get_config_from_oldstyle_file(self, cfg_filename):
        cfg_struct = {}
        grid_struct = {}
        try:
            with open(cfg_filename, "r") as cfg_file:
                # this is based loosely on read_config_file in BMI_base.py
                while True:
                    # Read lines from config file until no more remain
                    line = cfg_file.readline()
                    if line == "":
                        break

                    # Comments start with '#'
                    COMMENT = line[0] == "#"

                    words = line.split("|")
                    if (len(words) == 4) and (not COMMENT):
                        var_name = words[0].strip()
                        value = words[1].strip()
                        var_type = words[2].strip()

                        # Process the variables based on variable name
                        if var_name[-4:] == "date":
                            # date variables end with "_date"
                            cfg_struct[var_name] = dt.datetime.strptime(
                                value, "%Y-%m-%d"
                            ).date()
                        elif var_name[0:4] == "grid":
                            # grid variables are processed after cfg file read
                            grid_struct[var_name] = value
                        elif var_name == "timestep":
                            # timestep is now a number of years
                            cfg_struct[var_name] = int(value)
                        elif var_type == "int":
                            # Convert integers to int
                            cfg_struct[var_name] = int(value)
                        elif var_type == "long":
                            # Convert longs to int
                            cfg_struct[var_name] = int(value)
                        else:
                            # Everything else is just passed as a string
                            cfg_struct[var_name] = value

        except:
            print(
                "\nError opening configuration file in\
                  initialize_from_config_file()"
            )
            raise

        """
        print(" ")
        for key in cfg_struct.keys():
            print("%s: %s" % (str(key), str(cfg_struct[key])))

        exit(0)
        """

        # After reading the files, process the grid_struct values
        cfg_struct["grid_shape"] = (
            int(grid_struct["grid_columns"]),
            int(grid_struct["grid_rows"]),
        )
        cfg_struct["grid_type"] = grid_struct["grid_type"]
        cfg_struct["grids"] = {grid_struct["grid_name"]: "np.float"}

        return cfg_struct

    def get_config_from_yaml_file(self, cfg_filename):
        cfg_struct = None
        try:
            with open(cfg_filename, "r") as cfg_file:
                cfg_struct = yaml.load(cfg_file)
        except:
            print(
                "\nError opening configuration file in\
                  initialize_from_config_file()"
            )
            raise

        return cfg_struct

    def verify_run_type_parameters(self, cfg_struct):
        # There should be a separate verify_config_for_<gridtype>_run()
        # routine for each type of grid
        try:
            exec("self.verify_config_for_%s_run(cfg_struct)" % cfg_struct["grid_type"])
        except:
            raise

    def verify_temperature_netcdf_for_region_resolution(self, cfg_struct):
        try:
            if (
                cfg_struct["run_resolution"] == "lowres"
                and cfg_struct["run_region"] == "Alaska"
            ):
                return data_directory / "cru_alaska_lowres_temperature.nc"
        except:
            # Likely a KeyError because missing a region or resolution
            raise

        raise ValueError(
            "Combination of run_region '%s' and run_resolution '%s' not recognized"
            % (cfg_struct["run_region"], cfg_struct["run_resolution"])
        )

    def i_nc_from_i(self, i, inverse=False, check_bounds=False):
        """Convert model's i-index to cru file's index
        Input: i  the i-coordinate of the model grid
        Output: i_nc  the coordinate in the netcdf grid
        inverse: if True, reverse the Input and Outpu
        check_bounds: if True, verify that all values are valid
        """
        if not inverse:
            if check_bounds:
                assert_between(i, 0, self._grid_shape[0] - 1)
            i_nc = self._nc_i0 + i * self._nc_iskip
            if check_bounds:
                assert_between(i_nc, 0, self._nc_xdim)
            return i_nc
        else:
            i_nc = i
            if check_bounds:
                assert_between(i_nc, 0, self._nc_xdim)
            i = (i_nc - self._nc_i0) / self._nc_iskip
            if check_bounds:
                assert_between(i, 0, self._grid_shape[0] - 1)
            return i

    def j_nc_from_j(self, j, inverse=False, check_bounds=False):
        """Convert model's j-index to cru file's index
        Input: j  the j-coordinate of the model grid
        Output: j_nc  the coordinate in the netcdf grid
        inverse: if True, reverse the Input and Outpu
        check_bounds: if True, verify that all values are valid
        """
        if not inverse:
            if check_bounds:
                assert_between(j, 0, self._grid_shape[1] - 1)
            j_nc = self._nc_j0 + j * self._nc_jskip
            if check_bounds:
                assert_between(j_nc, 0, self._nc_xdim)
            return j_nc
        else:
            j_nc = j
            if check_bounds:
                assert_between(j_nc, 0, self._nc_ydim)
            j = (j_nc - self._nc_j0) / self._nc_jskip
            if check_bounds:
                assert_between(j, 0, self._grid_shape[1] - 1)
            return j

    def get_first_last_dates_from_nc(self):
        try:
            nc_time_var = self._cru_temperature_ncfile.variables["time"]
            nc_time_units = nc_time_var.getncattr("time_units").split()
            for part in nc_time_units:
                # Most of these "part"s will fail,
                # but the 'time_units' value will execute the try clause
                try:
                    # If we get a datestring of YYYY-MM-DD, parse it
                    reference_time = dt.datetime.strptime(part, "%Y-%m-%d").date()

                    # First valid day is first day of month of first_date
                    days_to_first_day = dt.timedelta(days=int(nc_time_var[0]))
                    start_date = reference_time + days_to_first_day
                    self._first_valid_date = dt.date(
                        start_date.year, start_date.month, 1
                    )

                    # Last valid day is last day of month of last_date
                    num_days = len(nc_time_var)
                    days_to_last_day = dt.timedelta(days=int(nc_time_var[num_days - 1]))
                    last_date = reference_time + days_to_last_day
                    day = calendar.monthrange(last_date.year, last_date.month)[1]
                    self._last_valid_date = dt.date(
                        last_date.year, last_date.month, day
                    )
                    break
                except ValueError:
                    # Expect most 'parts' of nc_time_units not to be date
                    pass
        except:
            raise

    def initialize_from_config_file(self, cfg_filename=None):
        cfg_struct = None

        # Set the cfg file if it exists, otherwise, a default
        if not cfg_filename:
            # No config file specified, use a default
            cfg_filename = examples_directory / "default_temperature.cfg"

        cfg_struct = self.get_config_from_oldstyle_file(cfg_filename)

        # Verify that the parameters are correct for the grid type
        self.verify_run_type_parameters(cfg_struct)

        # Get the temperature netcdf file name
        self._cru_temperature_nc_filename = self.verify_temperature_netcdf_for_region_resolution(
            cfg_struct
        )

        # Open the netcdf files
        self._cru_temperature_ncfile = Dataset(
            self._cru_temperature_nc_filename, "r", mmap=True
        )
        assert_true(self._cru_temperature_ncfile is not None)

        # Initialize the time variables
        try:
            # From config
            self._timestep_duration = cfg_struct["timestep"]

            # first_date and last_date are years from cfg file
            self.first_date = dt.date(
                cfg_struct["model_start_year"], self.month, self.day
            )
            # This could be set externally, eg by WMT
            if self._date_at_timestep0 is None:
                self._date_at_timestep0 = self.first_date

            self.last_date = dt.date(cfg_struct["model_end_year"], self.month, self.day)

            self.get_first_last_dates_from_nc()

            # Ensure that model dates are okay
            assert_between(
                self._date_at_timestep0, self._first_valid_date, self._last_valid_date
            )
            assert_between(
                self.first_date, self._first_valid_date, self._last_valid_date
            )
            assert_between(
                self.last_date, self._first_valid_date, self._last_valid_date
            )

            # Initial calculations, assuming units of days
            self._current_date = self._date_at_timestep0
            self._first_timestep = self.timestep_from_date(self.first_date)
            self._last_timestep = self.timestep_from_date(self.last_date)
            self._current_timestep = self._first_timestep
        except:
            raise

        # Allocate the grids
        self._grid_shape = cfg_struct["grid_shape"]
        for g in cfg_struct["grids"]:
            grid_assignment_string = "self.%s_grid = np.zeros(%s, dtype=%s)" % (
                g,
                self._grid_shape,
                cfg_struct["grids"][g],
            )
            # (g, cfg_struct['grid_shape'], cfg_struct['grids'][g])
            exec(grid_assignment_string)

        # Set the netcdf offset arrays
        # This should eventually be done non-manually
        self._nc_i0 = cfg_struct["i_ul"]
        self._nc_j0 = cfg_struct["j_ul"]
        try:
            self._nc_iskip = cfg_struct["i_skip"]
        except KeyError:
            self._nc_iskip = 1
        try:
            self._nc_iskip = cfg_struct["j_skip"]
        except KeyError:
            self._nc_jskip = 1

        # Calculate the end points
        self._nc_i1 = self.i_nc_from_i(self._grid_shape[0])
        self._nc_j1 = self.j_nc_from_j(self._grid_shape[1])

        # Read in the latitude and longitude arrays
        nc_latitude = self._cru_temperature_ncfile.variables["lat"]
        self._latitude = np.asarray(
            nc_latitude[
                self._nc_j0 : self._nc_j1 : self._nc_jskip,
                self._nc_i0 : self._nc_i1 : self._nc_iskip,
            ]
        ).astype(np.float32)
        nc_longitude = self._cru_temperature_ncfile.variables["lon"]
        self._longitude = np.asarray(
            nc_longitude[
                self._nc_j0 : self._nc_j1 : self._nc_jskip,
                self._nc_i0 : self._nc_i1 : self._nc_iskip,
            ]
        ).astype(np.float32)

        # If the variables that point to the netcdfile's variables
        # aren't independently closed, then a RuntimeWarning will be raised
        # when the program ends or thenetcdf file is closed
        nc_latitude = None
        nc_longitude = None

        # Read initial data
        # Set the temperature file data to a variable
        # Note: This is probably fine for a small file, but it may not be
        # the best way to read from files that are several GB in size
        nc_temperature = self._cru_temperature_ncfile.variables["temp"]
        self._temperature = np.asarray(
            nc_temperature[
                :,
                self._nc_j0 : self._nc_j1 : self._nc_jskip,
                self._nc_i0 : self._nc_i1 : self._nc_iskip,
            ]
        ).astype(np.float32)
        # Deduce the model xdim and ydim from the size of this array
        self._nc_tdim = nc_temperature.shape[0]
        self._nc_ydim = nc_temperature.shape[1]
        self._nc_xdim = nc_temperature.shape[2]

        nc_temperature = None

        # Set the T_air values--which are the "model results--
        # from the _temperature[] grid--which is the full lowres dataset
        self.update_temperature_values()

        # Close the netcdf file
        # Note: this will need to change if reading larger files and
        # accessing data from the files as time goes on
        self._cru_temperature_ncfile.close()
        self._cru_temperature_ncfile = None

    def timestep_from_date(self, this_date):
        """Return the timestep from a date
        Note: assumes that the model's time values have been initialized
        Note: this may be inaccurate if partial timesteps (year) are used
        """
        this_timestep = this_date.year - self._date_at_timestep0.year
        return this_timestep

    def increment_date(self, change_amount=None):
        """Change the current date by a timedelta amount
        and update the timestep to reflect that change
        """
        if change_amount is None:
            change_amount = self._timestep_duration

        self._current_date += relativedelta(years=change_amount)
        self._current_timestep = self.timestep_from_date(self._current_date)

    def get_current_timestep(self):
        return self.timestep_from_date(self._current_date)

    def get_end_timestep(self):
        return self.timestep_from_date(self.last_date)

    def update(self, frac=None):
        # Update can handle fractional timesteps...sort of
        if frac is not None:
            print("Fractional times not yet permitted, rounding to nearest int")
            time_change = self._timestep_duration * int(frac + 0.5)
        else:
            time_change = self._timestep_duration

        for n in range(time_change):
            # Update values for one timestep
            self.increment_date()

        self.update_temperature_values()

    def get_time_index(self, month, year):
        """ Return the index of the time coordinate of the netcdf file
            for a specified month and year """
        return month + 12 * (year - self._first_valid_date.year) - 1

    def get_temperatures_month_year(self, month, year):
        """ Return the temperature field at specified month, year """
        # Check for valid month, year
        try:
            testdate = dt.date(year, month, 1)
        except:
            raise ValueError(
                "Month (%d) and Year (%d) can't be made a date" % (month, year)
            )

        testdate = dt.date(year, month, 1)
        # Check that month, year are in range
        idx = self.get_time_index(month, year)
        assert idx >= 0
        if (testdate < self._first_valid_date) or (testdate > self._last_valid_date):
            return np.zeros_like(self._temperature[idx, :, :]).fill(np.nan)

        return self._temperature[idx, :, :]

    def update_temperature_values(self):
        """Update the temperature array values based on the current date

           This model now provides not just the "current" temperature
           but also the previous monthly means for the this and the preceding
           11 months, and the annual average for the last 12 months
        """
        year = self._current_date.year
        month = self._current_date.month
        self.T_air = self.get_temperatures_month_year(month, year)
        self.T_air_prior_months = []

        for monthnum in np.arange(-11, 1):
            thisdate = self._current_date + relativedelta(months=monthnum)
            self.T_air_prior_months.append(
                self.get_temperatures_month_year(thisdate.month, thisdate.year)
            )
        self.T_air_prior_jan = self.T_air_prior_months[0]
        self.T_air_prior_jul = self.T_air_prior_months[6]
        self.T_air_prior_year = np.average(self.T_air_prior_months, axis=0)

    def read_config_file(self):
        # Open CFG file to read data
        cfg_unit = open(self.cfg_file, "r")
        last_var_name = ""

        while True:
            line = cfg_unit.readline()
            if line == "":
                break  # (reached end of file)

            # Comments are lines that start with '#'
            COMMENT = line[0] == "#"

            # Columns are delimited by '|'
            words = line.split("|")

            # Only process non-comment lines with exactly 4 words
            # Note: the 4th word describes the variable, and is ignored
            if (len(words) == 4) and not COMMENT:
                var_name = words[0].strip()
                value = words[1].strip()
                var_type = words[2].strip()

                READ_SCALAR = False
                READ_FILENAME = False

                # Does var_name end with an array subscript ?
                p1 = var_name.rfind("[")
                p2 = var_name.rfind("]")
                if (p1 > 0) and (p2 > p1):
                    var_base = var_name[:p1]
                    subscript = var_name[p1 : p2 + 1]
                    var_name_file_str = var_base + "_file" + subscript
                else:
                    var_base = var_name
                    var_name_file_str = var_name + "_file"

                # if the immediately preceding line describes this variables's
                # type, change the type of this variable
                if last_var_name.startswith(var_base + "_type"):
                    type_choice = "undefined"
                    exec("type_choice = self." + last_var_name)
                    if type_choice.lower() == "scalar":
                        exec("self." + var_name_file_str + " = ''")
                        READ_SCALAR = True
                    else:
                        exec("self." + var_name + " = 0.0")
                        READ_FILENAME = True

                # -----------------------------------
                # Read a value of type "var_type"
                # -----------------------------------
                # Convert scalars to numpy scalars
                # -----------------------------------
                if var_type in ["float64", "np.float64"]:
                    value = np.float64(value)
                    exec("self." + var_name + " = value")
                elif var_type in ["float32", "np.float32"]:
                    value = np.float32(value)
                    exec("self." + var_name + " = value")
                elif var_type in ["long", "long int", "np.int64"]:
                    value = np.int64(value)
                    exec("self." + var_name + " = value")
                elif var_type in ["int", "np.int32"]:
                    value = np.int32(value)
                    exec("self." + var_name + " = value")
                elif var_type in ["short", "short int", "int16", "np.int16"]:
                    value = np.int16(value)
                    exec("self." + var_name + " = value")
                elif var_type == "string":
                    # Replace [case_prefix] or [site_prefix] in a string's value
                    # with the appropriate values
                    case_str = "[case_prefix]"
                    site_str = "[site_prefix]"
                    s = value
                    if s[:13] == case_str:
                        value_str = self.case_prefix + s[13:]
                    elif s[:13] == site_str:
                        value_str = self.site_prefix + s[13:]
                    else:
                        value_str = s

                    assert value_str is not None

                    # If var_name starts with "SAVE_" and value is
                    # Yes or No, then convert to Python boolean.
                    if var_name[:5] == "SAVE_":
                        VALUE_SET = True
                        if s.lower() in ["yes", "true"]:
                            exec("self." + var_name + " = True")
                        elif s.lower() in ["no", "false"]:
                            exec("self." + var_name + " = False")
                        else:
                            VALUE_SET = False
                    else:
                        VALUE_SET = False

                    # If string wasn't a SAVE_ variable, set it here
                    if not VALUE_SET:
                        if READ_FILENAME:
                            exec("self." + var_name_file_str + " = value_str")
                        elif READ_SCALAR:
                            exec("self." + var_name + " = np.float64(value_str)")
                        else:
                            exec("self." + var_name + " = value_str")
                else:
                    raise ValueError(
                        "In read_config_file(), unsupported data type: %d" % var_type
                    )

                last_var_name = var_name
