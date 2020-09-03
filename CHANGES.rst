Changelog for cru_alaska_temperature
====================================

0.2.0 (unreleased)
------------------

- Renamed package, modules, and classes to follow Python naming conventions

- Updated the cruAKtemp BMI for BMI version 2 and added bmi-tester
  to the continuous integration builds (#16)

- Updated the pymt model metadata and moved it into the data folder
  of the package (#15)

- Added continuous integration for Linux, Mac, and Windows using Travis and AppVeyor

- Changed to use pytest for testing (removed nose)

- Moved tests outside of package

- Lots of reorganization


0.1.1 (2018-03-19)
------------------

- Fixed BMI update_until method to take a float argument

0.1.0 (2018-03-15)
------------------

- Initial release
