# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Cottage Labs LLP.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""License vocabulary, in SPDX form.

Unlike other vocabularies, this one is pulled from a JSON file, not a CSV.

The `licenses.json` file should be sourced from
<https://github.com/spdx/license-list-data/blob/master/json/licenses.json>.
"""

import json
from collections import OrderedDict
from operator import itemgetter

from .vocabulary import Vocabulary


class LicenseVocabulary(Vocabulary):
    """License vocabulary, in SPDX form."""

    vocabulary_name = 'license'
    key_field = 'licenseId'
    readable_key = 'name'

    def _load_data(self):
        """Sets self.data with the filled rows."""
        with open(self.path) as f:
            data = json.load(f)
            # NOTE: We use an OrderedDict to preserve on file row order
            self.data = OrderedDict([
                (self.key(obj), obj)
                for obj in data['licenses']
            ])

    def dump_options(self):
        return [{
            'rights': item[self.readable_key],
            'scheme': 'spdx',
            'identifier': item[self.key_field],
            'url': item['seeAlso'][0] if item.get('seeAlso') else None,
        } for item in sorted(self.data.values(), key=itemgetter(self.readable_key))]
