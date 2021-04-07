# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Models for Invenio RDM Records."""

from .creatibutor_role import CreatibutorRoleVocabulary
from .resource_type import ResourceTypeVocabulary
from .title_type import TitleTypeVocabulary
from .vocabularies import Vocabularies
from .vocabulary import Vocabulary

__all__ = (
    "CreatibutorRoleVocabulary",
    "ResourceTypeVocabulary",
    "TitleTypeVocabulary",
    "Vocabularies",
    "Vocabulary",
)
