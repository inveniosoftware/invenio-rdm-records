# SPDX-FileCopyrightText: 2020 CERN.
# SPDX-FileCopyrightText: 2020 Northwestern University.
# SPDX-License-Identifier: MIT

"""Test utilities.

NOTE: To get pytest's nice assertions this file had to be prefixed with
`test_` .
"""

import pytest
from marshmallow import ValidationError


def assert_raises_messages(lambda_expression, expected_messages):
    with pytest.raises(ValidationError) as e:
        lambda_expression()

    messages = e.value.normalized_messages()
    assert expected_messages == messages
