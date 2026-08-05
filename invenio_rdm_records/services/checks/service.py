# SPDX-FileCopyrightText: 2026 Graz University of Technology.
# SPDX-License-Identifier: MIT

"""RDM Record Checks Service."""

import sqlalchemy as sa
from invenio_checks.models import CheckRun
from invenio_pidstore.errors import PIDUnregistered
from invenio_records_resources.services import LinksTemplate, RecordService
from invenio_records_resources.services.base.utils import map_search_params


class RDMRecordChecksService(RecordService):
    """Record checks service.

    The checks service is in charge of managing the checks of a given record.
    """

    @property
    def record_cls(self):
        """Factory for creating a record class."""
        return self.config.record_cls

    @property
    def draft_cls(self):
        """Factory for creating a draft class."""
        return self.config.draft_cls

    def search(self, id_, identity, params):
        """Search for record's checks runs."""
        try:
            record = self.record_cls.pid.resolve(id_)
        except PIDUnregistered:
            record = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "read", record=record)

        search_params = map_search_params(self.config.search, params)

        check_runs = (
            CheckRun.query.filter(CheckRun.record_id == record.pid.object_uuid)
            .order_by(
                search_params["sort_direction"](
                    sa.text(",".join(search_params["sort"]))
                )
            )
            .paginate(
                page=search_params["page"],
                per_page=search_params["size"],
                error_out=False,
            )
        )

        return self.result_list(
            self,
            identity,
            check_runs,
            params=search_params,
        )
