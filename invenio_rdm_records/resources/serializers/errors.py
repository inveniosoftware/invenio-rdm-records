# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Errors for serializers."""


class SerializerError(Exception):
    """Base class for serializer errors."""


class VocabularyItemNotFoundError(SerializerError):
    """Error thrown when a vocabulary is not found."""
