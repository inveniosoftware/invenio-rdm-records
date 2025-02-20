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
    message: i18next.t("Record saved with validation errors in"),
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
      "The draft was not published. Record saved with validation errors in"
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
      "The draft was not submitted for review. Record saved with validation errors in"
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
   * Return object with human readbable labels as keys and error messages as
   * values given an errors object.
   *
   * @param {object} errors
   * @returns object
   */
  getErrorPaths(obj) {
    const paths = new Set(); // Use a Set to avoid duplicates

    // Iterate over the top-level keys
    for (const topLevelKey of Object.keys(obj)) {
      if (Object.hasOwn(obj, topLevelKey)) {
        const nestedObj = obj[topLevelKey];

        // Iterate over the nested keys
        for (const nestedKey of Object.keys(nestedObj)) {
          if (Object.hasOwn(nestedObj, nestedKey)) {
            // Construct the path and add it to the Set
            paths.add(`${topLevelKey}.${nestedKey}`);
          }
        }
      }
    }

    // Convert the Set to an array and return
    return Array.from(paths);
  }

  /**
   * Return object with human readbable labels as keys and error messages as
   * values given an errors object.
   *
   * @param {object} errors
   * @returns object
   */
  getErrorMessages(arr) {
    const labels = arr
      .map((x) => document.querySelector(`label[for^="${x}"]`))
      .filter(Boolean);
    const sections = [...new Set(labels.map((x) => x.closest(".accordion")))];
    const outputSections = sections.map((x) => [
      x.id,
      x.querySelector(".title").innerText,
    ]);
    const message = outputSections.map((x, i) => (
      <a key={i} href={"#" + x[0]}>
        {x[1]}
      </a>
    ));
    return message;
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

    const errorPaths = this.getErrorPaths(errors);
    const errorSections = this.getErrorMessages(errorPaths);

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
            <strong>
              {backendErrorMessage || message}{" "}
              {errorSections.length > 0
                ? errorSections.reduce((prev, curr) => [prev, ", ", curr])
                : ""}
            </strong>
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
