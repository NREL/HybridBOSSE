#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Parangat Bhaskar",
    author_email='parangat.bhaskar94@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Tool for estimating BOS costs for hybrid power plants that share infrastructure",
    entry_points={
        'console_scripts': [
            'hybrids_shared_infrastructure=hybrids_shared_infrastructure.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='hybrids_shared_infrastructure',
    name='hybrids_shared_infrastructure',
    packages=find_packages(include=['hybrids_shared_infrastructure', 'hybrids_shared_infrastructure.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/parangat94/hybrids_shared_infrastructure',
    version='1',
    zip_safe=False,
)
