/*
 * SPDX-FileCopyrightText: 2022-2025 CERN.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { Component } from "react";
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
  oai_dcat: "OAI DCAT-AP",
};

function LinksTable({data}) {
  const [links, setLinks] = React.useState(passedLinks || []);
  const [formats, setFormats] = React.useState([]);
  const [currentFormat, setCurrentFormat] = React.useState(currentPrefix ?? "oai_dc");
  const [error, setError] = React.useState(undefined);
  React.useEffect(() => {
    fetchFormats();
  }, []);

  const fetchFormats = () => {
    const cancellableFetchFormats = withCancel(http.get("/api/oaipmh/formats"));

    try {
      const response = await cancellableFetchFormats.promise;

      const formats = response.data?.hits?.hits;

      if (!_isEmpty(formats)) {
        const serialized = formats.map((formt) => ({
          key: formt.id,
          value: formt.id,
          text: knownFormats[formt.id] ?? formatKeyToName(formt.id),
        }));

        setFormats(serialized);
      }
    } catch (error) {
      console.error(error);

      setError({
          header: i18next.t("Fetch error"),
          content: i18next.t("Error fetching OAI set formats."),
          id: error.code,
        });
    }
  };

  const replaceLinkPrefix = (link, newPrefix) => {
    if (_isEmpty(link)) return null;

    const prefixParam = "metadataPrefix";
    const url = new URL(link);
    const params = url.searchParams;

    if (params.has(prefixParam)) {
      params.set(prefixParam, newPrefix);
    }

    return url.toString();
  };

  const getPrefixFromLink = (link) => {
    if (_isEmpty(link)) return null;
    const prefixParam = "metadataPrefix";
    const url = new URL(link);
    const prefix = url.searchParams.get(prefixParam);

    return prefix || null;
  };

  const formatKeyToName = (formatKey) => {
    const whiteSpaced = formatKey.replace("_", " ");
    return capitalize(whiteSpaced);
  };

  const prefixOnChange = (event, data) => {
    const newFormat = data.value;
    const { formats, links } = this.state;

    if (formats.some((obj) => obj.key === newFormat)) {
      const newLinks = {};
      Object.keys(links).forEach((key) => {
        const link = links[key];
        newLinks[key] = replaceLinkPrefix(link, newFormat);
      });
      this.setState({ links: newLinks, currentFormat: newFormat });
    }
  };

  const resetErrorState = () => {
    setError(undefined);
  };

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
                  rel="noreferrer"
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
                  rel="noreferrer"
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
          <ErrorMessage {...error} removeNotification={resetErrorState} />
        )}
      </>
    );
}

LinksTable.propTypes = {
  data: PropTypes.object.isRequired,
};

export default LinksTable;
