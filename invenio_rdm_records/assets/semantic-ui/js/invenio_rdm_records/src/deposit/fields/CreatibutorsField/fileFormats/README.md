# Creatibutor file formats

The "Add authors/contributors from file" dialog of the deposit form imports
creators and contributors from a file. The formats it accepts come from a
registry: invenio-rdm-records registers a JSON format, and an instance can add
its own formats (e.g. an XML author list) or remove the built-in one.

## A format

```js
{
  id: "author_xml",               // unique
  label: i18next.t("XML (author.xml)"), // tab name in the dialog, already translated
  extension: ".xml",              // unique; selects the format from the file name
  order: 110,                     // optional, lower first; JSON is 100
  example: "<collaborationauthorlist>…", // optional, shown in the format's tab
  note: i18next.t("…"),           // optional, shown under the example, already translated
  parse: (text) => [/* creatibutors */], // return null (or throw) for invalid content
}
```

`parse` receives the file's text (without a byte order mark) and returns an
array of creatibutors in the deposit form's shape, e.g.
`{ person_or_org: { type: "personal", family_name, given_name, identifiers }, affiliations }`.
A `role` may be an id (`"projectmember"`) or a vocabulary object (`{ id, title }`).

The dialog selects the format by extension (case-insensitive; the longest
match wins, so `.tar.gz` is preferred over `.gz`). It reports "This file type
is not supported." when no format matches, and "This is not a valid {label}
file." when `parse` returns something other than an array or throws.

## Registering a format in an instance

Register formats in a module the deposit page loads. In an InvenioRDM instance
that is the overridable registry,
`assets/js/invenio_app_rdm/overridableRegistry/mapping.js`; keep the
registration in its own module and import it from there:

```js
// assets/js/components/deposit/fileFormats/index.js
import {
  getCreatibutorFileFormats,
  registerCreatibutorFileFormat,
} from "@js/invenio_rdm_records";
import { myFileFormat } from "./myFormat";

if (!getCreatibutorFileFormats().some(({ id }) => id === myFileFormat.id)) {
  registerCreatibutorFileFormat(myFileFormat);
}
```

```js
// assets/js/invenio_app_rdm/overridableRegistry/mapping.js
import "../../components/deposit/fileFormats";
```

## API

Exported from `@js/invenio_rdm_records`:

| Export                                  |                                                                                                           |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `registerCreatibutorFileFormat(format)` | Add a format to the dialog. Throws on an invalid descriptor, a duplicate `id` or a duplicate `extension`. |
| `unregisterCreatibutorFileFormat(id)`   | Remove a format, e.g. the built-in `"json"`. Throws when `id` is not registered.                          |
| `getCreatibutorFileFormats()`           | The registered formats, in the order the dialog offers them.                                              |
| `createCreatibutorFileFormatRegistry()` | A separate registry with the same `register`/`unregister`/`getFormats`, e.g. for tests.                   |
| `DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER` | `100`, the order of JSON and of formats that set none.                                                    |

When no format is registered, the dialog's button is not shown.
