// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Field } from "./Field";
import { SchemaField } from "./SchemaField";

describe("SchemaField tests", () => {
  const schemaField = new SchemaField({
    fieldpath: "aFieldPath",
    schema: {
      fieldA: new Field({
        fieldpath: "fieldA",
      }),
      fieldB: new Field({
        fieldpath: "fieldB",
      }),
    },
    deserializedDefault: [{ fieldA: "aDefaultValue" }],
  });

  describe("deserialize", () => {
    it("fills a __key attribute", () => {
      let serialized = {
        aFieldPath: [
          { fieldA: "A1", fieldB: "B1" },
          { fieldA: "A2", fieldB: "B2" },
        ],
      };

      let deserialized = schemaField.deserialize(serialized);

      deserialized.aFieldPath.forEach((o, i) => {
        expect(o.__key).toEqual(i);
      });
    });
  });

  describe("serialize", () => {
    it("deletes the __key attribute", () => {
      let deserialized = {
        aFieldPath: [
          { fieldA: "A1", fieldB: "B1", __key: 0 },
          { fieldA: "A2", fieldB: "B2", __key: 1 },
        ],
      };

      let serialized = schemaField.serialize(deserialized);

      serialized.aFieldPath.forEach((o) => {
        expect("__key" in o).toEqual(false);
      });
    });
  });
});
