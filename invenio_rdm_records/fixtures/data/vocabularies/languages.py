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

scope_map = {
    "I": "individual",
    "M": "macrolanguage",
    "S": "special-scope",
}

type_map = {
    "A": "ancient",
    "C": "constructed",
    "E": "extinct",
    "H": "historical",
    "L": "living",
    "S": "special-type",
}


def iter_languages():
    """Iterate over languages."""
    for lang in pycountry.languages:
        record = {
            "id": lang.alpha_3,
            "title": {"en": lang.name},
            "props": {"alpha_2": getattr(lang, "alpha_2", "")},
            "tags": [scope_map[lang.scope], type_map[lang.type]],
        }
        yield record


def create_yaml_languages():
    """Create languages to yaml file."""
    with open(join(dirname(__file__), "languages.yaml"), "w") as f:
        yaml.dump(list(iter_languages()), f)


if __name__ == "__main__":
    print("Creating languages.yaml...")
    create_yaml_languages()
