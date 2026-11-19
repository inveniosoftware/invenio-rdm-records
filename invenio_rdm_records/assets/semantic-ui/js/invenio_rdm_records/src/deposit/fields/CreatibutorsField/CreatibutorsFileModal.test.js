/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { render, screen, fireEvent, wait } from "@testing-library/react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { CreatibutorsFileModal } from "./CreatibutorsFileModal";
import {
  getCreatibutorFileFormats,
  registerCreatibutorFileFormat,
  unregisterCreatibutorFileFormat,
} from "./fileFormats";

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

const renderModal = ({ schema = "creators" } = {}) => {
  const onConfirm = jest.fn();
  render(modal({ schema, onConfirm }));
  fireEvent.click(screen.getByText("open"));
  return onConfirm;
};

const importFile = async (fileName, content, type, { schema = "creators" } = {}) => {
  const onConfirm = renderModal({ schema });
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

  it("reports a format-specific error when the file contents are invalid", async () => {
    await importFile("authors.json", "not JSON", "application/json");

    expect(screen.getByText("This is not a valid JSON file.")).toBeTruthy();
  });

  it("imports creatibutors from a JSON file", async () => {
    const onConfirm = await importFile("authors.json", JSON_FILE, "application/json");

    await confirmImport(onConfirm);

    expect(onConfirm).toHaveBeenCalledWith(JSON.parse(JSON_FILE));
  });

  it("imports contributors that do not carry a role", async () => {
    const onConfirm = await importFile(
      "contributors.json",
      REPORTED_JSON_FILE,
      "application/json",
      { schema: "contributors" }
    );

    expect(screen.getByText("Valid contributors (2)")).toBeTruthy();
    await confirmImport(onConfirm, "contributors", 2);

    expect(onConfirm).toHaveBeenCalledWith(JSON.parse(REPORTED_JSON_FILE));
  });

  it("imports roles exported as vocabulary objects as their id", async () => {
    const exported = `[{
      "person_or_org": { "type": "personal", "family_name": "Smith" },
      "role": { "id": "projectmember", "title": { "en": "Project member" } }
    }]`;
    const onConfirm = await importFile(
      "contributors.json",
      exported,
      "application/json",
      {
        schema: "contributors",
      }
    );

    expect(screen.getByText("Valid contributors (1)")).toBeTruthy();
    await confirmImport(onConfirm, "contributors", 1);

    expect(onConfirm).toHaveBeenCalledWith([
      {
        person_or_org: { type: "personal", family_name: "Smith" },
        role: "projectmember",
      },
    ]);
  });

  it("reports roles that are neither an id nor a vocabulary object", async () => {
    await importFile(
      "contributors.json",
      `[{"person_or_org": {"type": "personal", "family_name": "Smith"}, "role": {"title": "x"}}]`,
      "application/json",
      { schema: "contributors" }
    );

    expect(screen.getByText(/Role must be a role id/)).toBeTruthy();
  });

  it("reports entries that do not identify a person or organization", async () => {
    await importFile(
      "contributors.json",
      `[{"person_or_org": {"type": "personal"}}]`,
      "application/json",
      { schema: "contributors" }
    );

    expect(screen.getByText(/Family name is a required field\./)).toBeTruthy();
    expect(screen.getByText(/^Import 0 contributors$/).closest("button").disabled).toBe(
      true
    );
  });

  it("reports an error for unsupported files", async () => {
    await importFile("authors.txt", "Smith, Jane", "text/plain");

    expect(screen.getByText("This file type is not supported.")).toBeTruthy();
  });

  it("offers and imports formats registered by an instance", async () => {
    registerCreatibutorFileFormat(customFormat);
    const onConfirm = jest.fn();
    render(modal({ onConfirm }));
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

  it("offers no dialog when no format is registered", () => {
    const registered = getCreatibutorFileFormats();
    registered.forEach(({ id }) => unregisterCreatibutorFileFormat(id));
    try {
      render(modal());
      expect(screen.queryByText("open")).toBeNull();
    } finally {
      registered.forEach(registerCreatibutorFileFormat);
    }
  });
});
