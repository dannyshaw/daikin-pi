import sys

if sys.version_info <= (3, 6):
    raise ValueError(
        'This library requires at least Python 3.6. ' +
        'You\'re running version {}.{} from {}.'.format(
            sys.version_info.major, sys.version_info.minor, sys.executable))
