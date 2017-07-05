#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='api_gateway',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'arrow==0.10.0',
        'boto3==1.4.4',
        'click==6.7',
        'Flask==0.12.2',
        'Flask-Cors==3.0.2',
        'Flask-RESTful==0.3.6',
        'Flask-SQLAlchemy==2.2',
        'gunicorn==19.7.1',
        'marshmallow==2.13.5',
        'netaddr==0.7.19',
        'psycopg2==2.7.1',
        'restful_ben==0.0.1',
        'requests==2.17.3',
        'SQLAlchemy==1.1.10'
    ],
    dependency_links=[
        'https://github.com/CityOfPhiladelphia/restful-ben/tarball/master#egg=restful_ben-0.0.1'
    ],
    entry_points={
        'console_scripts': [
            'api_gateway=api_gateway.cli:main',
        ],
    }
)
