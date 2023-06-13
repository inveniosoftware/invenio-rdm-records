# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Resource access token for sharing access to resources of records."""

from .permissions import RATNeed
from .resource_access import validate_rat

__all__ = ("RATNeed", "validate_rat")
