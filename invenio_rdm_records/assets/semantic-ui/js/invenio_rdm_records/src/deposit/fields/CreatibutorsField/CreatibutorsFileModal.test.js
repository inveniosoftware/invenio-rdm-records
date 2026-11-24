/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import { render, screen, fireEvent, wait } from "@testing-library/react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import Overridable, { OverridableContext, parametrize } from "react-overridable";
import {
  CREATIBUTORS_FILE_MODAL_ID,
  CreatibutorsFileModal,
} from "./CreatibutorsFileModal";
import { jsonFileFormat } from "./fileFormats";

const JSON_FILE = `[
  {
    "person_or_org": { "type": "personal", "family_name": "Smith" }
  }
]`;

const REPORTED_JSON_FILE = `[
  {
    "person_or_org": {
      "type": "personal",
      "family_name": "Smith",
      "given_name": "Jane",
      "identifiers": [{ "scheme": "orcid", "identifier": "0000-0002-1825-0097" }]
    },
    "affiliations": [{ "name": "CERN" }]
  },
  {
    "person_or_org": {
      "type": "organizational",
      "name": "European Organization for Nuclear Research"
    }
  }
]`;

const CONTRIBUTORS_JSON_FILE = `[
  {
    "person_or_org": {
      "type": "personal",
      "family_name": "Smith",
      "given_name": "Jane"
    },
    "role": "editor"
  },
  {
    "person_or_org": {
      "type": "organizational",
      "name": "European Organization for Nuclear Research"
    },
    "role": "hostinginstitution"
  }
]`;

const EXPORTED_CONTRIBUTORS_JSON_FILE = `[
  {
    "person_or_org": {
      "type": "personal",
      "family_name": "Smith",
      "given_name": "Jane"
    },
    "role": { "id": "editor" }
  }
]`;

const customFormat = {
  id: "custom",
  label: "Custom (.custom)",
  extension: ".custom",
  example: "Smith, Jane",
  note: "Custom format note",
  parse: (text) => [
    { person_or_org: { type: "personal", given_name: "Jane", family_name: "Smith" } },
  ],
};

const modal = (props) => (
  <DndProvider backend={HTML5Backend}>
    <CreatibutorsFileModal
      schema="creators"
      roleOptions={[]}
      onConfirm={jest.fn()}
      trigger={<button type="button">open</button>}
      {...props}
    />
  </DndProvider>
);

const renderModal = ({ schema = "creators", fileFormats } = {}) => {
  const onConfirm = jest.fn();
  render(modal({ schema, onConfirm, ...(fileFormats && { fileFormats }) }));
  fireEvent.click(screen.getByText("open"));
  return onConfirm;
};

const importFile = async (
  fileName,
  content,
  type,
  { schema = "creators", fileFormats } = {}
) => {
  const onConfirm = renderModal({ schema, fileFormats });
  const input = document.querySelector('input[type="file"]');
  fireEvent.change(input, {
    target: { files: [new File([content], fileName, { type })] },
  });

  await wait(() =>
    expect(
      screen.getByText(/Review (authors\/creators|contributors) from file/)
    ).toBeTruthy()
  );
  return onConfirm;
};

const confirmImport = async (onConfirm, type = "authors/creators", count = 1) => {
  const label = new RegExp(`^Import ${count} ${type}$`);
  await wait(() => expect(screen.getByText(label)).toBeTruthy());
  fireEvent.click(screen.getByText(label));
};

describe("CreatibutorsFileModal", () => {
  it("offers the built-in formats by default", () => {
    renderModal();

    expect(screen.getByText("Supported file types: .json")).toBeTruthy();
    expect(document.querySelector('input[type="file"]').getAttribute("accept")).toBe(
      ".json"
    );
    expect(screen.getByText("JSON").closest(".item")).toBeTruthy();
    // The slash must reach the page as text, not as an HTML entity.
    expect(
      screen.getByText("Upload a file containing a list of authors/creators.")
    ).toBeTruthy();
  });

  it("is overridable with parametrize, as documented", () => {
    render(
      <DndProvider backend={HTML5Backend}>
        <OverridableContext.Provider
          value={{
            [CREATIBUTORS_FILE_MODAL_ID]: parametrize(CreatibutorsFileModal, {
              fileFormats: [jsonFileFormat, customFormat],
            }),
          }}
        >
          <Overridable id={CREATIBUTORS_FILE_MODAL_ID}>
            <CreatibutorsFileModal
              schema="creators"
              roleOptions={[]}
              onConfirm={jest.fn()}
              trigger={<button type="button">open</button>}
            />
          </Overridable>
        </OverridableContext.Provider>
      </DndProvider>
    );
    fireEvent.click(screen.getByText("open"));

    expect(screen.getByText("Supported file types: .json, .custom")).toBeTruthy();
    expect(screen.getByText("Custom (.custom)").closest(".item")).toBeTruthy();
  });

  it("reports a format-specific error when the file contents are invalid", async () => {
    await importFile("authors.json", "not JSON", "application/json");

    expect(screen.getByText("This is not a valid JSON file.")).toBeTruthy();
  });

  it("imports creatibutors from a JSON file", async () => {
    const onConfirm = await importFile("authors.json", JSON_FILE, "application/json");

    await confirmImport(onConfirm);

    expect(onConfirm).toHaveBeenCalledWith(JSON.parse(JSON_FILE));
  });

  it("imports contributors that carry a role", async () => {
    const onConfirm = await importFile(
      "contributors.json",
      CONTRIBUTORS_JSON_FILE,
      "application/json",
      { schema: "contributors" }
    );

    expect(screen.getByText("Valid contributors (2)")).toBeTruthy();
    await confirmImport(onConfirm, "contributors", 2);

    expect(onConfirm).toHaveBeenCalledWith(JSON.parse(CONTRIBUTORS_JSON_FILE));
  });

  it("imports contributors with roles from exported JSON", async () => {
    const onConfirm = await importFile(
      "contributors.json",
      EXPORTED_CONTRIBUTORS_JSON_FILE,
      "application/json",
      { schema: "contributors" }
    );

    expect(screen.getByText("Valid contributors (1)")).toBeTruthy();
    await confirmImport(onConfirm, "contributors", 1);

    expect(onConfirm).toHaveBeenCalledWith([
      { ...JSON.parse(EXPORTED_CONTRIBUTORS_JSON_FILE)[0], role: "editor" },
    ]);
  });

  it("reports contributors that do not carry a role", async () => {
    await importFile("contributors.json", REPORTED_JSON_FILE, "application/json", {
      schema: "contributors",
    });

    // The record schema requires a role for contributors, so neither entry imports.
    expect(screen.getAllByText(/Role is a required field\./).length).toBe(2);
    expect(screen.getByText(/^Import 0 contributors$/).closest("button").disabled).toBe(
      true
    );
  });

  it("reports entries that do not identify a person or organization", async () => {
    await importFile(
      "authors.json",
      `[{"person_or_org": {"type": "personal"}}]`,
      "application/json"
    );

    expect(screen.getByText(/Family name is a required field\./)).toBeTruthy();
    expect(
      screen.getByText(/^Import 0 authors\/creators$/).closest("button").disabled
    ).toBe(true);
  });

  it("reports an error for unsupported files", async () => {
    await importFile("authors.txt", "Smith, Jane", "text/plain");

    expect(screen.getByText("This file type is not supported.")).toBeTruthy();
  });

  it("offers and imports formats supplied by an instance", async () => {
    const onConfirm = jest.fn();
    const fileFormats = [jsonFileFormat, customFormat];
    render(modal({ onConfirm, fileFormats }));
    fireEvent.click(screen.getByText("open"));

    expect(screen.getByText("Supported file types: .json, .custom")).toBeTruthy();
    expect(document.querySelector('input[type="file"]').getAttribute("accept")).toBe(
      ".json,.custom"
    );

    fireEvent.click(screen.getByText("Custom (.custom)"));
    expect(screen.getByText("Custom format note")).toBeTruthy();

    fireEvent.change(document.querySelector('input[type="file"]'), {
      target: {
        files: [new File(["Smith, Jane"], "authors.custom", { type: "text/plain" })],
      },
    });
    await wait(() =>
      expect(screen.getByText(/Review authors\/creators from file/)).toBeTruthy()
    );
    await confirmImport(onConfirm);

    expect(onConfirm).toHaveBeenCalledWith([
      {
        person_or_org: { type: "personal", given_name: "Jane", family_name: "Smith" },
      },
    ]);
  });

  it("hides the trigger when there are no formats", () => {
    render(modal({ fileFormats: [] }));

    expect(screen.queryByText("open")).toBeNull();
  });
});
