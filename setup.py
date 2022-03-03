# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.md') as f:
    project_readme = f.read()

with open('LICENSE') as f:
    project_license = f.read()

setup(
    name='infopave-analyzer',
    version='0.1.0',
    description='LTPP InfoPave data analyzer',
    long_description=project_readme,
    author='Carlos González Marco',
    author_email='cargonm6@teleco.upv.es',
    url='https://github.com/cargonm6/infopave-analyzer',
    license=project_license,
    packages=find_packages(exclude=('tests', 'docs'))
)
