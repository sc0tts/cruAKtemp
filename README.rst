cruAKtemp
=========

.. note::

  cruAKtemp is still in development and likely does not yet work
  as a package or pymt component

.. note::
  This version does *not* contain the netcdf file!  Because uncompressed,
  it is too large for github.

The Python package *cruAKtemp* provides access to a subsample of CRU NCEP
data temperature for Alaska from:

  http://ckan.snap.uaf.edu/dataset/historical-monthly-and-derived-temperature-products-771m-cru-ts

The geographical extent of this dataset has been reduced to greatly reduce 
the number of ocean or Canadian pixels.  Also, the spatial resolution has
been reduced by a factor of 13 in each direction, resulting in an effective
pixel resolution of about 10km.

The data are monthly average temperatures for each month from January 1901
through December 2009.

BMI
---

The original dataset was in the form of a set of geotiff files.  This 
package provides access to the data via BMI functions and the data itself
is encoded as a single netCDF file.

bmi-tester
----------

If you have installed CSDMS's 'bmi-tester' package, you can verify that
cruAKtemp is BMI-compliant by running:

.. code:: bash

   $ bmi-tester cruAKtemp:BmiCruAKtempMethod 
