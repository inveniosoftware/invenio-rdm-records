// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React from "react";
import { i18next } from "@translations/invenio_administration/i18next";
import CopyButton from "./CopyButton";
import { Table, Header } from "semantic-ui-react";

function LinksTable({ data }) {
  /**
   * WIP: this method should remove metadataPrefix from the url once the attribute is listed
   * as a dropdown.
   *
   * @param {string} url
   * @returns {string} stripped url
   */
  const sanitizeLink = (url) => {
    return url;
  };

  const { links } = data;
  const listRecords = sanitizeLink(links["oai-listrecords"]);
  const listIdentifiers = sanitizeLink(links["oai-listidentifiers"]);

  return (
    <>
      {
        <>
          <Header as="h2">{i18next.t("Links")}</Header>
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
