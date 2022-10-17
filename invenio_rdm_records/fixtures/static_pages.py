# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2022 CERN.
# Copyright (C) 2019-2022 Northwestern University.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Data fixtures module."""

from invenio_db import db
from invenio_pages import Page


class StaticPages:
    """Static Pages."""

    def run(self):
        """Run the creation of Static Pages."""
        pages = [
            Page(
                url="/about",
                title="About",
                description="About",
                content="InvenioRDM about page",
                template_name="invenio_pages/default.html",
            ),
            Page(
                url="/contact",
                title="Contact",
                description="Contact",
                content="You can contact InvenioRDM developers on "
                        '<a href="https://discord.com/channels/692989811736182844/704625518552547329">'
                        "our chatroom</a>",
                template_name="invenio_pages/default.html",
            ),
        ]
        with db.session.begin_nested():
            Page.query.delete()
            db.session.add_all(pages)
        db.session.commit()
