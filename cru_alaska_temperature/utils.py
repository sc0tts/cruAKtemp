"""cruAKtemp_utils.py

Utility routines for the cruAKtemp package
"""
import datetime
import errno
import os
import sys

import numpy as np
import yaml


def write_gridfile(gridname, gridshape=(1,), gridtype=np.float, filename=None):
    """write_grid: Creates a grid for permamodel runs
    gridshape: the dimensions of the grid array [default is a single point]
    gridtype:  the data type of the grid [default 4-byte floats]
    filename:  the file to write the yaml description to [default None
                 which means return the description
    """
    # Ensure that the grid description is legal
    try:
        np.zeros(gridshape, dtype=gridtype)
    except TypeError:
        raise ValueError(
            "Can't create grid of shape %s and type %s: %s"
            % (str(gridshape), str(gridtype), sys.exc_info()[0])
        )
    griddict = {}
    griddict["gridname"] = gridname
    griddict["gridshape"] = gridshape
    griddict["gridtype"] = gridtype

    # Write the grid description to the provided filename or return it
    contents = yaml.dump(griddict, default_flow_style=False)
    if filename is not None:
        with open(filename, "w") as fp:
            fp.write(contents)
    else:
        return contents


def generate_default_temperature_run_cfg_file(
    filename=None, overwrite=False, SILENT=True
):
    """generate_default_temperature_run_cfg_file:
    Creates a default configuration file for cruAKtemp
    """
    cfgdict = {}
    # Description of model run
    cfgdict["run_description"] = "north slope subset of upscaled cru-ncep temp data"
    cfgdict["run_region"] = "Alaska"

    # Grid description
    cfgdict["grid_type"] = "uniform_rectilinear"
    cfgdict["run_resolution"] = "lowres"
    cfgdict["run_resolution"] = "lowres"
    cfgdict["grid_shape"] = (40, 20)
    cfgdict["i_ul"] = 50
    cfgdict["j_ul"] = 25

    # Time description
    cfgdict["timestep"] = datetime.timedelta(days=1)
    # cfgdict['reference_date'] = datetime.date(1900, 1, 1)
    cfgdict["reference_date"] = datetime.datetime(1900, 1, 1)
    cfgdict["model_start_date"] = datetime.datetime(1902, 1, 1)
    cfgdict["model_end_date"] = datetime.datetime(1910, 12, 31)
    cfgdict["dataset_start_date"] = datetime.datetime(1901, 1, 1)
    cfgdict["dataset_end_date"] = datetime.datetime(2009, 12, 31)
    cfgdict["grids"] = {"temperature": "np.float"}

    if filename is None:
        filename = "default_temperature.cfg"
    cfgdict["filename"] = filename

    if overwrite:
        with open(filename, "w") as fp:
            yaml.dump(cfgdict, fp)
    else:
        fileflags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
        try:
            yamlfile_handle = os.open(filename, fileflags)
        except OSError as e:
            if e.errno == errno.EEXIST:
                if not SILENT:
                    print("config file exists, not overwritten: %s" % filename)
                else:
                    pass
            else:
                raise
        else:
            with os.fdopen(yamlfile_handle, "w") as yamlfile:
                yaml.dump(cfgdict, yamlfile)
            return None
