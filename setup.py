# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2022 CERN.
# Copyright (C) 2019-2022 Northwestern University.
# Copyright (C)      2022 TU Wien.
# Copyright (C)      2022 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""DataCite-based data model for Invenio."""

import os

from setuptools import find_packages, setup

readme = open('README.rst').read()
history = open('CHANGES.rst').read()

tests_require = [
    'invenio-app>=1.3.1,<2.0.0',
    'pytest-invenio>=1.4.2,<2.0.0',
    'pytest-mock>=1.6.0',
]

# Should follow inveniosoftware/invenio versions
invenio_db_version = '>=1.0.11,<2.0.0'
invenio_search_version = '>=1.4.0,<2.0.0'

extras_require = {
    'docs': [
        'Sphinx>=4.2.0',
    ],
    # Elasticsearch version
    'elasticsearch6': [
        'invenio-search[elasticsearch6]{}'.format(invenio_search_version),
    ],
    'elasticsearch7': [
        'invenio-search[elasticsearch7]{}'.format(invenio_search_version),
    ],
    # Databases
    'mysql': [
        'invenio-db[mysql,versioning]{}'.format(invenio_db_version),
    ],
    'postgresql': [
        'invenio-db[postgresql,versioning]{}'.format(invenio_db_version),
    ],
    'sqlite': [
        'invenio-db[versioning]{}'.format(invenio_db_version),
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
    'Babel>=2.8',
    'pytest-runner>=3.0.0,<5',
]

install_requires = [
    'arrow>=0.17.0',
    'citeproc-py-styles>=0.1.2',
    'citeproc-py>=0.6.0',
    'datacite>=1.1.1',
    'dcxml>=0.1.2',
    'Faker>=2.0.3',
    'ftfy>=4.4.3,<5.0.0',
    'invenio-communities>=2.8.0.dev0,<2.9.0',
    'invenio-drafts-resources>=0.16.0,<0.17.0',
    'invenio-oaiserver>=1.4.0',
    'invenio-vocabularies>=0.11.0,<0.12.0',
    'pytz>=2020.4',
    'pyyaml>=5.4.0',
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
        "invenio_base.api_blueprints": [
            'invenio_rdm_records = invenio_rdm_records.views:create_records_bp',
            'invenio_rdm_records_draft_files = invenio_rdm_records.views:create_draft_files_bp',
            'invenio_rdm_records_ext = invenio_rdm_records.views:blueprint',
            'invenio_rdm_records_parent_links = invenio_rdm_records.views:create_parent_record_links_bp',
            'invenio_rdm_records_record_files = invenio_rdm_records.views:create_record_files_bp',
            'invenio_vocabularies_affiliations = invenio_rdm_records.views:create_affiliations_blueprint_from_app',
            'invenio_vocabularies_names = invenio_rdm_records.views:create_names_blueprint_from_app',
            'invenio_vocabularies_subjects = invenio_rdm_records.views:create_subjects_blueprint_from_app',
        ],
        "invenio_base.blueprints": [
            'invenio_rdm_records_ext = invenio_rdm_records.views:blueprint',
        ],
        'invenio_celery.tasks': [
            'invenio_rdm_records_fixtures = invenio_rdm_records.fixtures.tasks',
            'invenio_rdm_records_services = invenio_rdm_records.services.tasks',
        ],
        'invenio_db.models': [
            'invenio_rdm_records = invenio_rdm_records.records.models',
            'affiliations = invenio_vocabularies.contrib.affiliations.models',
            'names = invenio_vocabularies.contrib.names.models',
            'subjects = invenio_vocabularies.contrib.subjects.models',
        ],
        'invenio_db.alembic': [
            'invenio_rdm_records = invenio_rdm_records:alembic',
        ],
        'invenio_jsonschemas.schemas': [
            'invenio_rdm_records = invenio_rdm_records.records.jsonschemas',
            'affiliations = invenio_vocabularies.contrib.affiliations.jsonschemas',
            'names = invenio_vocabularies.contrib.names.jsonschemas',
            'subjects = invenio_vocabularies.contrib.subjects.jsonschemas',
        ],
        'invenio_search.mappings': [
            'rdmrecords = invenio_rdm_records.records.mappings',
            'affiliations = invenio_vocabularies.contrib.affiliations.mappings',
            'names = invenio_vocabularies.contrib.names.mappings',
            'subjects = invenio_vocabularies.contrib.subjects.mappings',
        ],
        'invenio_i18n.translations': [
            'invenio_rdm_records = invenio_rdm_records',
        ],
        'invenio_requests.types': [
            'community_submission = invenio_rdm_records.requests:CommunitySubmission',
        ],
        'invenio_requests.entity_resolvers': [
            'records = invenio_rdm_records.requests.resolver:RDMRecordResolver',
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
    ],
)
