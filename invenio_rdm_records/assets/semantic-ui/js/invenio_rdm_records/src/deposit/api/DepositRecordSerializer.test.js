// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { RDMDepositRecordSerializer } from "./DepositRecordSerializer";
import { emptyDate } from "../fields/DatesField/initialValues";
import { emptyIdentifier } from "../fields/Identifiers/initialValues";
import { emptyRelatedWork } from "../fields/RelatedWorksField/initialValues";
import { emptyReference } from "../fields/ReferencesField/initialValues";

describe("RDMDepositRecordSerializer tests", () => {
  const defaultLocale = "en";
  const serializer = new RDMDepositRecordSerializer(defaultLocale);

  describe("removeEmptyValues", () => {
    const record = {
      contributors: [{ identifiers: [] }],
      version: 0,
      cool: false,
      creators: [null, undefined, {}],
      description: "",
    };

    const cleanedRecord = serializer._removeEmptyValues(record);

    expect(cleanedRecord).toEqual({ cool: false, version: 0 });
  });

  describe("serialize", () => {
    describe("dates", () => {
      it("serializes array as-is if filled", () => {
        const record = {
          metadata: {
            dates: [
              {
                date: "2020/08",
                type: "accepted",
                description: "bar",
              },
            ],
          },
        };

        const serializedRecord = serializer.serialize(record);

        expect(serializedRecord.metadata.dates).toEqual([
          {
            date: "2020/08",
            type: { id: "accepted" },
            description: "bar",
          },
        ]);
      });

      it("doesn't serialize if only default is present", () => {
        const record = {
          metadata: {
            dates: [emptyDate],
          },
        };

        const serializedRecord = serializer.serialize(record);

        expect(serializedRecord).toEqual({ metadata: {}, custom_fields: {}, pids: {} });
      });
    });

    describe("alternate identifiers", () => {
      it("serializes array as-is if filled", () => {
        const record = {
          metadata: {
            identifiers: [{ scheme: "doi", identifier: "10.5281/zenodo.9999999" }],
          },
        };

        const serializedRecord = serializer.serialize(record);

        expect(serializedRecord.metadata.identifiers).toEqual([
          {
            scheme: "doi",
            identifier: "10.5281/zenodo.9999999",
          },
        ]);
      });

      it("doesn't serialize if only default is present", () => {
        const record = {
          metadata: {
            identifiers: [emptyIdentifier],
          },
        };

        const serializedRecord = serializer.serialize(record);

        expect(serializedRecord).toEqual({ metadata: {}, custom_fields: {}, pids: {} });
      });
    });

    describe("related identifiers", () => {
      it("serializes array as-is if filled", () => {
        const record = {
          metadata: {
            related_identifiers: [
              {
                scheme: "doi",
                identifier: "10.5281/zenodo.9999988",
                resource_type: "image-photo",
                relation_type: "requires",
              },
            ],
          },
        };

        const serializedRecord = serializer.serialize(record);

        expect(serializedRecord.metadata.related_identifiers).toEqual([
          {
            scheme: "doi",
            identifier: "10.5281/zenodo.9999988",
            resource_type: { id: "image-photo" },
            relation_type: { id: "requires" },
          },
        ]);
      });

      it("doesn't serialize if only default is present", () => {
        const record = {
          metadata: {
            related_identifiers: [emptyRelatedWork],
          },
        };

        const serializedRecord = serializer.serialize(record);

        expect(serializedRecord).toEqual({ metadata: {}, custom_fields: {}, pids: {} });
      });
    });

    describe("references", () => {
      it("serializes array as-is if filled", () => {
        const record = {
          metadata: {
            references: [
              {
                reference: "Test reference",
              },
            ],
          },
        };

        const serializedRecord = serializer.serialize(record);

        expect(serializedRecord.metadata.references).toEqual([
          {
            reference: "Test reference",
          },
        ]);
      });

      it("doesn't serialize if only default is present", () => {
        const record = {
          metadata: {
            references: [emptyReference],
          },
        };

        const serializedRecord = serializer.serialize(record);

        expect(serializedRecord).toEqual({ metadata: {}, custom_fields: {}, pids: {} });
      });
    });
  });

  describe("deserialize", () => {
    it("fills empty values with predefined values", () => {
      const record = {
        access: {},
        metadata: {
          title: null,
        },
      };
      const expectedRecord = {
        expanded: {},
        metadata: {
          title: "",
          additional_titles: [],
          additional_descriptions: [],
          creators: [],
          contributors: [],
          resource_type: "",
          publication_date: "",
          dates: [],
          languages: [],
          identifiers: [],
          related_identifiers: [],
          references: [],
          subjects: [],
          rights: [],
          funding: [],
          version: "",
        },
        access: {
          record: "public",
          files: "public",
        },
        pids: {},
      };

      const deserializedRecord = serializer.deserialize(record);

      expect(deserializedRecord).toEqual(expectedRecord);
    });

    it("deserializes a full record", () => {
      const record = {
        access: {
          access_right: "open",
          files: false,
          metadata: false,
        },
        conceptid: "nz13t-me993",
        created: "2020-10-28 18:35:58.113520",
        expires_at: "2020-10-28 18:35:58.113692",
        id: "wk205-00878",
        links: {
          publish:
            "https://127.0.0.1:5000/api/records/wk205-00878/draft/actions/publish",
          self: "https://127.0.0.1:5000/api/records/wk205-00878/draft",
          self_html: "https://127.0.0.1:5000/uploads/wk205-00878",
        },
        pids: {
          doi: {
            identifier: "10.1234/rec.nz13t-me993",
            provider: "datacite",
            client: "rdm",
          },
        },
        metadata: {
          contributors: [
            {
              person_or_org: {
                name: "Jane Smith",
                type: "personal",
                identifiers: [
                  {
                    identifier: "0000-0002-1825-0097",
                    scheme: "orcid",
                  },
                ],
              },
              role: { id: "datacurator" },
            },
          ],
          creators: [
            {
              person_or_org: { name: "John Doe", type: "personal" },
              affiliations: [
                {
                  id: "01ggx4157",
                  name: "CERN",
                },
              ],
            },
          ],
          publication_date: "2020-09-28",
          resource_type: { id: "lesson" },
          title: "Test 2020-1028 13:34",
          additional_titles: [
            {
              title: "Another title",
              type: { title: "Abstract", id: "abstract" },
              lang: { title: "Danish", id: "dan" },
            },
          ],
          additional_descriptions: [
            {
              description: "Another description",
              type: { title: "Other", id: "other" },
              lang: { title: "Danish", id: "dan" },
            },
          ],
          dates: [
            {
              date: "1920/2020",
              type: { id: "collected" },
              description: "foo",
            },
          ],
          languages: [
            { title: "en", id: "en_id" },
            { title: "fr", id: "fr_id" },
          ],
          identifiers: [{ scheme: "doi", identifier: "10.5281/zenodo.9999999" }],
          rights: [
            {
              id: "id_cc_4.0",
            },
            {
              title: {
                en: "A custom license",
              },
              description: {
                en: "A custom description",
              },
              link: "https://customlicense.com",
            },
          ],
          related_identifiers: [
            {
              scheme: "doi",
              identifier: "10.5281/zenodo.9999988",
              resource_type: { id: "image-photo" },
              relation_type: "requires",
            },
          ],
          references: [
            {
              reference: "Test reference",
            },
          ],
          subjects: [
            {
              subject: "MeSH: Cognitive Neuroscience",
              id: "mesh_1",
            },
          ],
          funding: [
            {
              funder: {
                name: "Funder 2",
              },
              award: {
                title: {
                  en: "Award B2",
                },
                number: "B21234",
                identifiers: [
                  {
                    identifier: "https://inveniosoftware.org/products/rdm/",
                    scheme: "url",
                  },
                ],
              },
            },
            {
              funder: {
                name: "Funder 3",
              },
            },
          ],
          version: "v2.0.0",
        },
        revision_id: 1,
        ui: {
          publication_date_l10n: "Sep 28, 2020",
        },
        updated: "2020-10-28 18:35:58.125222",
      };

      const deserializedRecord = serializer.deserialize(record);

      const expectedRecord = {
        access: {
          access_right: "open",
          files: false,
          metadata: false,
        },
        expanded: {},
        id: "wk205-00878",
        links: {
          publish:
            "https://127.0.0.1:5000/api/records/wk205-00878/draft/actions/publish",
          self: "https://127.0.0.1:5000/api/records/wk205-00878/draft",
          self_html: "https://127.0.0.1:5000/uploads/wk205-00878",
        },
        pids: {
          doi: {
            identifier: "10.1234/rec.nz13t-me993",
            provider: "datacite",
            client: "rdm",
          },
        },
        metadata: {
          contributors: [
            {
              affiliations: [],
              person_or_org: {
                name: "Jane Smith",
                type: "personal",
                identifiers: [
                  {
                    identifier: "0000-0002-1825-0097",
                    scheme: "orcid",
                  },
                ],
              },
              role: "datacurator",
              __key: 0,
            },
          ],
          creators: [
            {
              affiliations: [
                {
                  id: "01ggx4157",
                  name: "CERN",
                },
              ],
              person_or_org: {
                name: "John Doe",
                type: "personal",
              },
              role: "",
              __key: 0,
            },
          ],
          publication_date: "2020-09-28",
          resource_type: "lesson",
          title: "Test 2020-1028 13:34",
          additional_titles: [
            { title: "Another title", type: "abstract", lang: "dan", __key: 0 },
          ],
          additional_descriptions: [
            {
              description: "Another description",
              type: "other",
              lang: "dan",
              __key: 0,
            },
          ],
          dates: [
            {
              date: "1920/2020",
              type: "collected",
              description: "foo",
              __key: 0,
            },
          ],
          languages: ["en_id", "fr_id"],
          identifiers: [
            { scheme: "doi", identifier: "10.5281/zenodo.9999999", __key: 0 },
          ],
          related_identifiers: [
            {
              scheme: "doi",
              identifier: "10.5281/zenodo.9999988",
              resource_type: "image-photo",
              relation_type: "requires",
              __key: 0,
            },
          ],
          references: [
            {
              reference: "Test reference",
              __key: 0,
            },
          ],
          subjects: [
            {
              id: "mesh_1",
              subject: "MeSH: Cognitive Neuroscience",
            },
          ],
          rights: [
            {
              id: "id_cc_4.0",
            },
            {
              title: "A custom license",
              description: "A custom description",
              link: "https://customlicense.com",
            },
          ],
          funding: [
            {
              funder: {
                name: "Funder 2",
              },
              award: {
                title: "Award B2",
                number: "B21234",
                url: "https://inveniosoftware.org/products/rdm/",
              },
              __key: 0,
            },
            {
              funder: {
                name: "Funder 3",
              },
              award: {},
              __key: 1,
            },
          ],
          version: "v2.0.0",
        },
        ui: {
          publication_date_l10n: "Sep 28, 2020",
        },
      };
      expect(deserializedRecord).toEqual(expectedRecord);
    });
  });
});
