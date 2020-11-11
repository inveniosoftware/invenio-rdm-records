"""License vocabulary, in SPDX form.

Unlike other vocabularies, this one is pulled from a JSON file, not a CSV.

The `licenses.json` file should be sourced from
<https://github.com/spdx/license-list-data/blob/master/json/licenses.json>.
"""

import json
from collections import OrderedDict

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
