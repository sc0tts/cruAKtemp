"""tests subpackage for cruAKtemp

Provides:
    cruAKtemp_directory: the 'root' directory of the cruAKtemp module
    tests_directory: the directory containing the module's automated tests
    data_directory: the directory where installed data files are found
    examples_directory: the directory where installed data files are found
"""

import os

tests_directory = os.path.dirname(__file__)
cruAKtemp_directory = os.path.join(tests_directory, '..')
data_directory = os.path.join(cruAKtemp_directory, 'data')
examples_directory = os.path.join(cruAKtemp_directory, 'examples')

