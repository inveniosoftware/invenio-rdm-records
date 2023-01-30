// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import CopyButton from "./CopyButton";
import { Table, Header, Dropdown, Grid } from "semantic-ui-react";
import { ErrorMessage } from "@js/invenio_administration";
import { withCancel } from "react-invenio-forms";
import _isEmpty from "lodash/isEmpty";
import { http } from "react-invenio-forms";
import { capitalize } from "lodash";

/** Map of known formats and their name. */
const knownFormats = {
  oai_dc: "OAI Dublin Core",
  datacite: "DataCite",
  oai_datacite: "OAI DataCite",
  oai_marcxml: "OAI MARCXML",
};

class LinksTable extends Component {
  constructor(props) {
    super(props);
    const { links: passedLinks } = props.data;

    const currentPrefix = this.getPrefixFromLink(
      passedLinks["oai-listrecords"]
    );

    this.state = {
      links: passedLinks || [],
      formats: [],
      currentFormat: currentPrefix ?? "oai_dc",
      error: undefined,
    };
  }

  fetchFormats = async () => {
    const cancellableFetchFormats = withCancel(http.get("/api/oaipmh/formats"));

    try {
      const response = await cancellableFetchFormats.promise;

      const formats = response.data?.hits?.hits;

      if (!_isEmpty(formats)) {
        const serialized = formats.map((formt) => ({
          key: formt.id,
          value: formt.id,
          text: knownFormats[formt.id] ?? this.formatKeyToName(formt.id),
        }));

        this.setState({
          formats: serialized,
        });
      }
    } catch (error) {
      console.error(error);

      this.setState({
        error: {
          header: i18next.t("Fetch error"),
          content: i18next.t("Error fetching OAI set formats."),
          id: error.code,
        },
      });
    }
  };

  componentDidMount() {
    this.fetchFormats();
  }

  /**
   * Replaces the metadata prefix in the link.
   * Used to update links when the metadata prefix is changed.
   */
  replaceLinkPrefix = (link, newPrefix) => {
    const oldPrefix = this.getPrefixFromLink(link);
    if (oldPrefix) {
      return link.replace(oldPrefix, newPrefix);
    }
    return link;
  };

  /**
   * Retrieves metadata prefix from a link.
   *
   * Returns null if parameter not found.
   */
  getPrefixFromLink = (link) => {
    if (_isEmpty(link)) return null;
    const prefixParam = "metadataPrefix";
    const params = new URLSearchParams(link);
    const prefix = params.get(prefixParam);

    return prefix || null;
  };

  /**
   * Transforms a key into a readable name.
   * @example
   *  // returns Oai Datacite
   *  formateKeytoName('oai_datacite')
   */
  formatKeyToName = (formatKey) => {
    const whiteSpaced = formatKey.replace("_", " ");
    return capitalize(whiteSpaced);
  };

  /**
   * Dropdown's on change handler.
   * This method will update the following states if the new prefix is known:
   * - 'links', each link with its prefix replaced by the new prefix.
   */
  prefixOnChange = (event, data) => {
    const newFormat = data.value;
    const { formats, links } = this.state;

    if (formats.some((obj) => obj.key === newFormat)) {
      const newLinks = {};
      Object.keys(links).map((key) => {
        const link = links[key];
        newLinks[key] = this.replaceLinkPrefix(link, newFormat);
      });
      this.setState({ links: newLinks, currentFormat: newFormat });
    }
  };

  resetErrorState = () => {
    this.setState({ error: undefined });
  };

  render() {
    const { links, formats, error, currentFormat } = this.state;
    const listRecords = links["oai-listrecords"];
    const listIdentifiers = links["oai-listidentifiers"];

    return (
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
                defaultValue={currentFormat}
                selectOnNavigation={false}
                onChange={this.prefixOnChange}
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
        {!_isEmpty(error) && (
          <ErrorMessage {...error} removeNotification={this.resetErrorState} />
        )}
      </>
    );
  }
}

LinksTable.propTypes = {
  data: PropTypes.object.isRequired,
};

export default LinksTable;
