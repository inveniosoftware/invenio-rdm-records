// This file is part of Invenio-RDM-Records
// Copyright (C) 2026 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import {
  Header,
  Grid,
  Label,
  Progress,
  Table,
  Container,
  Message,
} from "semantic-ui-react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export default function StorageOverview({ storage }) {
  const statusColor = {
    Draft: "warning",
    Published: "positive",
  };

  return (
    <Container aria-label={i18next.t("Storage")} className="storage-overview">
      <Header as="h5" className="mb-2">
        <strong>{i18next.t("Quota overview")}</strong>
      </Header>
      <p className="text-muted mb-4">
        {i18next.t(
          "You can now manage your record storage by assigning additional quota as needed."
        )}{" "}
        <a href="./">{i18next.t("Find out more.")}</a>{" "}
        {/* Need to link to help guide.*/}
      </p>

      <Grid doubling columns={3} stackable className="rel-mb-1">
        <Grid.Column>
          <Message
            icon="hdd"
            size="tiny"
            header={<Header as="h4">{storage.default_quota} GB</Header>}
            content={i18next.t("Default quota per record")}
            className="rel-p-2"
          />
        </Grid.Column>

        <Grid.Column>
          <Message
            icon="server"
            size="tiny"
            positive={storage.additional_available_quota > 5}
            warning={storage.additional_available_quota < 5}
            header={<Header as="h4">{storage.additional_available_quota} GB</Header>}
            content={i18next.t("Available of {{total}} GB allowance", {
              total: storage.total_allowed_quota,
            })}
            className="rel-p-2"
          />
        </Grid.Column>

        <Grid.Column>
          <Message
            icon="sitemap"
            size="tiny"
            info
            header={<Header as="h4">{storage.additional_granted_quota} GB</Header>}
            content={i18next.t("Quota granted across {{count}} records", {
              count: storage.records.length,
            })}
            className="rel-p-2"
          />
        </Grid.Column>
      </Grid>

      <div className="mb-4">
        <Grid>
          <Grid.Row columns={2}>
            <Grid.Column textAlign="left">
              <Label className="medium rel-mb-1">0 GB</Label>
            </Grid.Column>
            <Grid.Column textAlign="right">
              <Label className="medium  rel-mb-1">
                {storage.total_allowed_quota} GB
              </Label>
            </Grid.Column>
          </Grid.Row>
        </Grid>
        <Progress
          value={storage.additional_used_quota}
          total={storage.total_allowed_quota}
          progress="value"
          className="primary"
        />
      </div>

      {/* Storage Allocations Table */}
      <Header as="h5" className="mb-2">
        <strong>{i18next.t("Allocated storage")}</strong>
      </Header>
      {storage.records.length > 0 ? (
        <Table size="small" padded>
          <Table.Header>
            <Table.Row>
              <Table.HeaderCell width={7}>{i18next.t("Record")}</Table.HeaderCell>
              <Table.HeaderCell width={2}>
                {i18next.t("Additional quota")}
              </Table.HeaderCell>
              <Table.HeaderCell width={4}>{i18next.t("Usage")}</Table.HeaderCell>
              <Table.HeaderCell width={2}>{i18next.t("Date")}</Table.HeaderCell>
              <Table.HeaderCell width={1}>{i18next.t("Status")}</Table.HeaderCell>
            </Table.Row>
          </Table.Header>

          <Table.Body className="storage-overview-table">
            {storage.records.map((record, idx) => {
              const percent =
                record.total > 0 ? Math.round((record.used / record.total) * 100) : 0;

              return (
                <Table.Row key={idx}>
                  <Table.Cell>
                    <a href={record.url}>{record.title}</a>
                    <p className="text-muted">{record.url}</p>
                  </Table.Cell>

                  <Table.Cell>
                    <strong>+{record.additional_quota} GB</strong>
                    <div className="ui tiny text-muted">
                      (
                      {i18next.t("{{total}} GB total", {
                        total: record.total,
                      })}
                      )
                    </div>
                  </Table.Cell>

                  <Table.Cell>
                    <Grid verticalAlign="middle" columns="equal">
                      <Grid.Column width={9}>
                        <Progress
                          value={record.used}
                          total={record.total}
                          className="m-0 primary"
                          size="tiny"
                        />
                      </Grid.Column>
                      <Grid.Column width={7} textAlign="left">
                        <p className="text-muted">
                          {record.used} / {record.total} GB
                        </p>
                      </Grid.Column>
                    </Grid>
                    <p className="text-muted">
                      {percent}% {i18next.t("used")}
                    </p>
                  </Table.Cell>

                  <Table.Cell>
                    <p className="text-muted">{record.date}</p>
                  </Table.Cell>

                  <Table.Cell>
                    <Label size="tiny" color={statusColor[record.status] || "grey"}>
                      {i18next.t(record.status)}
                    </Label>
                  </Table.Cell>
                </Table.Row>
              );
            })}
          </Table.Body>
        </Table>
      ) : (
        <Message icon size="small">
          <i className="archive icon" />
          <Message.Content>
            <Message.Header>{i18next.t("No allocated storage")}</Message.Header>
            <p>
              {i18next.t("No records have been granted any additional quotas yet.")}
            </p>
          </Message.Content>
        </Message>
      )}
    </Container>
  );
}

StorageOverview.propTypes = {
  storage: PropTypes.shape({
    default_quota: PropTypes.number.isRequired,
    total_allowed_quota: PropTypes.number.isRequired,
    additional_granted_quota: PropTypes.number.isRequired,
    additional_available_quota: PropTypes.number.isRequired,
    additional_used_quota: PropTypes.number.isRequired,
    records: PropTypes.arrayOf(
      PropTypes.shape({
        title: PropTypes.string.isRequired,
        url: PropTypes.string.isRequired,
        additional_quota: PropTypes.number.isRequired,
        total: PropTypes.number.isRequired,
        used: PropTypes.number.isRequired,
        date: PropTypes.string.isRequired,
        status: PropTypes.string.isRequired,
      })
    ),
  }).isRequired,
};
