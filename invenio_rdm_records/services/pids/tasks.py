# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""RDM PIDs Service tasks."""

from celery import shared_task


@shared_task(ignore_result=True)
def register_pid(recid, pid_type):
    """Register a PID."""
    pass
