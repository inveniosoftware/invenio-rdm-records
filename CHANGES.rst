
..
    Copyright (C) 2019-2023 CERN.
    Copyright (C) 2019 Northwestern University.


    Invenio-RDM-Records is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version 4.43.0 (2023-12-11)

- fixtures: method to add/update entries
- fixtures: add KTH affiliation
- chore: pycodestyle fix
- tests: added cff serializer test
- serializers: added yaml formatter
- serializers: added cff
- contrib: removed open terms from software fields
- codemeta: fixed funding serialization
- mappings: fix some mapping paths
- mapping: add a text subfield for award acronyms
- updated formatting
- export: sanitized file name in dcat schema
- export: santized filename in marcxml
- deposit-ui: improve error messages

Version 4.42.0 (2023-11-30)

- services: add signals component
- contrib: codemeta serializer

Version 4.41.0 (2023-11-29)

- metadata: use DateAndTime format for dates field
- contrib: update imprint labels to be more descriptive
- services: extend embargo check to all versions
- service: improve check for record existance
- generators: add community inclusion reviewers

Version 4.40.0 (2023-11-20)

- access: avoid setting ``access_request_token``
- resources: add parent doi redirection
- serializers: don't strip html for dc and marcxml
- config: update OAISERVER_RECORD_SETS_FETCHER
- deposit-ui: fix affiliations serialization

Version 4.39.3 (2023-11-13)

- secret-links: remove token from session on expiration

Version 4.39.2 (2023-11-07)

- resources: fix dcat serializer for restricted record files
- email templates: fix access request submit templates
- schemaorg: added fields to schema to improve fair score
- notifications: send community inclusion emails to community managers

Version 4.39.1 (2023-11-01)

- installation: remove upper pin for invenio-oauth2server
- draft: fix creatibutors affiliation de-duplication in select dropdown

Version 4.39.0 (2023-10-31)

- jsonschema: remove unique items constraints
- ui: deposit fields license Custom SearchBar
- fix: upload going blank on translation

Version 4.38.3 (2023-10-30)

- oaiserver: fix record loading for db results
- tests: add OAI endpoint tests

Version 4.38.2 (2023-10-27)

- datacite: fix related identifiers serialization.

Version 4.38.1 (2023-10-26)

- files: updating url  encoding
- entity: catch soft deleted draft
- schemaorg: serialize "creator"
- user access request e-mail: include requestor email address

Version 4.38.0 (2023-10-25)

- github: fix identity fetch for releases

Version 4.37.4 (2023-10-25)

- serializers: fix award serialization in marcxml
- assets: improve email templates formatting

Version 4.37.3 (2023-10-23)

- subjects: validate that values are unique
- github: added default repo creators
- service: fix draft access on deleted published record

Version 4.37.2 (2023-10-20)

- email: case-insensitive comparison of user email
- resources: make search request args class configurable
- service: make search option class configurable
- serializers: fix bibtex for github record-releases and requiring given_name field

Version 4.37.1 (2023-10-19)

- serializing: patch edtf date parser

Version 4.37.0 (2023-10-19)

- service config: change lock edit publish file
- installation: bump invenio-drafts-resources

Version 4.36.10 (2023-10-19)

- access: relax serialization checks

Version 4.36.9 (2023-10-18)

- github: added support for extra metadata.
- edit: fix serialization of creator roles
- deposit: fix required identifiers for creators
- serializers: fix wrongly used get

Version 4.36.8 (2023-10-17)

- github metadata: fix empty affiliations

Version 4.36.7 (2023-10-17)

- github: fixed authors serialization.

Version 4.36.6 (2023-10-16)

- reindex stats in batches of 10k

Version 4.36.5 (2023-10-16)

- allow users to delete pending files
- fix beforeunload event in upload form

Version 4.36.4 (2023-10-15)

- remove dependency in `flask_login.current_user` on service layer

Version 4.36.3 (2023-10-15)

- fix search of drafts

Version 4.36.2 (2023-10-14)

- datastore: prevent autoflush on search

Version 4.36.1 (2023-10-14)

- github: read releases by user identity permission

Version 4.36.0 (2023-10-13)

- service add version scan method

Version 4.35.0 (2023-10-13)

- datacite: hide DOI on delete record admin action
- datacite: show DOI on restore record admin action

Version 4.34.0 (2023-10-12)

- oai: add alias methods for backwards compatibility
- oai: marcxml: string encoding bug
- dependencies: upper pinned types requests.
- add schemaorg serializer
- oaiserver: add rebuild index method

Version 4.33.2 (2023-10-11)

- deposit form: improve UX of contributors modal
- tombstone: fix information removed by Admin

Version 4.33.1 (2023-10-10)

- service: fix restore/delete of specific record version

Version 4.33.0 (2023-10-09)

- journal: ui serializer formatting improvements
- serializers: ui - add publication date to journal citation
- github: store name and family name of author

Version 4.32.0 (2023-10-06)

- deposit form: report invalid value errors on each draft save
- access-requests: send notification on submit action
- access-requests: replace EmailOp with NotificationOp on guest access token create
- access-requests: replace EmailOp with NotificationOp

Version 4.31.1 (2023-10-04)

- deposit: make name's affiliation/id optionals

Version 4.31.0 (2023-10-04)

- files: add check for deleted record
- communities: add resource and service handlers for setting default community
- versions: add status param interpreter
- communities-records: set correct links

Version 4.30.0 (2023-10-03)

- add task to reindex records to update views/downloads stats

Version 4.29.0 (2023-10-03)

- serializers: replace slugs caching with invenio-cache
- assets: remove redundant recover on file upload fail
- notifications: add submission accept action notification
- ui: added autoFocus to Deposit Form modals

Version 4.28.2 (2023-09-28)

- serializers: fix cache ttl when fetching communities slugs

Version 4.28.1 (2023-09-28)

- serializers: use cache when fetching communities slugs
- service: fix config sort object being wrongly updated

Version 4.28.0 (2023-09-26)

- services: add community deletion component
- resources: fix response code on delete action
- resources: accept if_match header with revision id on DELETE

Version 4.27.0 (2023-09-22)

- services: added record components config support
- links: return parent_doi for both records and drafts

Version 4.26.0 (2023-09-21)

- deposit: add accessibility attributes
- resources: add etag headers
- search: query filter for deleted records on the main search endpoint
- services: add search params

Version 4.25.0 (2023-09-19)

- permissions: allow moderator to see all drafts
- services: filter out deleted records
- service: add quota load schema

Version 4.24.0 (2023-09-19)

- community submission: fix modal text for different cases
- resources: add administration and moderation actions
- models: avoid flushing when getting records

Version 4.23.2 (2023-09-17)

- config: fix ADS bibcode idutils scheme

Version 4.23.1 (2023-09-15)

- resources: remove response handler from submit review

Version 4.23.0 (2023-09-14)

- fixtures: update names and affiliations to use model PIDs

Version 4.22.0 (2023-09-14)

- service: set records and user quota
- deposit modals: fix modal headlines and list options styling for creatibutors

Version 4.21.0 (2023-09-13)

- service: prevent creating a request if invalid restrictions
- mappings: added award acronym to os-v1 and es-v7

Version 4.20.1 (2023-09-12)

- records: adds conditional dumping of files
- records: revert file dumper
- entity_resolvers: add missing ghost_record representation
- deposit: update headers for submit review action

Version 4.20.0 (2023-09-11)

- export formats: fix serializers
- links: add media files archive link
- moderation: delete user's records when blocking them
- serializers: added locations to UI serializer

Version 4.19.0 (2023-09-06)

- custom fields: update namespace values
- tokens: make RAT subject schema configurable
- services: handle no-value DOI for links
- deposit-ui: use "vnd.inveniordm.v1+json" always
- access: serialize "owned_by" field
- resources: add "x-bibtex" record serialization
- resources: make record serializers configurable
- schema: expose checksum and file ID
- services: make record/draft API classes configurable

Version 4.18.0 (2023-09-06)

- uow: use ParentRecordCommitOp when committing parent
- resolver: resolve records first when draft is published

Version 4.17.0 (2023-09-05)

- dumper: add files dumper ext
- services: add record deletion workflow
- alembic: fix record consent recipe

Version 4.16.1 (2023-09-04)

- stats: omit events from records without parent
- views: fix non existing avatar fetch in guest access request

Version 4.16.0 (2023-08-30)

- access request: record the consent to share personal data
- access request: ensure compliance of endpoints with the RFC
- access request: add load serialization schema
- oai-pmh: read oai sets prefix from app config

Version 4.15.1 (2023-08-25)

- access-field: rely on `instance.files.enabled` to indicate if files exist or not

Version 4.15.0 (2023-08-24)

- access request: add secret_link_expiration to guest access request payload schema
- permissions: add create/update conditions for managing access options
- views: add error handlers to the blueprint
- access request: add permission on secret_link_expiration request field


Version 4.14.0 (2023-08-17)

- alembic: add recipe for files and media files versioning
- permissions: fix permissions about whom can add a record to community
- service: lock record files conditionally
- search: added 'verified' field sort option
- records: added verified field to record
- permissions: extract base permissions
- deposit: set color of discard button
- github: remove python 3.7 from the tests
- records: add tombstone and deletion status
- access request: add secret link expiration access request setting
- deposit: fix license modal

Version 4.13.1 (2023-08-11)

- vocabularies: add new values to resource types

Version 4.13.0 (2023-08-09)

- alembic: fix wrong revision id
- access requests: new endpoint to update access request settings
- doi: fix exception logging
- tasks: discover missing celery task for access requests
- notifications: filter out creator when creating requests
- user moderation: add empty actions hooks
- ui: fix layout issues with community modals

Version 4.12.2 (2023-07-25)

- permissions: fix permission syntax error

Version 4.12.1 (2023-07-25)

- permissions: fix external doi versioning generator

Version 4.12.0 (2023-07-24)

- access: allow dump of parent.access.settings field
- github: fix metadata validation issues
- github: add badges support
- records: add parent access settings schema

Version 4.11.0 (2023-07-21)

- add parent doi resolution

Version 4.10.0 (2023-07-18)

- access-requests: change expires_at to isodatestring
- ui: align commmunity header logo with other community headers
- github: add invenio github integration

Version 4.9.1 (2023-07-17)

- available actions: reorder actions

Version 4.9.0 (2023-07-13)

- add access requests for users and guests

Version 4.8.0 (2023-07-12)

- add media files

Version 4.7.0 (2023-07-05)

- transifex: update config
- conf: add variable to enable files by default

Version 4.6.0 (2023-07-03)

- implement resource access (RAT) tokens
- ui: fix deposit form access value when submitting to restricted community

Version 4.5.0 (2023-06-30)

- fix custom fields issue with nested array in an object
- use reindex_users method

Version 4.4.1 (released 2023-06-28)

- Fixes permission checks when there is no record object to check i.e new record

Version 4.4.0 (released 2023-06-15)

- access: fix permissions check for managing access
- schemas: remove redundant permission check
- setup: upgrade invenio-communities

Version 4.3.0 (released 2023-06-07)

- add notification on community submission / community review request
- add notification templates

Version 4.2.5 (released 2023-06-05)

- custom-fields: fix deserialization for array of string values

Version 4.2.4 (released 2023-06-02)

- results: implement abstract method for system record

Version 4.2.3 (released 2023-05-31)

- resource-types: more fixes on types/subtypes

Version 4.2.2 (released 2023-05-30)

- export all file-uploader components
- resource types: fix wrongly mapped ids

Version 4.2.1 (released 2023-05-27)

- fix on resource types vocabularies

Version 4.2.0 (released 2023-05-26)

- update resource types vocabularies
- add permission flag system field
- change the mapping of files entries from integer to long
- add dumpers for imprint and meeting in csl
- add missing dumper to citation serializer
- improve a11y for community modals

Version 4.1.0 (released 2023-05-05)

- add reference fields to deposit components
- fix records and drafts mappings
- fix custom field components exports

Version 4.0.0 (released 2023-04-25)

- record: add file metadata to the indexing
- fixtures: add user locale preferences

Version 3.1.0 (released 2023-04-21)

- assets: move react deposit components

Version 3.0.0 (released 2023-04-20)

- usage statistics: refactor files structure

Version 2.13.0 (released 2023-04-17)

- serializers: added schema processors (custom fields)
- serializers: created dump and load mixins for custom fields

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
