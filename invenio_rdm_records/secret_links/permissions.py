# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Secret links for sharing access to records."""

from functools import partial

from flask_principal import Need

LinkNeed = partial(Need, "link")
LinkNeed.__doc__ = """A need with the method preset to `"link"`."""
