# SPDX-FileCopyrightText: 2021 TU Wien.
# SPDX-License-Identifier: MIT

"""Secret links for sharing access to records."""

from functools import partial

from flask_principal import Need

LinkNeed = partial(Need, "link")
LinkNeed.__doc__ = """A need with the method preset to `"link"`."""
