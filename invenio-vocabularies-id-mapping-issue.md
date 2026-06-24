# Bug: Vocabulary `id` field is mapped as `text` in OpenSearch, causing term queries to fail for non-lowercase IDs

## Summary

The OpenSearch mapping for the vocabulary index maps the `id` field as `type: text` (with a `keyword` sub-field). The `get_vocabulary_props` function in `invenio-rdm-records` searches for vocabulary terms using `dsl.Q("term", id=id_)` — a term query on the text field. For IDs that contain uppercase letters or are split by the text analyzer (e.g., `EHVM-H119`), the term query returns zero hits and raises `VocabularyItemNotFoundError`, even though the record exists in both the database and the OpenSearch index.

## Affected versions

- `invenio-rdm-records` (query side — uses `dsl.Q("term", id=...)` on a text field)
- `invenio-vocabularies` (mapping side — defines `id` as `text`)

## Steps to reproduce

1. Load a vocabulary type that contains terms with non-lowercase IDs (e.g., CCMM resource types, which use identifiers like `EHVM-H119`).
2. Create a dataset record that references one of these terms as its `resource_type`.
3. Navigate to the dataset record's detail page in the UI.

**Result:**
```
invenio_rdm_records.resources.serializers.errors.VocabularyItemNotFoundError:
  The 'resourcetypes' vocabulary item 'EHVM-H119' was not found.
```

## Root cause

### Mapping side (`invenio-vocabularies`)

The vocabulary index mapping defines the `id` field as:
```json
{"type": "text", "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}}
```

When the standard OpenSearch text analyzer processes `EHVM-H119`, it produces lowercase tokens (e.g., `ehvm` and `h119` after hyphen splitting). The original string `EHVM-H119` is not preserved as an exact token in the text field's inverted index.

### Query side (`invenio-rdm-records`)

`get_vocabulary_props` in `invenio_rdm_records/resources/serializers/utils.py`:

```python
results = vocabulary_service.read_all(
    system_identity,
    ["id"] + fields,
    vocabulary,
    extra_filter=dsl.Q("term", id=id_),  # <-- term query on text field
)
```

A `term` query on a text field matches analyzed tokens exactly. Because `EHVM-H119` is not stored as an exact token, the query returns zero hits, and the function raises `VocabularyItemNotFoundError`.

Standard InvenioRDM resource type IDs (e.g., `dataset`, `publication`, `software`) are lowercase and single-word, so they survive text analysis. This bug is invisible until a vocabulary type with uppercase or hyphenated IDs is loaded.

## Impact

Any vocabulary term whose ID contains uppercase letters or other characters that the text analyzer transforms will be unreachable by `get_vocabulary_props`. This causes the DataCite serializer (called during signposting on every record detail page) to crash with a 500 error for any record using such a term.

Triggered by the CCMM resource type vocabulary, which uses COAR IDs such as `EHVM-H119`, `c_18cc`, `C_dcae04ef`, etc.

## Proposed fix

**Option A — Fix the mapping** (`invenio-vocabularies`): Change the `id` field to `type: keyword` so term queries work as exact matches regardless of case or character content.

**Option B — Fix the query** (`invenio-rdm-records`): Change `dsl.Q("term", id=id_)` to `dsl.Q("term", **{"id.keyword": id_})` in `get_vocabulary_props`.

Option B is a one-line change and does not require an index migration.

## Workaround (applied in this repository)

Recreate the vocabulary index with `id` as a `keyword` field:

```python
from invenio_search import current_search_client

mapping = current_search_client.indices.get_mapping(index='frozen_testing-vocabularies-vocabulary-v1.0.0')
m = list(mapping.values())[0]['mappings']
m['properties']['id'] = {'type': 'keyword', 'ignore_above': 256}

current_search_client.indices.delete(index='frozen_testing-vocabularies-vocabulary-v1.0.0')
current_search_client.indices.create(
    index='frozen_testing-vocabularies-vocabulary-v1.0.0',
    body={'mappings': m}
)
current_search_client.indices.update_aliases({'actions': [
    {'add': {'index': 'frozen_testing-vocabularies-vocabulary-v1.0.0',
             'alias': 'frozen_testing-vocabularies'}}
]})
```

Then reindex all vocabulary records from the database.
