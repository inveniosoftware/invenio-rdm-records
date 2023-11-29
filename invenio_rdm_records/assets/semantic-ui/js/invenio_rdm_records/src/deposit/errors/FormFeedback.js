// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import _get from "lodash/get";
import _isObject from "lodash/isObject";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Grid, Message } from "semantic-ui-react";
import {
  DISCARD_PID_FAILED,
  DRAFT_DELETE_FAILED,
  DRAFT_HAS_VALIDATION_ERRORS,
  DRAFT_PREVIEW_FAILED,
  DRAFT_PUBLISH_FAILED,
  DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS,
  DRAFT_SAVE_FAILED,
  DRAFT_SAVE_SUCCEEDED,
  DRAFT_SUBMIT_REVIEW_FAILED,
  DRAFT_SUBMIT_REVIEW_FAILED_WITH_VALIDATION_ERRORS,
  FILE_IMPORT_FAILED,
  FILE_UPLOAD_SAVE_DRAFT_FAILED,
  RESERVE_PID_FAILED,
} from "../state/types";
import { leafTraverse } from "../utils";
import PropTypes from "prop-types";

const defaultLabels = {
  "files.enabled": i18next.t("Files"),
  "metadata.resource_type": i18next.t("Resource type"),
  "metadata.title": i18next.t("Title"),
  "metadata.additional_titles": i18next.t("Additional titles"),
  "metadata.publication_date": i18next.t("Publication date"),
  "metadata.creators": i18next.t("Creators"),
  "metadata.contributors": i18next.t("Contributors"),
  "metadata.description": i18next.t("Description"),
  "metadata.additional_descriptions": i18next.t("Additional descriptions"),
  "metadata.rights": i18next.t("Licenses"),
  "metadata.languages": i18next.t("Languages"),
  "metadata.dates": i18next.t("Dates"),
  "metadata.version": i18next.t("Version"),
  "metadata.publisher": i18next.t("Publisher"),
  "metadata.related_identifiers": i18next.t("Related works"),
  "metadata.references": i18next.t("References"),
  "metadata.identifiers": i18next.t("Alternate identifiers"),
  "metadata.subjects": i18next.t("Keywords and subjects"),
  "access.embargo.until": i18next.t("Embargo until"),
  "pids.doi": i18next.t("DOI"),
};

const ACTIONS = {
  [DRAFT_SAVE_SUCCEEDED]: {
    feedback: "positive",
    message: i18next.t("Record successfully saved."),
  },
  [DRAFT_HAS_VALIDATION_ERRORS]: {
    feedback: "warning",
    message: i18next.t("Record saved with validation errors:"),
  },
  [DRAFT_SAVE_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "The draft was not saved. Please try again. If the problem persists, contact user support."
    ),
  },
  [DRAFT_PUBLISH_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "The draft was not published. Please try again. If the problem persists, contact user support."
    ),
  },
  [DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS]: {
    feedback: "negative",
    message: i18next.t(
      "The draft was not published. Record saved with validation errors:"
    ),
  },
  [DRAFT_SUBMIT_REVIEW_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "The draft was not submitted for review. Please try again. If the problem persists, contact user support."
    ),
  },
  [DRAFT_SUBMIT_REVIEW_FAILED_WITH_VALIDATION_ERRORS]: {
    feedback: "negative",
    message: i18next.t(
      "The draft was not submitted for review. Record saved with validation errors:"
    ),
  },
  [DRAFT_DELETE_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft deletion failed. Please try again. If the problem persists, contact user support."
    ),
  },
  [DRAFT_PREVIEW_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft preview failed. Please try again. If the problem persists, contact user support."
    ),
  },
  [RESERVE_PID_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Identifier reservation failed. Please try again. If the problem persists, contact user support."
    ),
  },
  [DISCARD_PID_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Identifier could not be discarded. Please try again. If the problem persists, contact user support."
    ),
  },
  [FILE_UPLOAD_SAVE_DRAFT_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Draft save failed before file upload. Please try again. If the problem persists, contact user support."
    ),
  },
  [FILE_IMPORT_FAILED]: {
    feedback: "negative",
    message: i18next.t(
      "Files import from the previous version failed. Please try again. If the problem persists, contact user support."
    ),
  },
};

class DisconnectedFormFeedback extends Component {
  constructor(props) {
    super(props);
    this.labels = {
      ...defaultLabels,
      ...props.labels,
    };
  }

  /**
   * Render error messages inline (if 1) or as list (if multiple).
   *
   * @param {Array<String>} messages
   * @returns String or React node
   */
  renderErrorMessages(messages) {
    const uniqueMessages = [...new Set(messages)];
    if (uniqueMessages.length === 1) {
      return messages[0];
    } else {
      return (
        <ul>
          {uniqueMessages.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      );
    }
  }

  /**
   * Return array of error messages from errorValue object.
   *
   * The error message(s) might be deeply nested in the errorValue e.g.
   *
   * errorValue = [
   *   {
   *     title: "Missing value"
   *   }
   * ];
   *
   * @param {object} errorValue
   * @returns array of Strings (error messages)
   */
  toErrorMessages(errorValue) {
    let messages = [];
    let store = (l) => {
      messages.push(l);
    };
    leafTraverse(errorValue, store);
    return messages;
  }

  /**
   * Return object with human readbable labels as keys and error messages as
   * values given an errors object.
   *
   * @param {object} errors
   * @returns object
   */
  toLabelledErrorMessages(errors) {
    // Step 0 - Create object with collapsed 1st and 2nd level keys
    //          e.g., {metadata: {creators: ,,,}} => {"metadata.creators": ...}
    // For now, only for metadata, files and access.embargo
    const metadata = errors.metadata || {};
    const step0Metadata = Object.entries(metadata).map(([key, value]) => {
      return ["metadata." + key, value];
    });
    const files = errors.files || {};
    const step0Files = Object.entries(files).map(([key, value]) => {
      return ["files." + key, value];
    });
    const access = errors.access?.embargo || {};
    const step0Access = Object.entries(access).map(([key, value]) => {
      return ["access.embargo." + key, value];
    });
    const pids = errors.pids || {};
    const step0Pids = _isObject(pids)
      ? Object.entries(pids).map(([key, value]) => {
          return ["pids." + key, value];
        })
      : [["pids", pids]];
    const customFields = errors.custom_fields || {};
    const step0CustomFields = Object.entries(customFields).map(([key, value]) => {
      return ["custom_fields." + key, value];
    });
    const step0 = Object.fromEntries(
      step0Metadata
        .concat(step0Files)
        .concat(step0Access)
        .concat(step0Pids)
        .concat(step0CustomFields)
    );

    // Step 1 - Transform each error value into array of error messages
    const step1 = Object.fromEntries(
      Object.entries(step0).map(([key, value]) => {
        return [key, this.toErrorMessages(value)];
      })
    );

    // Step 2 - Group error messages by label
    // (different error keys can map to same label e.g. title and
    // additional_titles)
    const labelledErrorMessages = {};
    for (const key in step1) {
      const label = this.labels[key] || "Unknown field";
      let messages = labelledErrorMessages[label] || [];
      labelledErrorMessages[label] = messages.concat(step1[key]);
    }

    return labelledErrorMessages;
  }

  render() {
    const { errors: errorsProp, actionState } = this.props;

    const errors = errorsProp || {};

    const { feedback, message } = _get(ACTIONS, actionState, {
      feedback: undefined,
      message: undefined,
    });

    if (!message) {
      // if no message to display, simply return null
      return null;
    }

    const labelledMessages = this.toLabelledErrorMessages(errors);
    const listErrors = Object.entries(labelledMessages).map(([label, messages]) => (
      <Message.Item key={label}>
        <b>{label}</b>: {this.renderErrorMessages(messages)}
      </Message.Item>
    ));

    // errors not related to validation, following a different format {status:.., message:..}
    const backendErrorMessage = errors.message;

    return (
      <Message
        visible
        positive={feedback === "positive"}
        warning={feedback === "warning"}
        negative={feedback === "negative"}
        className="flashed top attached"
      >
        <Grid container>
          <Grid.Column width={15} textAlign="left">
            <strong>{backendErrorMessage || message}</strong>
            {listErrors.length > 0 && <Message.List>{listErrors}</Message.List>}
          </Grid.Column>
        </Grid>
      </Message>
    );
  }
}

DisconnectedFormFeedback.propTypes = {
  errors: PropTypes.object,
  actionState: PropTypes.string,
  labels: PropTypes.object,
};

DisconnectedFormFeedback.defaultProps = {
  errors: undefined,
  actionState: undefined,
  labels: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  errors: state.deposit.errors,
});

export const FormFeedback = connect(mapStateToProps, null)(DisconnectedFormFeedback);
