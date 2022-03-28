# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio-RDM-Records Awards vocabulary customizations."""


from flask_babelex import lazy_gettext as _
from invenio_records_resources.services.records.facets import TermsFacet
from invenio_vocabularies.contrib.awards.config import AwardsSearchOptions as \
    AwardsSearchOptionsBase
from invenio_vocabularies.contrib.awards.services import \
    AwardsServiceConfig as AwardsServiceConfigBase
from invenio_vocabularies.contrib.funders.facets import FundersLabels


class AwardsSearchOptions(AwardsSearchOptionsBase):
    """Awards search options with facets."""

    facets = {
        'funders': TermsFacet(
            field='funder.id',
            label=_('Funders'),
            value_labels=FundersLabels('funders')
        )
    }


class AwardsServiceConfig(AwardsServiceConfigBase):
    """Awards service config with facets."""

    search = AwardsSearchOptions
