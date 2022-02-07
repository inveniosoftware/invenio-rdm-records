# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Graz University of Technology.
#
# Invenio-Records-Resources is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.
from invenio_db import db
from invenio_records_resources.services.uow import Operation


class OAISetCommitOp(Operation):
    def __init__(self, oai_set):
        super().__init__()
        self._oai_set = oai_set

    def on_register(self, uow):
        db.session.add(self._oai_set)

class OAISetDeleteOp(Operation):
    def __init__(self, oai_set):
        super().__init__()
        self._oai_set = oai_set

    def on_register(self, uow):
        db.session.remove(self._oai_set)
