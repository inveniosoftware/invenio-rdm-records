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

  const { links, id: pidValue } = data;

  const linkElems = [];

  Object.entries(links).forEach(([key, link]) => {
    link = sanitizeLink(link, pidValue);

    if (key !== "self") {
      linkElems.push(
        <Table.Row key={key}>
          <Table.Cell width={3}>
            <b>{key}</b>
          </Table.Cell>
          <Table.Cell textAlign="left">
            {link}
            <CopyButton text={link} />
          </Table.Cell>
        </Table.Row>
      );
    }
  });

  return (
    <>
      {linkElems && (
        <>
          <Header as="h2">{i18next.t("Links")}</Header>
          <Table unstackable>
            <Table.Body>{linkElems}</Table.Body>
          </Table>
        </>
      )}
    </>
  );
}

LinksTable.propTypes = {
  data: PropTypes.object.isRequired,
};

export default LinksTable;
