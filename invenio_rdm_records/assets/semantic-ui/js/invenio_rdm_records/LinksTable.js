// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { useContext } from "react";
import { i18next } from "@translations/invenio_administration/i18next";
import CopyButton from "./CopyButton";
import { Table, Header, Grid } from "semantic-ui-react";
import AdminDetailsContext from "@js/invenio_administration/details/AdminDetailsContext.js";

function LinksTable({ }) {

  /**
   * WIP: this method should remove metadataPrefix from the url once the attribute is listed
   * as a dropdown.
   *
   * @param {string} url
   * @returns {string} stripped url
   */
  const sanitizeLink = (url) => {
    return url;
  }

  const ctx = useContext(AdminDetailsContext);
  const data = ctx.data;
  const links = data.links;
  const pidValue = data.id;

  let linkElems = [];

  Object.entries(links).forEach(([key, link]) => {
    link = sanitizeLink(link, pidValue);

    if (key !== "self") {
      linkElems.push(
        <Table.Row key={key}>
          <Table.Cell>
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
            <Table.Body>
              {linkElems}
            </Table.Body>
          </Table>
        </>
      )}
    </>
  );
}

LinksTable.propTypes = {
  data: PropTypes.object.isRequired,
  columns: PropTypes.array.isRequired,
};


export default LinksTable;
