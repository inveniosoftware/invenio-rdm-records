# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 Graz University of Technology.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Func to generate languages.yaml."""

from os.path import dirname, join

import pycountry
import yaml
from babel import Locale, UnknownLocaleError
from invenio_i18n.ext import current_i18n


def create_yaml_languages():
    """Create languages to yaml file."""
    records = []
    instance_languages = [lang[0] for lang in current_i18n.get_languages()]

    for pycountry_language in pycountry.languages:
        pycountry_language_code = pycountry_language.alpha_3
        try:
            # Parse the locale for the pycountry language entry
            locale = Locale.parse(pycountry_language_code)
            # Create the title dict for all the configured instance languages
            title = {}
            for instance_lang in instance_languages:
                title[instance_lang] = locale.get_display_name(instance_lang)
            # Create record
            metadata = {
                "id": pycountry_language_code,
                "title": title,
            }
            records.append(metadata)
        except UnknownLocaleError:
            # Pass for the pycountry languages
            # that babel cannot parse the locale
            pass
    with open(join(dirname(__file__), 'languages.yaml'), 'w') as f:
        data = yaml.dump(records, f)

    return data
