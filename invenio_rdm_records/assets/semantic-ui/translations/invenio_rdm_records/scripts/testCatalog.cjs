// SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
// SPDX-License-Identifier: MIT

const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const test = require("node:test");
const i18next = require("i18next");
const { Parser } = require("i18next-scanner");
const { options } = require("../i18next-scanner.config.js");

const source = `msgid ""
msgstr ""
"Language: sv\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"

msgid "Reviewed"
msgstr "Granskad"

#, python-format, fuzzy
msgid "Needs review"
msgstr "Ej granskad"

msgid "item"
msgid_plural "items"
msgstr[0] "Sak"
msgstr[1] "Saker"

msgid "Missing"
msgstr ""
`;

test("compile reviewed entries and v4 plurals; fall back for fuzzy entries", async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "i18n-catalog-"));
  try {
    const messages = path.join(directory, "messages", "sv");
    fs.mkdirSync(messages, { recursive: true });
    fs.writeFileSync(path.join(messages, "messages.po"), source);
    const result = spawnSync(
      process.execPath,
      [path.join(__dirname, "compileCatalog.js")],
      {
        cwd: directory,
        encoding: "utf8",
      }
    );
    assert.equal(result.status, 0, result.stderr);
    const translations = JSON.parse(
      fs.readFileSync(path.join(messages, "translations.json"), "utf8")
    );
    assert.equal(translations.Reviewed, "Granskad");
    assert.equal(translations["Needs review"], undefined);
    assert.equal(translations.Missing, undefined);
    assert.equal(translations.item_one, "Sak");
    assert.equal(translations.item_other, "Saker");
    const runtime = i18next.createInstance();
    await runtime.init({
      lng: "sv",
      fallbackLng: "en",
      debug: false,
      keySeparator: false,
      nsSeparator: false,
      resources: {
        sv: { translation: translations },
        en: {
          translation: { "Needs review": "Needs review", "Missing": "Missing" },
        },
      },
    });
    assert.equal(runtime.t("Reviewed"), "Granskad");
    assert.equal(runtime.t("Needs review"), "Needs review");
    assert.equal(runtime.t("Missing"), "Missing");
    assert.equal(runtime.t("item", { count: 1 }), "Sak");
    assert.equal(runtime.t("item", { count: 2 }), "Saker");
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("extract DOI validation messages from both publish controls", () => {
  const parser = new Parser({ ...options, debug: false });
  const controls = path.resolve(
    __dirname,
    "../../../js/invenio_rdm_records/src/deposit/controls/PublishButton"
  );
  for (const [filename, action] of [
    ["PublishButton.js", "publishing"],
    ["SubmitReviewButton.js", "submitting for review"],
  ]) {
    parser.parseFuncFromString(fs.readFileSync(path.join(controls, filename), "utf8"));
    const message = `DOI is needed. You need to reserve a DOI before ${action}.`;
    assert.equal(parser.get().en.translations[message], message);
  }
});

test("extract complete messages containing formatting and links", () => {
  const deposit = path.resolve(
    __dirname,
    "../../../js/invenio_rdm_records/src/deposit"
  );
  const cases = [
    [
      "controls/PublishButton/SubmitReviewModal.js",
      [
        "The '{{communityTitle}}' curators will have access to <bold>view and edit</bold> your upload's metadata and files.",
        "If your upload is accepted by the community curators, it will be <bold>immediately published</bold>. Before that, you will still be able to modify metadata and files of this upload.",
        "Your upload will be <bold>immediately published</bold> in '{{communityTitle}}'. You will no longer be able to change the files in the upload! However, you will still be able to update the record's metadata later.",
      ],
    ],
    [
      "fields/AccessField/components/AccessMessage.js",
      [
        "On <bold>{{fmtDate}}</bold> the record will automatically be made publicly accessible. Until then, the record can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions.",
        "The record can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions.",
        "The record is publicly accessible. The files can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions.",
        "The record is publicly accessible. On <bold>{{fmtDate}}</bold> the files will automatically be made publicly accessible. Until then, the files can <bold>only</bold> be accessed by <bold>users specified</bold> in the permissions.",
      ],
    ],
    [
      "fields/AccessField/components/EmbargoAccess.js",
      [
        "Record or files protection must be <bold>restricted</bold> to apply an embargo.",
      ],
    ],
    [
      "components/StorageSettings/StorageOverview.js",
      [
        "You can now manage your record storage by assigning additional quota as needed. <helpLink>Find out more.</helpLink>",
      ],
    ],
    [
      "fields/VersionField/VersionField.js",
      [
        "Mostly relevant for software and dataset uploads. A semantic version string is preferred see <semverLink>semver.org</semverLink>, but any version string is accepted.",
      ],
    ],
  ];
  for (const [filename, messages] of cases) {
    const parser = new Parser({ ...options, debug: false });
    parser.parseTransFromString(fs.readFileSync(path.join(deposit, filename), "utf8"));
    assert.deepEqual(
      parser.get().en.translations,
      Object.fromEntries(messages.map((message) => [message, message])),
      filename
    );
  }
});

test("render Swedish Trans messages with reordered values and named elements", async () => {
  const React = require("react");
  const { TransWithoutContext } = require("react-i18next");
  const runtime = i18next.createInstance();
  const key = "On <bold>{{fmtDate}}</bold> see <helpLink>details</helpLink>.";
  await runtime.init({
    lng: "sv",
    fallbackLng: "en",
    keySeparator: false,
    nsSeparator: false,
    resources: {
      sv: {
        translation: {
          [key]: "Se <helpLink>detaljer</helpLink> den <bold>{{fmtDate}}</bold>.",
        },
      },
    },
  });
  const output = TransWithoutContext({
    i18n: runtime,
    defaults: key,
    values: { fmtDate: "13 november" },
    components: {
      bold: React.createElement("b"),
      helpLink: React.createElement("a", { href: "./" }),
    },
  });
  const elements = output.filter(React.isValidElement);
  assert.deepEqual(
    elements.map((element) => element.type),
    ["a", "b"]
  );
  assert.equal(elements[0].props.href, "./");
  assert.deepEqual(elements[0].props.children, ["detaljer"]);
  assert.deepEqual(elements[1].props.children, ["13 november"]);
});

test("extract complete source messages", () => {
  const sourceRoot = path.resolve(__dirname, "../../../js");
  const cases = [
    [
      "invenio_rdm_records/src/deposit/fields/License/NoLicenseResults.js",
      ["Did not find your license? <customLink>Add a custom license.</customLink>"],
    ],
    [
      "invenio_rdm_records/src/deposit/components/StorageSettings/StorageOverview.js",
      ["{{percent}}% used", "Draft", "Published"],
    ],
    [
      "invenio_rdm_records/src/deposit/fields/FileUploader/FileUploader.js",
      [
        "Uploading the selected files would result in {{count}} files (max.{{maxFiles}})",
      ],
    ],
    [
      "invenio_rdm_records/src/deposit/fields/CreatibutorsField/CreatibutorsFileModal.js",
      [
        "Upload authors/creators from file",
        "Upload contributors from file",
        "Upload a JSON file containing a list of authors/creators.",
        "Upload a JSON file containing a list of contributors.",
        "Valid authors/creators ({{count}})",
        "Valid contributors ({{count}})",
        "Add authors/creators from file",
        "Add contributors from file",
        "Review authors/creators from file",
        "Review contributors from file",
        "Import {{count}} authors/creators",
        "Import {{count}} contributors",
      ],
    ],
    [
      "invenio_rdm_records/src/deposit/fields/CreatibutorsField/CreatibutorsDisplay/CreatibutorsInlinePanel.js",
      ["Filter contributors...", "Filter authors/creators..."],
    ],
    [
      "invenio_rdm_records/src/deposit/fields/FileUploader/FileUploaderToolbar.js",
      ["{{used}} out of {{available}}"],
    ],
    [
      "invenio_rdm_records/src/deposit/fields/FileUploader/QuotaManager/QuotaManager.js",
      ["New total: <bold>{{quota}} GB</bold>"],
    ],
    [
      "invenio_rdm_records/src/deposit/fields/FileUploader/QuotaManager/QuotaDisplay.js",
      [
        "Default ({{quota}} GB)",
        "Additional (+{{quota}} GB)",
        "Available ({{quota}} GB)",
        "See your <settingsLink>storage settings</settingsLink> for usage across all records",
      ],
    ],
    [
      "invenio_rdm_records/src/deposit/fields/FileUploader/EditFilesAccordion.js",
      [
        "To <strong>add, modify or remove files</strong>, it is recommended that you create a new version. A new record is created which tracks the evolution of your work.",
        "To <strong>correct</strong> minor errors, you can unlock the files.",
      ],
    ],
  ];
  for (const [filename, messages] of cases) {
    const parser = new Parser({ ...options, debug: false });
    const source = fs.readFileSync(path.join(sourceRoot, filename), "utf8");
    parser.parseFuncFromString(source);
    parser.parseTransFromString(source);
    const extracted = parser.get().en.translations;
    for (const message of messages) {
      assert.ok(
        Object.hasOwn(extracted, message) || Object.hasOwn(extracted, `${message}_one`),
        `${filename}: missing ${message}`
      );
    }
  }
});
