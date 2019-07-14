from setuptools import setup

setup(
    name='daikin-pi',
    version='0.1',
    description='IR Sender and MQTT Client for Daikin Split System AC on RasPi',
    url='http://github.com/dannyshaw/daikin-pi',
    author='Danny Shaw',
    author_email='code@dannyshaw.io',
    license='MIT',
    packages=['daikin-pi'],
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose'],
)
