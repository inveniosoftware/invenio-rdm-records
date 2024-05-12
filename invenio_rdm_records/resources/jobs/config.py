# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 CERN.
# Copyright (C) 2020 Northwestern University.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Jobs resource configuration."""

from flask_resources import ResourceConfig
from invenio_records_resources.services.base.config import ConfiguratorMixin, FromConfig

class JobsResourceConfig(ResourceConfig, ConfiguratorMixin):
    """Jobs resource config."""

    # Blueprint configuration
    blueprint_name = None
    url_prefix = "/jobs"
    routes = {
        "list": "",
    }


