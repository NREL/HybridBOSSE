#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# requirements = ['Click>=7.0', ]

# setup_requirements = ['pytest-runner', ]

# test_requirements = ['pytest>=3', ]

setup(
    author="Parangat Bhaskar",
    author_email='parangat.bhaskar94@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Tool for estimating BOS costs for hybrid power plants that share a physical infrastructure",
    # entry_points={
    #     'console_scripts': [
    #         'hybrids_shared_infrastructure=hybrids_shared_infrastructure.cli:main',
    #     ],
    # },
    # install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    # include_package_data=True,
    keywords='HybridBOSSE',
    name='hybridbosse',
    install_requires=[
        'pandas==1.0.3',
        'numpy==1.17.2',
        'sympy==1.4',
        'scipy==1.3.1',
        'xlsxwriter==1.2.1',
        'xlrd==1.2.0',
        'pytest==5.3.5'
        'PyYaml==5.1.2'
    ],
    packages=['hybridbosse', 'hybridbosse.hybrids_shared_infrastructure',
              'hybridbosse.LandBOSSE', 'hybridbosse.LandBOSSE.landbosse.model',
              'hybridbosse.LandBOSSE.landbosse.excelio', 'hybridbosse.LandBOSSE.landbosse.tests',
              'hybridbosse.LandBOSSE.landbosse.landbosse_api', 'hybridbosse.SolarBOSSE',
              'hybridbosse.SolarBOSSE.excelio', 'hybridbosse.SolarBOSSE.model',
              'hybridbosse.SolarBOSSE.project_data', 'hybridbosse.hybridbosse_api'],

    # packages=find_packages(include=['hybrids_shared_infrastructure', 'hybrids_shared_infrastructure.*',
    #                                 'SolarBOSSE', 'SolarBOSSE.*', 'LandBOSSE', 'LandBOSSE.*', 'hybridbosse_api',
    #                                 'hybridbosse_api.*']),

    # setup_requires=setup_requirements,
    # test_suite='tests',
    # tests_require=test_requirements,
    url='https://github.com/parangat94/hybridbosse',
    version='0.9.7',
    # zip_safe=False,
)
