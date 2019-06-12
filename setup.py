from setuptools import setup, find_packages

setup(
    name='Daikin Pi',
    url='https://github.com/dannyshaw/daikin-pi',
    author='Danny Shaw',
    author_email='code@dannyshaw.io',
    packages=find_packages(),
    install_requires=['flask'],
    classifiers=['Programming Language :: Python :: 3.5'],
    version='0.1',
    license='MIT',
    description=
    'An IR Gateway for a Daikin Split System AC, (requires lircd configured)',
    zip_safe=False,
    extras_require={'testing': ['pytest']})
