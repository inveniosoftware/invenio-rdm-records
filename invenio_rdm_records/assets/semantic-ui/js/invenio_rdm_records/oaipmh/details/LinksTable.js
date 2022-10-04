// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import { i18next } from "@translations/invenio_administration/i18next";
import CopyButton from "./CopyButton";
import { Table, Header, Dropdown, Grid } from "semantic-ui-react";
import { http } from "@js/invenio_administration/src/api/config.js";
import { capitalize, isEmpty } from "lodash";
import { ErrorMessage } from "@js/invenio_administration/src/ui_messages/messages";

/** Map of known formats and their name. */
const knownFormats = {
  "oai_dc": "OAI Dublin Core",
  "datacite": "DataCite",
  "oai_datacite": "OAI DataCite",
}

class LinksTable extends Component {
  constructor(props) {
    super(props);
    const { links: passedLinks } = props.data;

    let defaultPrefix = this.getPrefixFromLink(passedLinks["oai-listrecords"] || []);
    const isPrefixKnown = Object.prototype.hasOwnProperty.call(knownFormats, defaultPrefix);
    if (!isPrefixKnown) {
      defaultPrefix = 'oai_dc';
    }

    this.state = {
      links: passedLinks || [],
      formats: [],
      currentFormat: defaultPrefix,
      error: undefined,
    }
  }

  async componentDidMount() {
    try {
      const response = await http.get(
        '/api/oaipmh/formats'
      );
      const formats = response.data?.hits?.hits;
      if (Array.isArray(formats) && formats.length > 0) {
        const serialized = formats.map((formt) => {
          return {
            key: formt.id,
            value: formt.id,
            text: knownFormats[formt.id] ?? this.formatKeyToName(formt.id)
          }
        });
        this.setState({
          formats: serialized
        });
      }
    } catch (error) {
      console.error(error);

      this.setState({
        error: { header: "Fetch error", content: "Error fetching OAI set formats.", id: error.code },
      });
    }
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
    if (!link)
      return null;
    const prefixParam = 'metadataPrefix';
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
    const capitalised = capitalize(whiteSpaced);
    return capitalised;
  };

  /**
   * Dropdown's on change handler.
   * This method will update the following states if the new prefix is known:
   * - 'links', each link with its prefix replaced by the new prefix.
   */
  prefixOnChange = (event, data) => {
    const newFormat = data.value;
    const { formats, links } = this.state;

    if (formats.some(obj => obj.key === newFormat)) {
      const newLinks = {};
      Object.keys(links).map((key) => {
        let link = links[key];
        let newLink = this.replaceLinkPrefix(link, newFormat);
        newLinks[key] = newLink;
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
        {
          <>
            <Grid>
              <Grid.Row />
              <Grid.Row>
                <Grid.Column width={3}>
                  <Header as="h2">{i18next.t("Links")}</Header>
                </Grid.Column>
                <Grid.Column width={13} textAlign="right">
                  <span className="mr-10" basic>
                    {i18next.t("Format")}
                  </span>
                  <Dropdown
                    options={formats}
                    floating
                    selection
                    defaultValue={currentFormat}
                    selectOnNavigaion={false}
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
                    <a href={listRecords} target="_blank" title={i18next.t("Opens in new tab")}>
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
                    <a href={listIdentifiers} target="_blank" title={i18next.t("Opens in new tab")}>
                      {listIdentifiers}
                    </a>
                  </Table.Cell>
                  <Table.Cell width={3} textAlign="right">
                    <CopyButton text={listIdentifiers} />
                  </Table.Cell>
                </Table.Row>
              </Table.Body>
            </Table>
            {!isEmpty(error) && (
              <ErrorMessage {...error} removeNotification={this.resetErrorState} />
            )}
          </>
        }
      </>
    );
  }
}

LinksTable.propTypes = {
  data: PropTypes.object.isRequired,
};

export default LinksTable;
