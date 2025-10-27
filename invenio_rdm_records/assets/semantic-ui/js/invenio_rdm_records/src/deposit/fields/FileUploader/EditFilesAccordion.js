// This file is part of Invenio-RDM-Records
// Copyright (C) 2025 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Trans } from "react-i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Accordion, Grid, Icon, Message } from "semantic-ui-react";
import { NewVersionButton } from "../../controls/NewVersionButton";
import { FileModification } from "./FileModification/FileModification";

export class EditFilesAccordion extends Component {
  state = { activeIndex: -1 };

  handleClick = (e, titleProps) => {
    const { index } = titleProps;
    const { activeIndex } = this.state;
    const newIndex = activeIndex === index ? -1 : index;

    this.setState({ activeIndex: newIndex });
  };

  render() {
    const { record, permissions, fileModification } = this.props;
    const { activeIndex } = this.state;
    return (
      <Message info>
        <Accordion className="m-0">
          <Accordion.Title
            className="ui"
            active={activeIndex === 0}
            index={0}
            onClick={this.handleClick}
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                this.handleClick(e, { index: 0 });
              }
            }}
          >
            <Icon name="angle right" className="mr-5" />
            <strong>Edit files</strong>
          </Accordion.Title>
          <Accordion.Content active={activeIndex === 0}>
            <Grid columns={2} verticalAlign="middle" padded="vertically">
              <Grid.Row className="p-0">
                <Grid.Column width={12}>
                  <p className="mt-5 display-inline-block">
                    <Trans>
                      To <strong>add, modify or remove files</strong>, it is recommended
                      that you create a new version. A new record is created which
                      tracks the evolution of your work.
                    </Trans>
                  </p>
                </Grid.Column>
                <Grid.Column width={4} className="right aligned">
                  <NewVersionButton
                    record={record}
                    onError={() => {}}
                    disabled={!permissions.can_new_version}
                  />
                </Grid.Column>
              </Grid.Row>
              <Grid.Row className="p-0">
                <Grid.Column width={12}>
                  <p className="mt-5 display-inline-block">
                    <Trans>
                      To <strong>correct</strong> minor errors, you can unlock the
                      files.
                    </Trans>
                  </p>
                </Grid.Column>

                <Grid.Column width={4} className="right aligned">
                  <FileModification
                    record={record}
                    permissions={permissions}
                    fileModification={fileModification}
                    disabled={false}
                  />
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Accordion.Content>
        </Accordion>
      </Message>
    );
  }
}

EditFilesAccordion.propTypes = {
  record: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
  fileModification: PropTypes.object,
};

EditFilesAccordion.defaultProps = {
  fileModification: {},
};
