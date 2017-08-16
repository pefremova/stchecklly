# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(name='stchecklly',
      version='0.0.3',
      description="Tool for generate and test statement transitions lists",
      include_package_data=True,
      packages=find_packages(exclude=['example', ]),
      install_requires=[],
      entry_points={
          'console_scripts': [
              'state_checker = stchecklly.command:main'
          ],
      },)
