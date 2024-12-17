# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""OCFL integration for InvenioRDM."""

from io import BytesIO
from os.path import join

from flask_resources import JSONSerializer
from invenio_access.permissions import system_identity
from invenio_ocfl.services import OCFLObjectBuilder
from ocflcore import StreamDigest

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.resources.serializers import \
    DataCite43XMLSerializer, DublinCoreXMLSerializer


class RDMRecordBuilder(OCFLObjectBuilder):
    """OCFL object builder for RDM Records."""

    serializers = {
        'record.json': JSONSerializer(),
        'meta/dublin-core.xml': DublinCoreXMLSerializer(),
        'meta/datacite4_3.xml': DataCite43XMLSerializer(),
    }
    service = current_rdm_records_service

    def files(self, record):
        """"Build data files."""
        try:
            result = self.service.files.list_files(record['id'], system_identity)
            for f in result.entries:
                item = self.service.files.get_file_content(record['id'], f['key'], system_identity)

                bytes = StreamDigest(BytesIO(JSONSerializer().serialize_object(item.to_dict()).encode('utf8')))
                yield join('meta', f['key']+".json"), bytes.stream, bytes.digest

                file_stream = StreamDigest(item.get_stream('rb'))
                yield join("data", f['key']), file_stream.stream, file_stream.digest
        except Exception:
            print("No files")
            return
