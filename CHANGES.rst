..
    Copyright (C) 2019-2023 CERN.
    Copyright (C) 2019 Northwestern University.


    Invenio-RDM-Records is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version 2.12.0 (released 2023-04-06)

- api: add record community suggestion endpoint

Version 2.11.0 (released 2023-03-30)

- add usage statistics indexing (by system field)
- add sorting by most viewed to the config
- move statistics events from invenio-app-rdm

Version 2.10.0 (released 2023-03-28)

- add requests endpoint to the record
- dublincore: transform identifiers tu urls
- record service: update community records

Version 2.9.0 (released 2023-03-24)

- communities: return ghost parent community when cannot be resolved
- contrib: add journal and meeting sort options
- contrib: updated custom fields UI widgets
- custom_fields: rename CodeMeta to Software

Version 2.8.0 (released 2023-03-20)

- fix marcxml format incompatibility
- add DCAT-AP export format serializer
- add record access configuration flag
- normalize commmunity config variable names
- configure community service error handlers

Version 2.7.0 (released 2023-03-13)

- record: implement multiple communities inclusion via new request type
- communities: allow overwriting access component
- serializers: refactor accessing fields in the schema

Version 2.6.0 (released 2023-03-09)

- review service: expand links
- review service: validate request type


Version 2.5.0 (released 2023-03-09)

- serializer: add bibtex
- serializer: rename coverage to locations in dublincore schema
- contrib custom fields: index titles both as text and keyword

Version 2.4.0 (released 2023-03-06)

- contrib custom fields: add journal, meeting
- configure metadata only records by feature flag and permissions

Version 2.3.0 (released 2023-03-03)

- records: remove from community
- oai-sets admin: frontend fixes
- contrib: add code meta as custom fields
- serializers: support search export in different formats
- serializers: refactoring to provide better abstraction
- remove deprecated flask_babelex dependency and imports

Version 2.2.0 (released 2023-02-20)

- records: remove communities from a record
- communities: support both slug (id) and uuid in communities endpoints
- communities: support direct publish (without review)
- fixtures: fix duplicated user creation

Version 2.1.0 (released 2023-02-14)

- export: add MARCXML serializer, including in OAI-PMH
- resources: add stubs for records' communities

Version 2.0.0 (released 2023-02-07)

- export: add GEOJSON serializer

Version 1.3.3 (released 2023-02-06)

- datacite: fix reversion in affiliation ROR handling and cleanup

Version 1.3.2 (released 2023-01-30)

- records: remove double permission check on community records search

Version 1.3.1 (released 2023-01-23)

- Add feature flag for archive download endpoint on record and draft resources

Version 1.3.0 (released 2023-01-20)

- add mechanism to validate a record based on each PID provider
- fix demo records creation adding missing search index prefix on index refresh
- Fix response status when searching for records of a non-existing community
- remove validation on DOI discard action
- skips PIDs modification when no data is passed

Version 1.2.1 (released 2022-12-01)

- Add identity to links template expand method.

Version 1.2.0 (released 2022-11-29)

- add records fixtures

Version 1.1.0 (released 2022-11-25)

- use communities v4
- use Axios centralized configuration
- add i18n translations
- refactor OAI sets view

Version 1.0.3 (released 2022-11-16)

- add draft indexer in registry

Version 1.0.2 (released 2022-11-15)

- fix service_id config values
- sanitize html in additional descriptions instead of stripping html

Version 1.0.1 (released 2022-11-04)

- upgrade invenio-vocabularies
- upgrade invenio-drafts-resources
- add dynamic formats to administration of oai sets
- add RO-Crate serializer

Version 1.0.0

- Initial public release.
