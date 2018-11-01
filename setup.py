#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as req_file:
    requirements = req_file.read().split('\n')

with open('requirements-dev.txt') as req_file:
    requirements_dev = req_file.read().split('\n')

setup(
    name='robby',
    version='0.5.0',
    description="Robby",
    long_description=readme,
    author="Simon de Haan",
    author_email='simon@praekeltfoundation.org',
    url='https://github.com/smn/robby',
    packages=[
        'robby',
    ],
    package_dir={'robby':
                 'robby'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='robby',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points={
        'console_scripts': ['robby = robby.cli:main'],
    },
)
