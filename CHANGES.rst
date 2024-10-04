
..
    Copyright (C) 2019-2024 CERN.
    Copyright (C) 2019-2024 Northwestern University.
    Copyright (C) 2024      KTH Royal Institute of Technology.


    Invenio-RDM-Records is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version v14.0.0 (released 2024-10-04)

- installation: bump invenio-vocabularies & invenio-communities

Version v13.0.0 (released 2024-10-03)

- collections: added feature, containing core functionalities and DB models
- ui: fixed propTypes warnings
- dependencies: bump flask-iiif to >1.0.0

Version v12.2.2 (released 2024-09-30)

- Improve handling of draft PID in RecordCommunitiesService
- Revert "deposit: check permission and set disable tooltip for publish button"
- Remove DeprecationWarning for sqlalchemy
- Add compatibility layer to move to flask>=3

Version v12.2.1 (released 2024-09-19)

- file upload: better handling of errors when uploading empty files
- serializers: ensure that the vocab id is set before performing a look up
- deposit: take into account the can_publish permission to control when the
           Publish button should be enabled or disabled

Version v12.1.1 (released 2024-09-11)

- resource: fix add record to community
- controls: refactored isDisabled function

Version v12.1.0 (released 2024-08-30)

- config: added links for thumbnails (#1799)

Version v12.0.4 (released 2024-08-28)

- stats: add missing "is_machine" field

Version v12.0.3 (released 2024-08-27)

- add permissions checks for community submission policy

Version v12.0.2 (released 2024-08-26)

- update file quota and size vars
- add quota config for media_files bucket

Version v12.0.1 (released 2024-08-22)

- bump invenio-vocabularies

Version v12.0.0 (released 2024-08-22)

- mappings: add analyzers and filters to improve results when searching records

Version v11.8.0 (released 2024-08-21)

- pids: fix parent DOI link generation
- schemaorg: add ``dateCreated`` field (closes #1777)
- i18n: push translations
- package: bump react-invenio-forms
- subjects: remove suggest from dropdown if not required
    * closes https://github.com/inveniosoftware/invenio-app-rdm/issues/2767

Version v11.7.0 (released 2024-08-12)

- resources: add vnd.inveniordm.v1+json http header
- translation: update file paths for strings (UI)

Version v11.6.0 (released 2024-08-07)

- creatibutors: fix buttons order
- permissions: change error handler for resolving pid permission denied
- record inclusion: use system identity to accept inclusion request when can_include_directly
- user_moderation: improve DB queries and use Celery tasks
- fix: use index to distinguish type of record in results
    * The problem with "is_published" is that drafts created from records will
      not be recognised correctly.
    * Using the index is a valid solution but it is not a nice implementation.
- results: added support for drafts in the results list
- fix(community): set branding
    * The set branding didn't work at all. It didn't work for rebranding if
      a default already exists and it didn't work if no branding exists at
      all.
    * The default property of the CommunitiesRelationManager needs a string.
      It can't handle a dict.

Version v11.5.0 (released 2024-07-22)

- codemeta: added identifier to schema
- signposting: generate 1 link context object for metadata
- fix: abort on record deletion exception

Version v11.4.0 (released 2024-07-15)

- affiliations: update defaults to ror v2

Version 11.3.1 (released 2024-07-12)

- processors: fix tiles files iteration
    * Creates a copy of the files list to be iterated since we might be
      modifying the underlying dictionary while processing tiles.

Version 11.3.0 (released 2024-07-12)

* media-files: generate ptif and include in manifets
* fix: pids required behavior
    * The fix for the parent doi configuration
      https://github.com/inveniosoftware/invenio-rdm-records/pull/1740 broke
      the "required" parameter for the pid provider. Previously you could
      have a pid provider that was active (shows up in the deposit form),
      but not required (pid would only be minted if something was entered).
      Because the check for "required" was removed, this stopped working.
    * This correction enables the option of having external DOIs without
      necessarily having to set one of them. This would not be possible with
      the "is_enabled" configuration.
* iiif: handle DecompressionBombError

Version 11.2.0 (released 2024-07-05)

- iiif: schema: only return images within size limit in manifest

Version 11.1.0 (released 2024-07-04)

- installation: upgrade invenio-drafts-resources

Version 11.0.0 (released 2024-06-04)

- installation: bump invenio-communities, invenio-vocabularies, invenio-drafts-resources and invenio-records-resources
- installation: added invenio-jobs

Version 10.7.1 (released 2024-05-31)

- secret links: set csrf token for all requests with secret links,
  i.e. fixes edit button CSRF error message on record landing page


Version 10.7.0 (released 2024-05-28)

- pids service: resolve owned_by for the emails
- entity_resolver: match drafts while resolving
- notifications: add user and guest notifications on request actions
- pids: unify pid behaviour, disable/enable parent DOI on demand, based on
  DATACITE_ENABLED configuration

Version 10.6.0 (released 2024-05-22)

- pids: prevent creating pids for restricted records
- pids: restrict updating permission levels for records based on a grace period

Version 10.5.0 (released 2024-05-21)

- iiif: add PyVIPS support for PDF thumbnail rendering

Version 10.4.3 (released 2024-05-17)

- services: fix permission for file edit

Version 10.4.2 (released 2024-05-08)

- iiif: resolve relative tiles storage against instance path

Version 10.4.1 (released 2024-05-07)

- grants: add new endpoint to grant access to records by groups

Version 10.4.0 (released 2024-05-07)

- config: add default values for IIIF tiles generation
- config: new variable for default IIIF manifest formats
- iiif: add pyramidal TIFF tiles generation on record publish via files processor
- iiif: harmonize configuration naming
- services: updated file schema
    - added "access" field to file schema
    - updated metadata field to be nested with a new schema
- services: fixed PDF image conversion bug
    - PDF thumbnails should now work again
- iiif: added fallback for iip server
- licenses: fix some delimiters not been recognized.

Version 10.3.2 (released 2024-04-30)

- iiif: fix proxy path generation

Version 10.3.1 (released 2024-04-25)

- resources: make IIIF proxy configurable via import string

Version 10.3.0 (released 2024-04-24)

- services: added nested links for record files

Version 10.2.0 (released 2024-04-23)

- iiif: added proxy to image server

Version 10.1.2 (released 2024-04-22)

- review: fix draft indexing operations order
    - Fixes a bug where when publishing directly to a community (e.g.
      beacause the uploader is a community admin/owner/curator), the draft
      would get deleted from the index and then get indexed again, thus
      appearing in the users' dashboard both as a published record and
      as a draft in review.

Version 10.1.1 (released 2024-04-19)

- pids: fix register/update serialization

Version 10.1.0 (released 2024-04-15)

- licenses: fix wrong characters encoding
- facets: integrate combined_subjects / fix nested subject faceting
- resources: fixed missing imports
- dublincore: fix license URL lookup

Version 10.0.0 (released 2024-04-11)

- Fixes datacite, dcat, dublin core, marcxml and schema.org serializer performance (reduced from ~500 queries in an OAI-PMH page down to 5).
- resources: fix performance of serializers
    - Rely on index data for licenses, subjects, communities, affiliations, and licenses instead of querying.
- datacite: fixed schema with unsafe access to parent
- datacite: fixed custom license links.
- serializer: add system updated date to DataCite
- csl: improve DOI (alternative identifier), ISBN, and ISSN
- csl: improve serialization performance
    - Remove funding information from CSL as it makes database queries and it is not relevant in the CSL JSON for generating citations.
- marcxml: removed service call for community slug
- marcxml: add license in 650
- marcxml: added references
- marcxml: updated award title in get_funding
- marcxml: added language
- marcxml: moved funding from 856 to 536
- marcxml: add contributor role
- marcxml: remove read_many call to vocab service
- records: add community.is_verified to mapping
- licenses: use sniffer to determine csv format
- licenses: bring urls up to date and use opensource and creativecommons as main urls with spdx as fallback
- licenses: change delimiter to comma
- assets: Add overridable tags (#1631)
- Added Swedish translation for vocabularies
- IIIF Presi: change viewingHint to individuals
- links: fix ESLint map expects a return value from arrow function
- vocab: add marc to roles.yaml

Version 9.1.0 (released 2024-04-04)

- api: added new endpoint to manage access restrictions of records
- deposit: improved communities sorting when uploading a new record
- serializers: marcxml: fixes to transformation rules

Version 9.0.1 (released 2024-03-25)

- serializers: DataCite to DCAT-AP - fix missing prov namespace for contributors project roles
- serializers: DataCite to DCAT-AP - include upstream editorial changes
- serializers: marcxml: Add leader to schema

Version 9.0.0 (released 2024-03-23)

- views: add signposting
- fixtures: added subject type creation on load
- contrib: change pages label and journal examples
- creatibutors: switch remove and edit button order
- serializers: add geolocation box and polygon to datacite
- serializers: fix longitude and latitude order to match geojson.
- resource-types: fix schema.org Thesis URL
- resource-types: publication-thesis = schema.org/Thesis
- resource-types: schema.org URL for Event
- ux: DOI prefix error message improvement
- init: move record_once to finalize_app

Version 8.3.0 (released 2024-03-06)

- services: introduced bulk_add permission
- requests: added community transfer request type
- services: added bulk addition to record community
- services: add metrics param interpreter

Version 8.2.0 (released 2024-03-05)

- bumps react-invenio-forms
- ui: center disabled new version popup tooltip
- fix: show popup tooltip on disabled new version button

Version 8.1.1 (released 2024-02-27)

- Revert "serializers: updated datacite schema rights."

Version 8.1.0 (released 2024-02-27)

- pids: allow empty-string PIDs
- config: safer parent PID conditional check
- serializers: updated datacite schema rights

Version 8.0.0 (released 2024-02-20)

- Bump due to major version upgrade in invenio-users-resources

Version 7.1.1 (released 2024-02-19)

- communities: add CommunityParentComponent

Version 7.1.0 (released 2024-02-19)

- mappings: change "dynamic" values to string
- requests: change default removal reason to spam
- mappings: add keyword field to ``funding.award.number``
- files: fixed infinite spinning wheel on error
- datacite: added config for funders id priority
- datacite: updated schema
- mapping: add community children

Version 7.0.0 (released 2024-02-16)

- services: update community components
- installation: bump invenio-communities
- mappings: denormalize communities in records
- systemfields: fix docstrings
- requests: add check on parent community on accept
- community selection: small ui fixes

Version 6.2.1 (released 2024-02-11)

- requests: add record to parent community

Version 6.2.0 (released 2024-02-09)

- tests: make deleted file fetching deterministic
- deposit: change upload workflow for styled communities
- deposit: indicate if community selection modal is used for initial submission
- deposit: add community.theme.enabled to selection modal
- installation: bump invenio-communities version

Version 6.1.1 (released 2024-02-05)

- oai: exclude deleted records from search
- models: add bucket_id index
- serializers: fix DataDownload missing mimetype

Version 6.1.0 (released 2024-02-01)

- Add CSV records serializer

Version 6.0.0 (released 2024-01-31)

- installation: bump dependencies
- installation: pin commonmeta-py

Version 5.1.1 (released 2024-01-30)

- Custom field ui: fix deserializing for primitive types

Version 5.1.0 (released 2024-01-29)

- pids: restore required PIDs on publish
- schema: add dataset specific fields to jsonld

Version 5.0.0 (2024-01-16)

- communities: utilize community theming mechanism

Version 4.43.2 (2024-01-16)

- dependencies: pin commonmeta-py

Version 4.43.1 (2023-12-12)

- replace ckeditor with tinymce

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
