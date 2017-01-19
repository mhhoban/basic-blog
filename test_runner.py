"""
Test runner to run unit or functional automated tests
"""

import subprocess
import sys


if sys.argv[1] == '-unit':

    subprocess.call(['python -m unittest discover -s tests/unit_tests -p "*_tests.py"'], shell=True)

elif sys.argv[1] == '-functional':
    subprocess.call(['python -m unittest discover -s tests/functional_tests -p "*_tests.py"'], shell=True)

else:
    print('invalid selection, provide either -unit or -functional arg')
