# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Custom Fields for InvenioRDM."""

from abc import ABC, abstractmethod

class BaseCF(ABC):
    """Base Custom Field class."""

    def __init__(self, name):
        """Constructor."""
        self.name = name
        super().__init__()

    @abstractmethod
    def mapping_type(self):
        """Return the mapping type."""
        pass

    @abstractmethod
    def validate(self):
        """Validate the custom field."""
        pass
