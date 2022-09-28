// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { i18next } from "@translations/invenio_administration/i18next";
import CopyButton from "./CopyButton";
import { Table, Header, Dropdown, Grid } from "semantic-ui-react";
import { http } from "@js/invenio_administration/src/api/config.js";
import { capitalize } from "lodash";

/** Map of known formats and their name. */
const knownFormats = {
  oai_dc: "OAI Dublin Core",
  datacite: "DataCite",
  oai_datacite: "OAI DataCite",
};

function LinksTable({ data }) {
  const [links, setLinks] = useState(data.links);
  const [formats, setFormats] = useState([]);

  useEffect(() => {
    async function getFormats() {
      try {
        const response = await http.get("/api/oaipmh/formats");
        const formats = response.data?.hits?.hits;
        if (Array.isArray(formats) && formats.length > 0) {
          const serialized = formats.map((formt) => {
            return {
              key: formt.id,
              value: formt.id,
              text: knownFormats[formt.id] ?? formatKeyToName(formt.id),
            };
          });
          setFormats(serialized);
        }
      } catch (error) {
        console.error(error);
      }
    }
    getFormats();
  }, []);

  /**
   * Replaces the metadata prefix in the link.
   * Used to update links when the metadata prefix is changed.
   */
  const replaceLinkPrefix = (link, newPrefix) => {
    const oldPrefix = getPrefixFromLink(link);
    if (oldPrefix) {
      return link.replace(oldPrefix, newPrefix);
    }
    return link;
  };

  /**
   * Retrieves metadata prefix from a link.
   * Uses a regex to retrieve the prefix, matching "&metadataPrefix=...&".
   *
   * Returns null if pattern not found.
   */
  const getPrefixFromLink = (link) => {
    const prefixRegex = /\&metadataPrefix\=(.*)\&/;
    const match = link.match(prefixRegex);
    if (match && match.length) {
      const prefix = match[1];
      return prefix;
    }
    return null;
  };

  /**
   * Transforms a key into a readable name.
   * @example
   *  // returns Oai Datacite
   *  formateKeytoName('oai_datacite')
   */
  const formatKeyToName = (formatKey) => {
    const whiteSpaced = formatKey.replace("_", " ");
    const capitalised = capitalize(whiteSpaced);
    return capitalised;
  };

  /**
   * Dropdown's on change handler.
   * This method will update the following states if the new prefix is known:
   * - 'links', each link with its prefix replaced by the new prefix.
   */
  const prefixOnChange = (event, data) => {
    const newPrefix = data.value;
    if (formats.some((obj) => obj.key === newPrefix)) {
      const newLinks = {};
      Object.keys(links).map((key) => {
        let link = links[key];
        let newLink = replaceLinkPrefix(link, newPrefix);
        newLinks[key] = newLink;
      });
      setLinks(newLinks);
    }
  };

  const listRecords = links["oai-listrecords"];
  const listIdentifiers = links["oai-listidentifiers"];

  // Set default prefix based on backend link, use dublin core if unknown.
  let defaultPrefix = getPrefixFromLink(listRecords);
  if (!Object.prototype.hasOwnProperty.call(formats, defaultPrefix)) {
    defaultPrefix = "oai_dc";
  }

  return (
    <>
      {
        <>
          <Grid>
            <Grid.Row />
            <Grid.Row>
              <Grid.Column width={3}>
                <Header as="h2">{i18next.t("Links")}</Header>
              </Grid.Column>
              <Grid.Column width={13} textAlign="right">
                <span className="mr-10">{i18next.t("Format")}</span>
                <Dropdown
                  options={formats}
                  floating
                  selection
                  defaultValue={defaultPrefix}
                  onChange={prefixOnChange}
                />
              </Grid.Column>
            </Grid.Row>
          </Grid>
          <Table unstackable>
            <Table.Body>
              <Table.Row key="list-records">
                <Table.Cell width={3}>
                  <b>{i18next.t("List records")}</b>
                </Table.Cell>
                <Table.Cell width={10} textAlign="left">
                  <a
                    href={listRecords}
                    target="_blank"
                    title={i18next.t("Opens in new tab")}
                  >
                    {listRecords}
                  </a>
                </Table.Cell>
                <Table.Cell width={3} textAlign="right">
                  <CopyButton text={listRecords} />
                </Table.Cell>
              </Table.Row>
              <Table.Row key="list-identifiers">
                <Table.Cell width={3}>
                  <b>{i18next.t("List identifiers")}</b>
                </Table.Cell>
                <Table.Cell width={10} textAlign="left">
                  <a
                    href={listIdentifiers}
                    target="_blank"
                    title={i18next.t("Opens in new tab")}
                  >
                    {listIdentifiers}
                  </a>
                </Table.Cell>
                <Table.Cell width={3} textAlign="right">
                  <CopyButton text={listIdentifiers} />
                </Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
        </>
      }
    </>
  );
}

LinksTable.propTypes = {
  data: PropTypes.object.isRequired,
};

export default LinksTable;
