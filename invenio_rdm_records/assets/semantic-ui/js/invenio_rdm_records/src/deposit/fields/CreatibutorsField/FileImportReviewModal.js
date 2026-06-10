// This file is part of Invenio-RDM-Records
// Copyright (C) 2026 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Header, Icon, Message, Modal, Segment } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { validateCreatibutorEntry } from "./CreatibutorsModal";
import { CreatibutorsInlinePanel } from "./CreatibutorsDisplay/CreatibutorsInlinePanel";

const getCreatibutorSchemaLabel = (schema) =>
  schema === "contributors" ? i18next.t("contributors") : i18next.t("authors");

const CREATIBUTOR_IMPORT_EXAMPLE = `[
  {
    "person_or_org": {
      "type": "personal",
      "family_name": "Smith",
      "given_name": "Jane",
      "identifiers": [{ "scheme": "orcid", "identifier": "0000-0002-1825-0097" }]
    },
    "affiliations": [{ "name": "CERN" }]
  },
  {
    "person_or_org": {
      "type": "organizational",
      "name": "European Organization for Nuclear Research"
    }
  }
]`;

const parseCreatibutorFile = (text) => {
  // Only allow a file that is a JSON array of objects at the top-level
  let parsed;
  try {
    parsed = JSON.parse(text);
  } catch {
    return [];
  }
  if (!Array.isArray(parsed)) {
    return [];
  }
  // All entries must be non-null objects (not arrays or primitives)
  for (const entry of parsed) {
    if (typeof entry !== "object") {
      return [];
    }
  }
  return parsed;
};

export class FileImportReviewModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      phase: "pick",
      loading: false,
      fileName: null,
      validEntries: [],
      invalidEntries: [],
    };
    this.fileInputRef = React.createRef();
  }

  openModal = () => {
    this.setState({
      open: true,
      phase: "pick",
      loading: false,
      fileName: null,
      validEntries: [],
      invalidEntries: [],
    });
  };

  closeModal = () => {
    this.setState({ open: false });
  };

  resetToPickPhase = () => {
    this.setState({
      phase: "pick",
      validEntries: [],
      invalidEntries: [],
    });
  };

  triggerFileInput = () => {
    if (this.fileInputRef.current) {
      this.fileInputRef.current.value = null;
      this.fileInputRef.current.click();
    }
  };

  handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;
    this.setState({ loading: true });
    const reader = new FileReader();
    reader.onload = (e) => {
      this.classifyEntries(parseCreatibutorFile(e.target.result), file.name);
    };
    reader.onerror = () => {
      this.setState({ loading: false });
    };
    reader.readAsText(file);
  };

  classifyEntries = (rows, fileName) => {
    const { schema } = this.props;
    const validEntries = [];
    const invalidEntries = [];
    rows.forEach((raw) => {
      const error = validateCreatibutorEntry(raw, schema);
      if (error) {
        invalidEntries.push({ raw, reason: error });
      } else {
        validEntries.push(raw);
      }
    });
    this.setState({
      loading: false,
      fileName,
      validEntries,
      invalidEntries,
      phase: "review",
    });
  };

  localRemove = (index) => {
    this.setState((prev) => {
      const validEntries = [...prev.validEntries];
      validEntries.splice(index, 1);
      return { validEntries };
    });
  };

  localReplace = (index, newValue) => {
    this.setState((prev) => {
      const validEntries = [...prev.validEntries];
      validEntries[index] = newValue;
      return { validEntries };
    });
  };

  localMove = (from, to) => {
    this.setState((prev) => {
      const validEntries = [...prev.validEntries];
      const [item] = validEntries.splice(from, 1);
      validEntries.splice(to, 0, item);
      return { validEntries };
    });
  };

  handleConfirm = () => {
    const { onConfirm } = this.props;
    const { validEntries } = this.state;
    onConfirm(validEntries);
    this.closeModal();
  };

  renderPickPhase() {
    const { schema } = this.props;
    const { loading } = this.state;
    const type = getCreatibutorSchemaLabel(schema);

    const handleDragOver = (e) => {
      e.preventDefault();
      e.stopPropagation();
    };

    const handleDrop = (e) => {
      e.preventDefault();
      e.stopPropagation();
      if (loading) return;
      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        this.handleFileChange({
          target: { files },
        });
      }
    };

    return (
      <>
        <Segment
          placeholder
          textAlign="center"
          className="mt-0"
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          style={{ cursor: loading ? "not-allowed" : "pointer" }}
        >
          <Header icon>
            <Icon name="cloud upload" />
            {i18next.t("Upload {{type}} from file", { type })}
            <Header.Subheader>
              {i18next.t("Supported file types: .json, .txt")}
            </Header.Subheader>
          </Header>
          <Button
            primary
            type="button"
            loading={loading}
            disabled={loading}
            onClick={this.triggerFileInput}
          >
            <Icon name="folder open outline" />
            {i18next.t("Choose file")}
          </Button>
          <div style={{ marginTop: "1em", color: "#888" }}>
            {i18next.t("Or drag a file here")}
          </div>
          <input
            type="file"
            ref={this.fileInputRef}
            accept=".json,.txt"
            style={{ display: "none" }}
            onChange={this.handleFileChange}
          />
        </Segment>

        <Message info size="small" className="text-left mt-15">
          <Message.Header>{i18next.t("File format")}</Message.Header>
          <p>
            {i18next.t("Upload a JSON file containing a list of {{type}}.", { type })}
          </p>
          <pre className="creatibutors-import-example">
            {CREATIBUTOR_IMPORT_EXAMPLE}
          </pre>
        </Message>
      </>
    );
  }

  renderReviewPhase() {
    const {
      schema,
      roleOptions,
      autocompleteNames,
      addLabel,
      editLabel,
      serializeSuggestions,
      serializeCreatibutor,
      deserializeCreatibutor,
      scrollThreshold,
      batchSize,
    } = this.props;
    const { validEntries, invalidEntries, fileName } = this.state;
    const type = getCreatibutorSchemaLabel(schema);

    return (
      <>
        <Message size="small">
          <Icon name="file outline" />
          <strong>{fileName}</strong>
        </Message>
        {validEntries.length > 0 && (
          <>
            <Header as="h4" className="mb-10">
              {i18next.t("Valid {{type}} ({{count}})", {
                type,
                count: validEntries.length,
              })}
            </Header>

            <CreatibutorsInlinePanel
              list={validEntries}
              keyPrefix="fileImport"
              schema={schema}
              highlightOnAdd={false}
              roleOptions={roleOptions}
              addLabel={addLabel}
              editLabel={editLabel}
              autocompleteNames={autocompleteNames}
              serializeSuggestions={serializeSuggestions}
              serializeCreatibutor={serializeCreatibutor}
              deserializeCreatibutor={deserializeCreatibutor}
              removeCreatibutor={this.localRemove}
              replaceCreatibutor={this.localReplace}
              moveCreatibutor={this.localMove}
              scrollThreshold={scrollThreshold}
              batchSize={batchSize}
            />
          </>
        )}

        {invalidEntries.length > 0 && (
          <Message error size="small">
            <Message.Header>
              <Icon name="exclamation triangle" />
              {i18next.t("{{count}} entries could not be imported", {
                count: invalidEntries.length,
              })}
            </Message.Header>
            <Message.List numbered>
              {invalidEntries.map((inv, idx) => {
                const preview =
                  typeof inv.raw === "string" ? inv.raw : JSON.stringify(inv.raw);
                return (
                  <Message.Item key={idx}>
                    <code>{preview}</code> {inv.reason}
                  </Message.Item>
                );
              })}
            </Message.List>
          </Message>
        )}

        {validEntries.length === 0 && invalidEntries.length === 0 && (
          <Message info size="small">
            <Icon name="info circle" />
            {i18next.t("The file appears to be empty or contains invalid data.")}
          </Message>
        )}
      </>
    );
  }

  render() {
    const { trigger, schema } = this.props;
    const { open, phase, validEntries } = this.state;
    const type = getCreatibutorSchemaLabel(schema);

    const headerText =
      phase === "pick"
        ? i18next.t("Add {{type}} from file", { type })
        : i18next.t("Review {{type}} from file", { type });

    return (
      <Modal
        onOpen={this.openModal}
        open={open}
        onClose={this.closeModal}
        trigger={trigger}
        size="large"
        closeOnDimmerClick={false}
        closeIcon
      >
        <Modal.Header as="h2" className="pt-10 pb-10">
          {headerText}
        </Modal.Header>

        <Modal.Content scrolling>
          {phase === "pick" ? this.renderPickPhase() : this.renderReviewPhase()}
        </Modal.Content>

        <Modal.Actions>
          {phase === "review" && (
            <Button
              floated="left"
              type="button"
              icon="arrow left"
              content={i18next.t("Choose a different file")}
              onClick={this.resetToPickPhase}
            />
          )}
          <Button icon="close" type="button" onClick={this.closeModal}>
            {i18next.t("Cancel")}
          </Button>
          {phase === "review" && (
            <Button
              positive
              type="button"
              icon="check"
              disabled={validEntries.length === 0}
              content={i18next.t("Import {{count}} {{type}}", {
                count: validEntries.length,
                type,
              })}
              onClick={this.handleConfirm}
            />
          )}
        </Modal.Actions>
      </Modal>
    );
  }
}

FileImportReviewModal.propTypes = {
  trigger: PropTypes.node.isRequired,
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  scrollThreshold: PropTypes.number,
  batchSize: PropTypes.number,
  onConfirm: PropTypes.func.isRequired,
  roleOptions: PropTypes.array.isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  addLabel: PropTypes.node,
  editLabel: PropTypes.node,
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
};

FileImportReviewModal.defaultProps = {
  scrollThreshold: 10,
  batchSize: 20,
  autocompleteNames: "search",
  addLabel: undefined,
  editLabel: undefined,
  serializeSuggestions: undefined,
  serializeCreatibutor: undefined,
  deserializeCreatibutor: undefined,
};
