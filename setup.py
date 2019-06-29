#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''The setup script.'''
from setuptools import find_packages
from setuptools import setup

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'Click>=6.0',
    'attrs',
    'pyusb>=1.0a2',
    'python-statemachine',
    'usbq',
    'pygame',
]

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']

setup(
    author='Brad Dixon',
    author_email='brad.dixon@carvesystems.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description='Winners never cheat. Cheaters never win. Hackers sometimes cheat.',
    entry_points={
        'console_scripts': ['edope=edope.cli:main'],
        'usbq': ['edope=edope.usbq_plugin'],
    },
    install_requires=requirements,
    license='MIT license',
    long_description=readme,
    include_package_data=True,
    keywords='edope',
    name='edope',
    packages=find_packages(include=['edope']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/rbdixon/edope',
    version='0.1.0',
    zip_safe=False,
)
