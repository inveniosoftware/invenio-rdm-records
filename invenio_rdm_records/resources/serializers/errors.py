# SPDX-FileCopyrightText: 2021 CERN.
# SPDX-License-Identifier: MIT

"""Errors for serializers."""


class SerializerError(Exception):
    """Base class for serializer errors."""


class VocabularyItemNotFoundError(SerializerError):
    """Error thrown when a vocabulary is not found."""
