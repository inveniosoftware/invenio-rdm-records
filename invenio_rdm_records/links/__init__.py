# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Secret links for sharing access to records."""

from .models import SecretLink, SecretLinkSerializer
from .permissions import LinkNeed

__all__ = ("LinkNeed", "SecretLink", "SecretLinkSerializer")
