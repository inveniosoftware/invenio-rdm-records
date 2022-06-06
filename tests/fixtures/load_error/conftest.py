# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Necessary conftest structure to test conflicts."""

import pytest
from invenio_app.factory import create_api as _create_api


@pytest.fixture(scope="module")
def extra_entry_points():
    """Conflicting entry points.

    We fake conflicting entrypoint groups by providing multiple vocabularies
    referring to conflicting vocabularies.yaml. In practice, there would
    ordinarily be 1 vocabularies name for the given module's
    'invenio_rdm_records.fixtures' group and conflicts would occur across
    modules.
    """
    return {
        "invenio_rdm_records.fixtures": [
            "vocabularies_A = conflicting_module_A.fixtures.vocabularies",
            "vocabularies_B = conflicting_module_B.fixtures.vocabularies",
        ],
    }


@pytest.fixture(scope="module")
def create_app(instance_path, entry_points):
    """Application factory fixture."""
    return _create_api
