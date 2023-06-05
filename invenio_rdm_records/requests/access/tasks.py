# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 TU Wien.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Celery tasks for access requests."""

from datetime import datetime

from celery import shared_task
from invenio_db import db

from .models import AccessRequestToken


@shared_task
def clean_expired_request_access_tokens():
    """Clean up expired access request tokens."""
    AccessRequestToken.query.filter(
        AccessRequestToken.expires_at < datetime.utcnow()
    ).delete()
    db.session.commit()
