/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import { render, screen, fireEvent, wait } from "@testing-library/react";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { CreatibutorsFileModal } from "./CreatibutorsFileModal";

const AUTHOR_XML_FILE = `<collaborationauthorlist
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:cal="http://inspirehep.net/info/HepNames/tools/authors_xml/">
  <cal:organizations>
    <foaf:Organization id="a1">
      <foaf:name>European Organization for Nuclear Research</foaf:name>
      <cal:orgName source="ROR">https://ror.org/01ggx4157</cal:orgName>
    </foaf:Organization>
  </cal:organizations>
  <cal:authors>
    <foaf:Person>
      <foaf:givenName>Jane</foaf:givenName>
      <foaf:familyName>Smith</foaf:familyName>
      <cal:authorAffiliations>
        <cal:authorAffiliation organizationid="a1"/>
      </cal:authorAffiliations>
      <cal:authorids>
        <cal:authorid source="ORCID">0000-0002-1825-0097</cal:authorid>
      </cal:authorids>
    </foaf:Person>
  </cal:authors>
</collaborationauthorlist>`;

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

const importFile = async (fileName, content, type, schema = "creators") => {
  const onConfirm = jest.fn();
  render(
    <DndProvider backend={HTML5Backend}>
      <CreatibutorsFileModal
        schema={schema}
        roleOptions={[]}
        onConfirm={onConfirm}
        trigger={<button type="button">open</button>}
      />
    </DndProvider>
  );

  fireEvent.click(screen.getByText("open"));
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
  it("accepts JSON and XML files", () => {
    render(
      <DndProvider backend={HTML5Backend}>
        <CreatibutorsFileModal
          schema="creators"
          roleOptions={[]}
          onConfirm={jest.fn()}
          trigger={<button type="button">open</button>}
        />
      </DndProvider>
    );

    fireEvent.click(screen.getByText("open"));

    expect(screen.getByText("Supported file types: .json, .xml")).toBeTruthy();
    expect(document.querySelector('input[type="file"]').getAttribute("accept")).toBe(
      ".json,.xml"
    );
  });

  it("imports authors from author.xml author list", async () => {
    const onConfirm = await importFile("authors.xml", AUTHOR_XML_FILE, "text/xml");

    expect(screen.getByText("authors.xml")).toBeTruthy();
    expect(screen.getByText("Valid authors/creators (1)")).toBeTruthy();

    await confirmImport(onConfirm);

    expect(onConfirm).toHaveBeenCalledWith([
      {
        person_or_org: {
          type: "personal",
          given_name: "Jane",
          family_name: "Smith",
          identifiers: [{ scheme: "orcid", identifier: "0000-0002-1825-0097" }],
        },
        affiliations: [
          { id: "01ggx4157", name: "European Organization for Nuclear Research" },
        ],
      },
    ]);
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
      "contributors"
    );

    expect(screen.getByText("Valid contributors (2)")).toBeTruthy();
    await confirmImport(onConfirm, "contributors", 2);

    expect(onConfirm).toHaveBeenCalledWith(JSON.parse(REPORTED_JSON_FILE));
  });

  it("reports entries that do not identify a person or organization", async () => {
    await importFile(
      "contributors.json",
      `[{"person_or_org": {"type": "personal"}}]`,
      "application/json",
      "contributors"
    );

    expect(screen.getByText(/Family name is a required field\./)).toBeTruthy();
    expect(screen.getByText(/^Import 0 contributors$/).closest("button").disabled).toBe(
      true
    );
  });

  it("reports an error for unsupported files", async () => {
    await importFile("authors.txt", "Smith, Jane", "text/plain");

    expect(
      screen.getByText(/The file does not match the expected .* format/)
    ).toBeTruthy();
  });
});
