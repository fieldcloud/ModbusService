#!/usr/bin/env python

try:
    with open('package_description.rst', 'r') as file_description:
		description = file_description.read()
except IOError:
    description = "https://github.com/fieldcloud/ModbusService"

from setuptools import setup, find_packages

#import FlclModbus

setup(
    name = "FlclModbus",
    version = "0.1.0",

    description = "Python library used to easily develop a modbus gateway",
    long_description = description,

    author = "fieldcloud SAS",
    author_email = "contact@fieldcloud.com",

    license = 'MIT',
    classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Information Technology',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url = "https://github.com/fieldcloud/ModbusService",

    keywords = ['iot', 'grove', 'internet of things', 'prototyping',
                'clouding things', 'fieldcloud'],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires = ['pymodbus', 'twisted']
)
