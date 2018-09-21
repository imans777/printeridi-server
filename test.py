
__author__ = "Iman Sahebi <iman.s_sani@yahoo.com>"
__license__ = "The MIT License <http://opensource.org/licenses/MIT>"
__copyright__ = "Copyright (C) 2018 Iman Sahebi - Released under terms of the MIT License"


def run_tests(verbosity=2):
    import unittest
    loader = unittest.TestLoader()
    # TODO: get the directory as an input
    # because running all tests for a single thing is not GOOD!
    tests = loader.discover('tests')
    result = unittest.TextTestRunner(verbosity=verbosity).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    import os
    os.environ['ENV_MODE'] = 'test'

    import sys
    if '-q' in sys.argv:
        run_tests(0)
    elif '-v' in sys.argv:
        run_tests(2)
    else:
        run_tests(1)
