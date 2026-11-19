# SPDX-FileCopyrightText: 2026 CERN.
# SPDX-License-Identifier: MIT

"""Resources serializers utils tests."""

from invenio_rdm_records.resources.serializers.utils import dict_get


def test_dict_get():
    """Test dictionary lookup by a key."""
    d = {
        "a": 1,
        "b": {"c": None},
        "d": ["1", "2"],
    }
    assert dict_get(d, "a") == d["a"]
    assert dict_get(d, "b") == d["b"]
    assert dict_get(d, "b.c") == d["b"]["c"]
    assert dict_get(d, "d") == d["d"]
    assert dict_get(d, "d.0") == d["d"][0]
    assert dict_get(d, "d.1") == d["d"][1]
    assert dict_get(d, "d.-1") == d["d"][-1]

    assert dict_get(d, "x") is None
    assert dict_get(d, "a.x") is None
    assert dict_get(d, "b.x") is None
    assert dict_get(d, "b.c.0") is None
    assert dict_get(d, "d.3") is None

    assert dict_get(d, "x", "default") == "default"
    assert dict_get(d, "a.x", 42) == 42
    assert dict_get(d, "b.x", 3.14) == 3.14
    assert dict_get(d, "b.c.0", []) == []
    assert dict_get(d, "d.3", {}) == {}
