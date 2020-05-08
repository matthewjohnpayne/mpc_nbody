#! /usr/bin/env python3
'''Just a little setup file with the basics, in case we ever need that.'''

import sys
from setuptools import setup

if sys.version_info[0] < 3:
    print('STOP USING PYTHON 2!!!')
    sys.exit(-1)

with open("README.md", "r") as fh:
    long_description = fh.read()

print("mpc_nbody unit-tests haven't been built into setup.py scripts. "
      "Please manually run '$ pytest tests/test_*.py' to ensure everything "
      "works before production use.")

dependencies = ['numpy >= 1.18.1',
                'argparse >= 1.1',
                'pytest >= 5.4.1',
                'astropy >= 4.0'
                ]

classifiers = ["Programming Languagge :: Python :: 3",
               "License :: OSI Approved :: MIT License",
               "Operating System :: OS Independent",
               "Development Status :: 2 - Pre-Alpha",
               "Intended Audience :: Science/Research",
               "Natural Language :: English",
               "Topic :: Scientific/Engineering :: Astronomy"
               ]

setup(name='mpc_nbody',
      version='0.1',
      author='Mike Alexandersen, Matthew J. Payne',
      author_email='mike.alexandersen@alumni.ubc.ca, mpayne@cfa.harvard.edu',
      description='Wrapper for parsing orbits, integrating nbody etc.',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/matthewjohnpayne/mpc_nbody',
      download_url='https://github.com/matthewjohnpayne/mpc_nbody.git',
      packages=['mpc_nbody'],
      classifiers=classifiers,
      keywords=['N-body', 'orbits'],
      license='MIT',
      install_requires=dependencies,
      )
