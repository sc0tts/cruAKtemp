# -*- coding: utf-8 -*-
"""
bmi_cruAKtemp.py

Provides BMI access to netcdf files containg cruNCEP data for
monthly temperature values for Alaska

For use with Permamodel components

"""
import os
import pathlib
import pkg_resources

import numpy as np

from .alaska_temperature import AlaskaTemperature
"""
class FrostnumberMethod( frost_number.BmiFrostnumberMethod ):
    _thisname = 'this name'
"""

examples_directory = pathlib.Path(
    pkg_resources.resource_filename("cru_alaska_temperature", "examples")
)


class AlaskaTemperatureBMI(object):
    """Provides BMI interface to CRU Alaska Temperature data"""

    METADATA = pkg_resources.resource_filename(
        "cru_alaska_temperature", "data/AlaskaTemperatureBMI"
    )

    def __init__(self):
        self._model = None
        self._values = {}
        self._var_units = {}
        self._grids = {}
        self._grid_type = {}

        self._name = "AlaskaTemperature"

        self._att_map = {
            "model_name": "PermaModel_cruAKtemp",
            "version": "0.1",
            "author_name": "J. Scott Stewart",
            "grid_type": "uniform_rectlinear",
            "time_step_type": "fixed",
            "step_method": "explicit",
            "comp_name": "AlaskaTemperatureBMI",
            "model_family": "PermaModel",
            "cfg_extension": "_cruAKtemp_model.cfg",
            "time_units": "days",
        }

        self._input_var_names = ()

        self._output_var_names = (
            "atmosphere_bottom_air__temperature",
            "atmosphere_bottom_air__temperature_mean_jan",
            "atmosphere_bottom_air__temperature_mean_jul",
            "atmosphere_bottom_air__temperature_year",
        )

        self._var_name_map = {
            "atmosphere_bottom_air__temperature": "T_air",
            "atmosphere_bottom_air__temperature_mean_jan": "T_air_prior_jan",
            "atmosphere_bottom_air__temperature_mean_jul": "T_air_prior_jul",
            "atmosphere_bottom_air__temperature_year": "T_air_prior_year",
        }

        self._var_units_map = {
            "atmosphere_bottom_air__temperature": "deg_C",
            "atmosphere_bottom_air__temperature_mean_jan": "deg_C",
            "atmosphere_bottom_air__temperature_mean_jul": "deg_C",
            "atmosphere_bottom_air__temperature_year": "deg_C",
            "datetime__start": "days",
            "datetime__end": "days",
        }

    def initialize(self, cfg_file=None):
        self._model = AlaskaTemperature()

        self._model.initialize_from_config_file(cfg_filename=cfg_file)

        self._name = "Permamodel CRU-AK Temperature Component"

        # Verify that all input and output variable names are mapped
        for varname in self._input_var_names:
            assert varname in self._var_name_map
            assert varname in self._var_units_map
        for varname in self._output_var_names:
            assert varname in self._var_name_map
            assert varname in self._var_units_map

        # Set a unique grid number for each grid
        gridnumber = 0
        for varname in self._input_var_names:
            self._grids[gridnumber] = varname
            self._grid_type[gridnumber] = "uniform_rectilinear"
            gridnumber += 1
        for varname in self._output_var_names:
            self._grids[gridnumber] = varname
            self._grid_type[gridnumber] = "uniform_rectilinear"
            gridnumber += 1

        self._values = {
            # These are the links to the model's variables and
            # should be consistent with _var_name_map
            "atmosphere_bottom_air__temperature": self._model.T_air,
            "atmosphere_bottom_air__temperature_mean_jan": self._model.T_air_prior_jan,
            "atmosphere_bottom_air__temperature_mean_jul": self._model.T_air_prior_jul,
            "atmosphere_bottom_air__temperature_year": self._model.T_air_prior_year,
            "datetime__start": self._model.first_date,
            "datetime__end": self._model.last_date,
        }

    def get_attribute(self, att_name):

        try:
            return self._att_map[att_name.lower()]
        except KeyError:
            print("###################################################")
            print(" ERROR: Could not find attribute: %s" % str(att_name))
            print("###################################################")
            print(" ")

    def get_input_var_names(self):
        return self._input_var_names

    def get_output_var_names(self):
        return self._output_var_names

    def get_start_time(self):
        # Currently, all models must start from timestep zero
        return np.float64(0)

    def get_var_location(self, long_var_name):
        return "node"

    def get_var_name(self, long_var_name):
        return self._var_name_map[long_var_name]

    def get_var_units(self, long_var_name):
        return self._var_units_map[long_var_name]

    def get_current_time(self):
        return self._model.get_current_timestep()

    def get_end_time(self):
        return self._model.get_end_timestep()

    def get_time_units(self):
        return self._model._time_units

    def update(self):
        # Update the time
        self._model.update()

        # Set the bmi temperature to the updated value in the model
        self._values["atmosphere_bottom_air__temperature"] = self._model.T_air
        self._values[
            "atmosphere_bottom_air__temperature_mean_jan"
        ] = self._model.T_air_prior_jan
        self._values[
            "atmosphere_bottom_air__temperature_mean_jul"
        ] = self._model.T_air_prior_jul
        self._values[
            "atmosphere_bottom_air__temperature_year"
        ] = self._model.T_air_prior_year

    def update_frac(self, time_fraction):
        """
        Model date is a floating point number of days.  This
        can be updated by fractional day, but update() will
        only be called if the integer value of the day changes
        """
        self._model.increment_date(
            change_amount=time_fraction * self._model._timestep_duration
        )
        self._model.update_temperature_values()

        self._model.update(frac=time_fraction)
        self._values["atmosphere_bottom_air__temperature"] = self._model.T_air
        self._values[
            "atmosphere_bottom_air__temperature_mean_jan"
        ] = self._model.T_air_prior_jan
        self._values[
            "atmosphere_bottom_air__temperature_mean_jul"
        ] = self._model.T_air_prior_jul
        self._values[
            "atmosphere_bottom_air__temperature_year"
        ] = self._model.T_air_prior_year

    def update_until(self, time):
        """Advance model state until the given time.

        Parameters
        ----------
        time : float
          A model time value.

        """
        stop_year = time + self._model._date_at_timestep0.year

        if stop_year < self._model._current_date.year:
            print(
                "Warning: update_until date--%d--is less than current\
                  date--%d"
                % (stop_year, self._model._current_date.year)
            )
            print("  no update run")
            return

        if stop_year > self._model.last_date.year:
            print("Warning: update_until date--%d" % stop_year)
            print("  was greater than end_date--%d." % self._model.last_date.year)
            print("  Setting stop_year to last_date")
            stop_year = self._model.last_date.year

        # Run update() one timestep at a time until stop_year
        while self._model._current_date.year < stop_year:
            self.update()

    def finalize(self):
        pass

    def get_grid_type(self, grid_number):
        return self._grid_type[grid_number]

    def get_time_step(self):
        # Model keeps track of timestep as a timedelta
        # Here, find the seconds and divide by seconds/day
        # to get the number of days
        return float(self._model._timestep_duration)

    def get_value_ref(self, var_name):
        return self._values[var_name]

    def set_value(self, var_name, new_var_values):
        val = self.get_value_ref(var_name)
        val[:] = new_var_values

    def set_value_at_indices(self, var_name, new_var_values, indices):
        self.get_value_ref(var_name).flat[indices] = new_var_values

    def get_var_itemsize(self, var_name):
        return np.asarray(self.get_value_ref(var_name)).flatten()[0].nbytes

    def get_value_at_indices(self, var_name, indices):
        return self.get_value_ref(var_name).take(indices)

    def get_var_nbytes(self, var_name):
        return np.asarray(self.get_value_ref(var_name)).nbytes

    def get_value(self, var_name, out):
        out[:] = self.get_value_ref(var_name).flat

    def get_var_type(self, var_name):
        return str(self.get_value_ref(var_name).dtype)

    def get_component_name(self):
        return self._name

    def get_var_grid(self, var_name):
        for grid_id, var_name_list in self._grids.items():
            if var_name in var_name_list:
                return grid_id

    def get_grid_shape(self, grid_id, shape):
        """Number of rows and columns of uniform rectilinear grid."""
        var_on_grid = self._grids[grid_id]
        shape[:] = self.get_value_ref(var_on_grid).shape
        return shape

    def get_grid_size(self, grid_id):
        var_on_grid = self._grids[grid_id]
        return self.get_value_ref(var_on_grid).size

    # Todo: Revise once we can work with georeferenced data in the CMF.
    def get_grid_spacing(self, grid_id, spacing):
        spacing[:] = (10000.0, 10000.0)
        return spacing

    # Todo: Revise once we can work with georeferenced data in the CMF.
    def get_grid_origin(self, grid_id, origin):
        origin[:] = (0.0, 0.0)
        return origin

    def get_grid_rank(self, grid_id):
        var_on_grid = self._grids[grid_id]
        return self.get_value_ref(var_on_grid).ndim

    def get_grid_node_count(self, grid_id):
        var_on_grid = self._grids[grid_id]
        return self.get_value_ref(var_on_grid).size


if __name__ == "__main__":
    # Execute standalone test run
    crumeth = AlaskaTemperatureBMI()
    crumeth.initialize(
        cfg_file=os.path.join(examples_directory, "default_temperature.cfg")
    )
    crumeth.update()
    print("After one timestep, value of temperature array:")
    print("  (This should be cruAKtemp for Dec 1903 (index=36 in Panoply)")
    print("  (Starting at Panoply's (51, 26) which is (50, 25) in ")
    print("     0-based notation")
    print(crumeth._values["atmosphere_bottom_air__temperature"])
    print("Current timestep (should be 1): %s" % str(crumeth.get_current_time()))
    crumeth.finalize()
