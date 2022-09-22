// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { useState } from "react";
import { i18next } from "@translations/invenio_administration/i18next";
import CopyButton from "./CopyButton";
import { Table, Header, Dropdown, Grid } from "semantic-ui-react";
import { prefixes } from "./formats";

const prefixFormats = [
  {
    key: prefixes.DUBLIN_CORE,
    text: "OAI Dublin Core",
    value: prefixes.DUBLIN_CORE
  },
  {
    key: prefixes.OAI_DATACITE,
    text: "OAI DataCite",
    value: prefixes.OAI_DATACITE
  },
  {
    key: prefixes.DATACITE,
    text: "DataCite",
    value: prefixes.DATACITE
  }
]

function LinksTable({ data }) {
  const [links, setLinks] = useState(data.links);

  /**
   * Replaces the metadata prefix in the link.
   * Used to update links when the metadata prefix is changed.
   */
  const replaceLinkPrefix = (link, newPrefix) => {
    const oldPrefix = getPrefixFromLink(link);
    if (oldPrefix) {
      return link.replace(oldPrefix, newPrefix)
    }
    return link;
  };

  /**
   * Retrieves metadata prefix from a link.
   * Uses a regex to retrieve the prefix, matching "&metadataPrefix=...&".
   * Returns null if not found.
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
   * Dropdown's on change handler.
   * This method will update the following states if the new prefix is known:
   * - 'links', each link with its prefix replaced by the new prefix.
   */
  const prefixOnChange = (event, data) => {
    const newPrefix = data.value;
    if (Object.values(prefixes).includes(newPrefix)) {
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
  let defaultPrefix = getPrefixFromLink(listRecords)
  if (!Object.prototype.hasOwnProperty.call(prefixes, defaultPrefix)) {
    defaultPrefix = prefixes.DUBLIN_CORE;
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
              <Grid.Column width={13}>
                <span className="mr-10" basic>
                  { i18next.t("Format") }
                </span>
                <Dropdown
                  options={prefixFormats}
                  floating
                  button
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
                  <b>List records</b>
                </Table.Cell>
                <Table.Cell textAlign="left">
                  <a href={listRecords} target="_blank">
                    {listRecords}
                  </a>
                  <CopyButton text={listRecords} />
                </Table.Cell>
              </Table.Row>
              <Table.Row key="list-records">
                <Table.Cell width={3}>
                  <b>List identifiers</b>
                </Table.Cell>
                <Table.Cell textAlign="left">
                  <a href={listIdentifiers} target="_blank">
                    {listIdentifiers}
                  </a>
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
