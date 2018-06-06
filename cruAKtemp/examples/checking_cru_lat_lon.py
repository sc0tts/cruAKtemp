"""
couple_cru_KUGeo.py

Example that couples cruAKtemp to KUGeo!

"""

from __future__ import print_function

import numpy as np
from netCDF4 import Dataset

from cruAKtemp.bmi_cruAKtemp import BmiCruAKtempMethod
from cruAKtemp.tests import data_directory

# Initial both components with local config files
cru_config_file = "default_temperature.cfg"

cru = BmiCruAKtempMethod()

cru.initialize(cru_config_file)

n_x_0 = cru._model._nc_i0
n_y_0 = cru._model._nc_j0
n_x_1 = cru._model._nc_i1
n_y_1 = cru._model._nc_j1

t   = cru.get_current_time()

lat = cru.get_value('latitude')
lon = cru.get_value('longitude')
tmp = cru.get_value('atmosphere_bottom_air__temperature')

tmp = np.ma.masked_less_equal(tmp, -90.)

#print ('from BMI:', lat.max(),lat.min(), tmp.max(), tmp.min())

example_filename = data_directory + '/'+'cru_alaska_lowres_temperature.nc'

# First: check the exact extent by column and row:

ncid = Dataset(example_filename)

lat_raw = ncid.variables['lat'][n_y_0:n_y_1,n_x_0:n_x_1]
lon_raw = ncid.variables['lon'][n_y_0:n_y_1,n_x_0:n_x_1]
lon_raw = ncid.variables['lon'][n_y_0:n_y_1,n_x_0:n_x_1]
tmp_raw = ncid.variables['temp'][0,n_y_0:n_y_1,n_x_0:n_x_1]

tmp_raw = np.ma.masked_less_equal(tmp_raw, -90.)

#print ('netCDF:', lat_raw.max(),lat_raw.min(), tmp_raw.max(), tmp_raw.min())

lat_cmp = np.abs(lat_raw - lat)
lon_cmp = np.abs(lon_raw - lon)
tmp_cmp = np.abs(tmp_raw - tmp)

if (lat_cmp.max()>1E-7 or lon_cmp.max()>1E-7):
    raise RuntimeError('Error')

