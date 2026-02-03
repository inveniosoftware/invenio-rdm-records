
..
    Copyright (C) 2019-2025 CERN.
    Copyright (C) 2019-2024 Northwestern University.
    Copyright (C) 2024      KTH Royal Institute of Technology.
    Copyright (C) 2024-2026 Graz University of Technology.

    Invenio-RDM-Records is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version v24.0.0 (released 2026-02-03)

- chore(setup): bump dependencies
- refactor(Link): take into account upstream changes
- chore(black): update formatting to >= 26.0
- refactor: replace deprecated Link usage
- revert: part of utcnow fix
- fix: SyntaxWarning: "\d" is invalid
- fix: ChangedInMarshmallow4Warning
- fix: FutureWarning
- fix:  PytestCollectionWarning
- fix(Warning): Received  for a non-boolean attribute .
- fix(js): react warnings
- fix(chore): RemovedInMarshmallow4Warning
- fix(chore): DeprecationWarning stdlib
- fix(chore): LegacyAPIWarning sqlalchemy
- fix(chore): DeprecationWarning stdlib
- fix:  DeprecationWarning
- refactor: remove max_number form context
- refactor: remove usage of is_parent context
- refactor(schema): remove usage of object_key
- fix(access_requests_ui): Fix view for guest when receiver isnt community

Version 23.2.2 (release 2026-01-27)

- fix(deposit): prevent Enter key from removing array field rows


Version 23.2.1 (release 2026-01-22)

- fix(permissions): allow system user to manage files
- fix(request_policies): allow system user to modify files
- chore: black formatting python3.9 compatability
- fix(files): fix for pending files with long names
- fix(deposit): rename conflicting prop func


Version v23.2.0 (released 2026-01-16)

- fix(requests): inherit from BaseRequest to fix self_html links
- fix(tests): update wikidata identifier
- fix: The character 'U+fe0f' is invisible.
- Add Arabic translations for resource types
- fix(schema): take the list of allowed tags and attrs from the app config

Version v23.1.1 (released 2026-01-08)

- bibtex: schema: add publication-thesis for compatibility

Version v23.1.0 (released 2026-01-07)

- fix(tests): use valid WikiData IDs and Geonames in fixtures
- feat(config): validate WikiData IDs for locations
- feat: add wikidata identifier to known identifier schemes
- serializers: use datapackage mediatype
    Express file MIMEType as mediatype, cf. Data Resource specification, see
    https://datapackage.org/standard/data-resource/#mediatype
- fix(tests): make logic to restore last revision more robust
    * the `invenio_records.api.RevisionsIterator` definition mentions that
      the list of revision IDs may have "holes" in it:
      https://github.com/inveniosoftware/invenio-records/blob/master/invenio_records/api.py

Version v23.0.0 (released 2025-12-12)

- chore(setup): bump major versions
- feat(permissions): add reply_comment permission

Version v22.7.0 (released 2025-12-08)

- fix(access_requests_ui): Fix permissions for commenting with guest token when request is locked
- fix(permissions): Fix can_create_comment to use parent attibute

Version v22.6.0 (released 2025-11-21)

- fix(requests): don't hard-code /me for record review request
- refactor(requests): move _update_link_config to new BaseRequest

Version v22.5.0 (released 2025-11-20)

- feat(file-modification): allow admins to unlock files for editing by default
- feat(file-modification): allows to configure conditions for users to edit files of published records

Version v22.4.0 (released 2025-11-12)

- setup: bump `invenio-github` major version

Version v22.3.0 (released 2025-11-05)

- feat(serializers.datacite): Add DataCite schema version 4.5 support
- fix(services): Make 'notes' parameter optional in _update_quota

Version v22.2.0 (released 2025-11-04)

- feat(secret-links): make expiration date optional or required for secret links
- feat(community-records): adds service component calls to RecordCommunitiesService

Version v22.1.0 (released 2025-10-27)

- feat(form): add support for help text to creatibutors button in the deposit form

Version v22.0.1 (released 2025-10-27)

- fix(contrib): meeting field ID allowed schemas source
- fix(deposit): duplicate uploads from resetting progress

Version v22.0.0 (released 2025-10-21)

- feat(resource_types)!: Remove publication-thesis
    * BREAKING CHANGE: resource_type with id publication-dissertation will now be used instead as it is correctly mapped to the "Dissertation" type in DataCite

Version v21.3.0 (released 2025-10-20)

- fix(deposit-ui): disable drag-n-drop files when files are locked
- fix(deposit-ui): re-add code removed in 9e8f553
- feat(schema): added related_identifiers variable
- fix(setup): temporarily tighten commonmeta-py pin
    * this avoids getting a version of the dependency with breaking changes
- fix(oai-pmh): handle broader permission denied errors
    * previously, the `GetRecord` verb targeting a restricted record would
      result in a HTTP 500 response due to an unhandled error
    * the `getrecord_fetcher()` function only handled
      `PermissionDeniedError` exceptions but not
      `RecordPermissionDeniedError`, which are the ones raised by services
    * since both of them are subclasses of `PermissionDenied`, we simply
      handle that instead

Version v21.2.0 (released 2025-10-01)

- feat(config): add last activity sort option

Version v21.1.0 (released 2025-09-24)

- installation: upgrade invenio-jobs

Version v21.0.0 (released 2025-09-24)

- installation: bump invenio-communities and invenio-checks
- feat(deletion-request): different checklist for immediate and request
- feat(record-deletion): add notifications
- fix(record-deletion): tombstone should have accepter's ID
- feat(deletion-request): add tags for valid removal reasons
- feat(schema): allow `removed_by` to be passed to tombstone schema
    * Allows loading the field in the schema.
    * If not passed, defaults to the `identity.id` of the deletion action.
- feat(schema): add `deletion_policy` to record tombstone
- feat: add support to request deletion of a record
- chore(js-tests): upgrade react-overridable major version
- fix(CreatibutorsModal): get identifier scheme from recent suggestions
- fix(datacite test link): update Datacite test DOI link
- fix: invalid datacite test mode link

Version v20.2.0 (released 2025-09-16)

- **feat(deposit-form)!: added `react-overridable` support more consistently across all deposit form fields**
    - Added Overridable for many components that did not already have it. This was done following the existing naming convention. New Overridables do not represent any breaking or behavior changes.
    - Renamed a number of existing Overridable IDs for better compliance with existing naming conventions. This is the full list:
        - `ReactInvenioDeposit.FileUploader.layout` -> `InvenioRdmRecords.DepositForm.FileUploader.Container`
        - `ReactInvenioDeposit.FileUploader.ImportButton.container` -> `InvenioRdmRecords.DepositForm.FileUploader.ImportButton`
        - `ReactInvenioDeposit.FileUploader.FileUploaderArea.container` -> `InvenioRdmRecords.DepositForm.FileUploader.UploadArea`
        - `ReactInvenioDeposit.FileUploader.NewVersionButton.container` -> `InvenioRdmRecords.DepositForm.FileUploader.NewVersionButton`
        - `ReactInvenioDeposit.FileUploader.Modal.container` -> `InvenioRdmRecords.DepositForm.FileUploader.Modal`
        - `ReactInvenioDeposit.FileUploaderToolbar.layout` -> `InvenioRdmRecords.DepositForm.FileUploaderToolbar.Container`
        - `ReactInvenioDeposit.FileUploaderToolbar.MetadataOnlyToggle.container` -> `InvenioRdmRecords.DepositForm.FileUploaderToolbar.MetadataOnlyToggle`
        - `InvenioRDMRecords.CreatibutorsModal.RoleSelectField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.RoleSelectField`
        - `InvenioRDMRecords.CreatibutorsModal.PersonRemoteSelectField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.PersonRemoteSelectField`
        - `InvenioRDMRecords.CreatibutorsModal.FullNameField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.FullNameField`
        - `InvenioRDMRecords.CreatibutorsModal.PersonIdentifiersField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.PersonIdentifiersField`
        - `InvenioRDMRecords.CreatibutorsModal.PersonAffiliationsField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.PersonAffiliationsField`
        - `InvenioRDMRecords.CreatibutorsModal.OrganizationRemoteSelectField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.OrganizationRemoteSelectField`
        - `InvenioRDMRecords.CreatibutorsModal.OrganizationNameField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.OrganizationNameField`
        - `InvenioRDMRecords.CreatibutorsModal.OrganizationIdentifiersField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.OrganizationIdentifiersField`
        - `InvenioRDMRecords.CreatibutorsModal.OrganizationAffiliationsField.container` -> `InvenioRdmRecords.DepositForm.CreatibutorsModal.OrganizationAffiliationsField`
        - `InvenioRdmRecords.DatesField.AddDateArrayField.Container` -> `InvenioRdmRecords.DepositForm.DatesField.Container`
        - `InvenioRdmRecords.DatesField.DescriptionTextField.Container` -> `InvenioRdmRecords.DepositForm.DatesField.DescriptionField`
        - `InvenioRdmRecords.DatesField.DateTextField.Container` -> `InvenioRdmRecords.DepositForm.DatesField.DateField`
        - `InvenioRdmRecords.DatesField.TypeSelectField.Container` -> `InvenioRdmRecords.DepositForm.DatesField.TypeField`
        - `InvenioRdmRecords.DatesField.RemoveFormField.Container` -> `InvenioRdmRecords.DepositForm.DatesField.RemoveButton`
    - No existing overridables have been removed completely to avoid breaking current implementations in an unresolvable way.

Version v20.1.0 (released 2025-09-05)

- setup: bump major versions of invenio-jobs and invenio-vocabularies
- fix: improve rendering of ErrorMessage in deposit form

Version v20.0.3 (released 2025-09-03)

- fix(deposit-form): correct wrong propType for optionalDOItransitions
- fix(deposit-form): on delete draft discard all changed pids
    * discard all draft pids if there is no published record (i.e. new version or new draft)
    * discard all draft pids that are not in the published record

Version v20.0.2 (released 2025-09-01)

- fix(optional-doi): show correctly showed value on form initialization
    * uses published record doi to check if the managed DOI can be unreserved.
    * `shouldCheckForExplicitDOIReservation` condition is evaluated against pids.doi because
      before it was taking into account only the pids object and there more pids could be present e.g. oai
- fix(iiif): add error handler for `MultimediaImageNotFound`

Version v20.0.1 (released 2025-08-27)

- fix: use config variable instead of redefining
- services: create RDMCommunityRecordSearchOptions
- deposit-form: add fallback message if checksum is not yet available
    * this is relevant for the multipart file upload with local file
      storage, where the checksum gets calculated in a background task after
      finalizing the upload
- fix(schemaorg): chase award schema relaxation from Invenio-Vocabularies
- fix(oaipmh): properly change output format
    * `URLSearchParams` does not parse URLs,
      https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams#no_url_parsing,
      preventing the `metadataPrefix` from changing when a new value is
      selected on the dropdown.
- UI: use X for discard instead of trash icon
- UI: add icon to delete button

Version v20.0.0 (released 2025-08-01)

- feat: implement request reviewers functionality
  - Add RequestReviewers generator with configuration support
  - Refactor request.reviewer to request.reviewers for consistency
  - Remove deprecated approve action
  - Add comprehensive tests for reviewer assignment
  - Include configuration validation for reviewer settings
- setup: bump major versions of invenio-communities and invenio-checks
  - needed to isolate the new request reviewers functionality

Version v19.5.3 (released 2025-07-31)

- optional-DOI: validation workflow improvements
  - fixes issue where optional DOI validation was not properly handled during the submit for review process
  - adds proper optional DOI validation when submitting records for review
- components: adds informative error message when attempting to create duplicate review requests

Version v19.5.2 (released 2025-07-30)

- fix(serializers): Strip none and trailing whitespace for thesis

Version v19.5.1 (released 2025-07-21)

- fix: cross-origin-file-uploads

Version v19.5.0 (released 2025-07-17)

- meeting cf: fix typo in the mapping
- i18n: pulled translations
- serializers: bibtex: Prefix all_version with doi
- tests: serializers: Add test for bibtex all versions
- serializers: bibtex: Add all versions export support

Version v19.4.2 (released 2025-07-16)

- PublishButton: Separate PublishModal and add checkbox easily via params
- assets: PublishModal: Ensure unique fieldPath and id for checkboxes
- Fix: installation failed due to type error

Version v19.4.1 (released 2025-07-14)

- doi: handle case with no configured parent dois

Version v19.4.0 (released 2025-07-10)

- chores: replacing importlib_metadata with importlib.metadata
- i18n: run js extract msgs
- i18n: replace Trans for EmbargoAccess
- i18n: replace Trans with i18next.t in VersionField
- i18n: replace Trans with i18next.t in DeleteModal
- i18n: replace Trans in access msgs
- i18n: fix warning msg not showing
- i18n: cs vocabulary translations (#2093)
- i18n:push translations
- i18n: run js compile catalog
- i18n: run js extract msgs
- i18n: refactor compile catalog
- i18n: force pull py and js translations
- i18n: extract python msgs
- fix: conflicting s3 part size for 1M-5M files
- ext: Add deprecation warning for publishModalExtraContent
- assets: PublishButton: Rename overridable containers
- assets: PublishButton: Make submit and publish utility overridable
- deposit: change creatributor and license item button order
- tests: have fixture test ignore load order
- resource: fix remove last community error
- fix: added overridable blocks and passing serializing functions as props

Version v19.3.0 (released 2025-07-02)

- fix: disabled remote and fetch transport in permissions
- fix: RemovedInMarshmallow4Warning
- fix: ChangedInMarshmallow4Warning
- contrib: specify proceedings in imprint title label
- fix: pkg_resources DeprecationWarning
- tests: add tests for setting record/user quotas
- quotas: set the record's file quota in a service component
- quotas: add extra info about the user_id column in record quotas
- quotas: remove unique constraint for the user_id in record quotas
- deposit-ui: implement uppy uploader field
- oaiserver/services: simplify search filtering
- fix: SADeprecationWarning
- i18n: localize embargoed date
- records-api: add Data Package serializer

Version v19.2.0 (released 2025-06-13)

- checks: integrate service component and community requests

Version v19.1.0 (released 2025-06-12)

- form: display errors on draft load
- deposit: updated fieldpath for feedback label
- serializers/datacite: configurable dumping of access right (#2047)
    * serializers/datacite: configurable dumping of access right
    * Adds a new `RDM_DATACITE_DUMP_ACCESS_RIGHTS` config variable to
      control if the access right level is included in the DataCite
      serialization. The value is based on the vocabulary documented at
      <https://wiki.surfnet.nl/spaces/standards/pages/11055603/info-eu-repo#infoeurepo-AccessRights>
    * confix: rename to `RDM_DATACITE_DUMP_OPENAIRE_ACCESS_RIGHTS`
- licenses: add creative commons public domain mark from spdx
- serializers: add publication-section rdm type (book section) to bibtex serialization
- localizing dates based on application selected locale
- contrib-meeting: add missing `url` field to deposit form

Version v19.0.1 (released 2025-06-10)

- file uploader: change from checkbox to radio
- file uploader: improve exceeded limit message
- tests: update error to reflect records-resources file permission order change
- creatibutors: adapt to new feedback label interface
- creatibutors: fix nested errors & feedback display

Version v19.0.0 (released 2025-06-03)

- setup: version bump on dependent packages
- fix: added permissions for getting/setting transfer metadata
  * Added extra permissions to get/update transfer metadata. These permissions
  are not used by REST API, they are used in background tasks, at this
  moment for fetch transfer (not enabled by default and not supported in UI)
- test: fixed test - file key is now required
- permissions: multipart upload with local fs storage
- Implementation of RFC 0072 - Pluggable transfer types
  * IfFileIsLocal is not used anymore as it was handling just one type of transport
  * Switched to IfTransferType permission generators
- installation: remove collections dependency

Version v18.14.0 (released 2025-06-02)

- config: make community request type classes customizable
    * Allows to customize community submissions and inclusion request type
      classes via the ``RDM_COMMUNITY_SUBMISSION_REQUEST_CLS`` and
      ``RDM_COMMUNITY_INCLUSION_REQUEST_CLS`` config variables.

Version v18.13.0 (released 2025-06-02)

- Move collections implementaiton to Invenio-Collections

Version v18.12.0 (released 2025-05-23)

- resources: expose get current revision of record
- deposit: fix global server errors in frontend
- feedback-ui: Add specific ID to disconnected feedback form

Version v18.11.0 (released 2025-05-16)

- deposit-ui: fix upload files error state
- deposit-ui: add feedback messages on the file level

Version v18.10.0 (released 2025-05-13)

- review: add components hook for submitting review
- deposit: show global backend validation message

Version v18.9.0 (released 2025-05-13)

- mappings: remove objectfields from "index.query.default_field" settings
- update setup.cfg

Version v18.8.1 (released 2025-05-07)

- schemas: provide default value for quota increase notes
- metadata: copyrights placeholder and help text changes
- ui serializer: display more thesis information

Version v18.8.0 (released 2025-05-06)

- services: make commit file link dependent on allow_upload
- meeting: add identifiers to data model of meeting contrib field
- services: include Opensearch meta in the results


Version v18.7.0 (released 2025-04-28)

- logging: add basic logging for expired embargoes

Version v18.6.1 (released 2025-04-28)

- services: remove commit file link from record (bugfix)

Version v18.6.0 (released 2025-04-24)

- datamodel contrib: add defense and submission date to thesis field

Version v18.5.0 (released 2025-04-24)

- datamodel: add copyright field

Version v18.4.0 (released 2025-04-23)

- urls: integrate invenio_url_for
- permissions: replace Disabled with SystemProcess

Version v18.3.2 (released 2025-04-17)

- custom_fields: added fallback to old thesis format and conditionally handle form display based on config

Version v18.3.1 (released 2025-04-14)

- user quota: anticipate system user
- doi: increase label width

Version v18.3.0 (released 2025-04-10)

- pids: change optional DOI validation
- views: FAIR signposting level 1 support (remove comment)
- views: signposting: fix fallback to level 2 linkset if collections size is too big to control link header size
- owner: allow system_user to be record owner


Version v18.2.0 (released 2025-04-03)

- fix: deletion_status gone after record.commit
- fix: tombstone gone after record.commit
- file_links: prepare for changes in invenio-records-resources
- deposit-ui: show icon and tooltip for new error format with severity error

Version v18.1.0 (released 2025-03-27)

- align licenses modal with funders modal
- use underscores for setuptools configuration instead of dashes
- lots of translations

Version v18.0.0 (released 2025-03-26)

deposit-ui: creatibutors: support general new error format with severity (fix null)
deposit-ui: creatibutors: support general new error format with severity
deposit-ui: fix: do not consider new error format's description as a field
thesis: add department and type (breaking change)
imprint: add edition

Version v17.4.0 (released 2025-03-18)

- deposit-ui: Support new error format with severity and description
  - FeedbackLabel for creatibutors and license

Version v17.3.0 (released 2025-03-11)

- resources: add param to filter shared with my uploads
  - returns record needs on entity resolution
  - reindex associated request on parent access changes
- service: change community submission actions on who can manage
- links: add preview_html link

Version v17.2.0 (released 2025-03-10)

- views: signposting: files: fix filename encoding issues for downloads
- resource_types: fix datapaper and interactiveresource datacite mapping
- schema.org: add uploadDate for VideoObject serialization [+]
- cff: add default "message" field
- iiif: fix info request not being proxied

Version v17.1.0 (released 2025-02-21)

- views: FAIR signposting level 1 support
- views: FAIR signposting remove linkset link to itself

Version v17.0.2 (released 2025-02-14)

- serializers/dcat: fix broken subject serialization for terms with apostrophes

Version v17.0.1 (released 2025-02-13)

- Bump pre-release dependencies to stable.

Version v17.0.0 (released 2025-02-13)

- Promote to stable release.
- serializers: DataCite to DCAT-AP: fix undefined variable $cheme for relation type has metadata
- services: proper escape the fields key in links generation
- UISerializer: add polygon locations to serializer in addition to points (#1924)

Version v17.0.0.dev2 (released 2025-01-23)

Version v17.0.0.dev1 (released 2024-12-16)

- fix: flask-sqlalchemy.pagination >= 3.0.0
- comp: make compatible to flask-sqlalchemy>=3.1
- setup: change to reusable workflows
- setup: bump major dependencies

Version v16.8.0 (released 2025-01-27)

- resources: expose record revisions

Version v16.7.1 (released 2025-01-21)

- optional-doi: fix new upload disabled states

Version v16.7.0 (released 2025-01-21)

- pids: improve deposit UI for optional DOI
- deposit-ui: fix affiliation selection input display

Version v16.6.1 (released 2025-01-16)

- Revert "bug: add custom comment notification for record/draft requests"
    * This is actually a breaking change since it introduces a new
      set of notification templates that will potentialy not be
      styled if overridden in an instance's overlay.

Version v16.6.0 (released 2025-01-16)

- notifications: add custom comment template for record inclusion
  and draft review requests
- deposit-ui: fix affiliations dropdown behavior for custom values
- moderation: fix use of uow
- serializers/bibtex: Conference paper not falling back to proceedings
- serializers/bibtex: Conference proceeding to proceedings
- serializers/bibtex: year and month using publication date
- rights: fix serialize condition for controlled license

Version v16.5.1 (released 2024-12-16)

- pids: add manage permission to be able to manage DOIs
- deposit: fix validation check when user needs a DOI and DOI is optional

Version v16.5.0 (released 2024-12-16)

- pids: add support for optional DOI

Version v16.4.1 (released 2024-12-11)

- mappings: add missing `identifiers` to community orgs
    * Adds the missing `identifiers` mapping field to community organizations

Version v16.4.0 (released 2024-12-10)

- bibtex: add trailing comma in url field
- community-records: allow scan search
    * Adds `scan` and `scan_params` arguments to
      `CommunityRecordsService.search(...)`, to allow for serving scan
      results (but only via the service).
- serializer: updated subjects and affiliations in dcat
- schema: added identifiers to subjects
- serializers: add datapackage serializer (#1742)

Version v16.3.4 (released 2024-12-06)

- github: return None for `NOASSERTION` license
- datacite: fix funding serialization for optional award fields
    * Makes sure that we handle missing values for optional award fields
      like "title" and "number".

Version v16.3.3 (released 2024-12-04)

- github: handle missing repo license

Version v16.3.2 (released 2024-12-04)

- github: lower license spdx id

Version v16.3.1 (released 2024-12-02)

- deposit-ui: make sure we handle null/undefined for SchemaField
- deposit-ui: skip unecessary removal of empty values in serialization
    * This initial removal of empty values can be dangerous, since the
      `record` at this point is a UI object representation that could
      potentially include circular references or very deeply nested objects.
      Since `_removeEmptyValues` is recursive this can lead to stack
      overflow errors.
- deposit-ui: log errors on all deposit form actions
    * This can help with debugging unexpected non-network related errors
      that might occur in the logic before/after a REST API requests.

Version v16.3.0 (released 2024-11-27)

- github: added default license from Github API
- deposit-ui: fix affiliations rendering during edits
- github: added custom_fields in metadata extraction
- github: added optional swhid field to the bibtex export
- datacite: improve error logging formatting and grouping
    * Avoids f-strings in logging calls so that entries are easier to be
      grouped.
    * Adds exception info to the logged errors.
- config: added service schema from config
- requests: manage sending notifications

Version v16.2.0 (released 2024-11-19)

- search: pass search parameters to collection records

Version v16.1.1 (released 2024-11-19)

- communities: fix set/unset of default record community
    * Closes https://github.com/inveniosoftware/invenio-app-rdm/issues/2869
    * Fixes the allowed values that can be passed to set/unset the default
      community of a record.
    * Part of the fix is to also accept an empty string ("") as a valid
      value when setting the "default" field, which was a currently wrong
      behavior in some UI logic.

Version v16.1.0 (released 2024-11-18)

- tokens: disable "sub" verification
    * According to the JWT Specification (https://datatracker.ietf.org/doc/html/rfc7519#section-4.1.2)
      `sub` has to be a string. PyJWT v2.10.0 started enforcing this validation,
      which breaks our usage of storing an object in the `sub` field.
    * Fixes jwt.decode options for specifying required fields.
- jsonschemas: backport "internal_notes" to v6.0.0
    * Backports the "internal_notes" field to the v6.0.0 JSONSchema, since
      it is backwards compatible, and thus doesn't require any record
      migration overhead.
- UI: display all affiliations

Version v16.0.1 (released 2024-11-11)

- deposit-ui: fix creator affiliations selection display
    * Fixes a bug where the selected affiliations from the dropdown do not
      appear inside the input box.

Version v16.0.0 (released 2024-11-11)

- identifiers: allow alternative identifiers with the same scheme but different values
- records: add intenal_notes schema field and bump of jsonschema version

Version v15.7.1 (released 2024-11-06)

- installation: bump babel-edtf to >=1.2.0
- tests: fix EDTF interval with unknown start/end
- ui: use config instead of hardcoded url
- setup: forward compatibility to itsdangerous>=2.1
- fix: DeprecationWarning of SQLAlchemy

Version v15.7.0 (released 2024-11-04)

- resources: make record error handlers configurable
    * Possible via the new `RDM_RECORDS_ERROR_HANDLERS` config variable.
- components: make content moderation configurable
    * Closes #1861.
    * Adds a new `RRM_CONTENT_MODERATION_HANDLERS` config variable to allow
      for configuring multiple handlers for the different write actions.
- user_moderation: use search for faster actions
    * Use search results to determine the user's list of records.
    * Use a TaskOp and Unit of Work to avoid sending Celery tasks immediately.
    * Add a cleanup task that will perform a more thorough check using the
      DB to lookup the user's records.
- deposit: add missing fields to record deserializer
- UI/UX: add consistent suggestions display to affiliations
- UI/UX: improve display of ROR information
- collections: move records search into service
- collections: added task to compute number of records for each collection
- services: make file-service components configurable
- access notification: provide correct draft preview link
    * Closes inveniosoftware/invenio-app-rdm#2827

Version v15.6.0 (released 2024-10-18)

- community: added myCommunitiesEnabled prop to CommunitySelectionSearch

Version v15.5.0 (released 2024-10-18)

- community: added autofocus prop to CommunitySelectionSearch

Version v15.4.0 (released 2024-10-17)

- DOI: fix wrong parent DOI link
- community: added props to make CommunitySelectionSearch reusable

Version v15.3.0 (released 2024-10-16)

- collections: display pages and REST API
- deposit: add feature flag for required community submission flow
- mappings: disable doc_values for geo_shape fields (#1807)
    * Fixes multiple values for ``metadata.locaations.features``.

Version v15.2.0 (released 2024-10-10)

- webpack: update axios and react-searchkit(due to axios) major versions

Version v15.1.0 (released 2024-10-10)

- jobs: register embargo update job type
- installation: upgrade invenio-jbs

Version v15.0.0 (released 2024-10-08)

- installation: bump invenio-communities
- dumper: refactor and updated docstring
- awards: added subjects and orgs, updated mappings
- relations: added subject relation in awards

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
