# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University, Galter Health Sciences Library & Learning Center.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'check-manifest>=0.25',
    'coverage>=4.0',
    'isort>=4.3.3',
    'pydocstyle>=2.0.0',
    'pytest-cov>=2.5.1',
    'pytest-pep8>=1.0.6',
    'pytest-invenio>=1.2.0',
    'pytest>=4.0.0,<5.0.0',
    'invenio_app>=1.2.3,<1.3.0'
]

invenio_search_version = '1.2.0'

extras_require = {
    'docs': [
        'Sphinx>=1.5.1',
    ],
    # Elasticsearch version
    'elasticsearch6': [
        'invenio-search[elasticsearch6]>={}'.format(invenio_search_version),
    ],
    'elasticsearch7': [
        'invenio-search[elasticsearch7]>={}'.format(invenio_search_version),
    ],
    # Databases
    'mysql': [
        'invenio-db[mysql,versioning]>=1.0.0',
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]>=1.0.0',
    ],
    'sqlite': [
        'invenio-db[versioning]>=1.0.0',
    ],
    'tests': tests_require,
}

extras_require['all'] = []
for name, reqs in extras_require.items():
    if name[0] == ':' or name in ('elasticsearch6', 'elasticsearch7',
                                  'mysql', 'postgresql', 'sqlite'):
        continue
    extras_require['all'].extend(reqs)

setup_requires = [
    'Babel>=1.3',
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    'arrow>=0.13.0',
    'Flask-BabelEx>=0.9.3',
    'invenio-jsonschemas>=1.0.0,<1.1.0',
    'invenio-records-rest>=1.5.0,<1.6.0',
    'invenio-records>=1.3.0,<1.4.0',
    'invenio-records-files>=1.1.1,<1.2.0',
    'invenio-records-permissions>=1.0.0a3',
    'marshmallow>=2.20.5,<3',
    'pycountry>=18.12.8',
    'Faker>=2.0.3'
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join('invenio_rdm_records', 'version.py'), 'rt') as fp:
    exec(fp.read(), g)
    version = g['__version__']

setup(
    name='invenio-rdm-records',
    version=version,
    description=__doc__,
    long_description=readme + '\n\n' + history,
    keywords='invenio data model',
    license='MIT',
    author='CERN',
    author_email='info@inveniosoftware.org',
    url='https://github.com/inveniosoftware/invenio-rdm-records',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    entry_points={
        'flask.commands': [
            'rdm-records = invenio_rdm_records.cli:rdm_records',
        ],
        'invenio_base.apps': [
            'invenio_rdm_records = invenio_rdm_records:InvenioRDMRecords',
        ],
        'invenio_base.api_apps': [
            'invenio_rdm_records = invenio_rdm_records:InvenioRDMRecords',
        ],
        'invenio_base.blueprints': [
            'invenio_rdm_records = invenio_rdm_records.views:blueprint',
        ],
        'invenio_config.module': [
            'invenio_rdm_records = invenio_rdm_records.config',
        ],
        'invenio_i18n.translations': [
            'messages = invenio_rdm_records',
        ],
        'invenio_jsonschemas.schemas': [
            'invenio_rdm_records = invenio_rdm_records.jsonschemas',
        ],
        'invenio_search.mappings': [
            'records = invenio_rdm_records.mappings',
        ],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 3 - Alpha',
    ],
)
