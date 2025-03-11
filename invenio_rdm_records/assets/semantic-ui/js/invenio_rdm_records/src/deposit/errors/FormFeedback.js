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
import { Grid, Message, Label, Icon, List } from "semantic-ui-react";
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
import { flattenAndCategorizeErrors } from "react-invenio-forms";

const ACTIONS = {
  [DRAFT_SAVE_SUCCEEDED]: {
    feedback: "positive",
    message: i18next.t("Record successfully saved."),
  },
  [DRAFT_HAS_VALIDATION_ERRORS]: {
    feedback: "negative",
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
      ...props.labels,
    };
    this.sections = {
      ...props.sectionsConfig,
    };
  }

  getErrorPaths(obj, prefix = "") {
    const paths = new Set();

    const recurse = (currentObj, currentPath) => {
      if (Array.isArray(currentObj)) {
        currentObj.forEach((item, index) => recurse(item, `${currentPath}[${index}]`));
      } else if (currentObj && typeof currentObj === "object") {
        Object.keys(currentObj).forEach((key) =>
          recurse(currentObj[key], currentPath ? `${currentPath}.${key}` : key)
        );
      } else {
        paths.add(currentPath);
      }
    };

    recurse(obj, prefix);
    return [...paths];
  }

  getErrorSections(errors) {
    const errorSections = new Map();
    const errorPaths = Object.keys(errors);
    errorPaths.forEach((path) => {
      let errorCount = 1;

      for (const [section, fields] of Object.entries(this.sections)) {
        if (fields.some((field) => path.startsWith(field))) {
          const sectionElement = document.getElementById(section);
          if (sectionElement) {
            const label = sectionElement.getAttribute("label") || "Unknown section";
            const errorField = _get(this.props.errors, path, null);
            errorCount = Array.isArray(errorField) ? errorField.length : 1;

            errorSections.set(section, {
              label,
              count: (errorSections.get(section)?.count || 0) + errorCount,
            });
          }
          return;
        }
      }

      const labelElement = document.querySelector(
        `label[for^="${path.replace(/^(.*?)(\[\d+\].*)?$/, "$1")}"]`
      );
      const sectionElement = labelElement?.closest(".accordion");

      if (sectionElement) {
        const sectionId = sectionElement.id;
        const label = sectionElement.getAttribute("label") || "Unknown section";
        const errorField = _get(this.props.errors, path, null);
        errorCount = Array.isArray(errorField) ? errorField.length : 1;

        errorSections.set(sectionId, {
          label,
          count: (errorSections.get(sectionId)?.count || 0) + errorCount,
        });
      }
    });

    const orderedSections = [
      ...(errorSections.has("files-section")
        ? [["files-section", errorSections.get("files-section")]]
        : []),
      ...[...errorSections].filter(([key]) => key !== "files-section"),
    ];

    return orderedSections.map(([sectionId, { label, count }], i) => (
      <a className="pl-5" key={i} href={`#${sectionId}`}>
        {label}{" "}
        <Label circular size="tiny">
          {count}
        </Label>
      </a>
    ));
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

    const { flattenedErrors, severityChecks } = flattenAndCategorizeErrors(errors);

    const errorSections = this.getErrorSections(flattenedErrors);

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
              <Icon name={feedback === "positive" ? "check" : "exclamation triangle"} />{" "}
              {backendErrorMessage || message}
              {errorSections.length > 0 && (
                <>{errorSections.reduce((prev, curr) => [prev, ", ", curr])}</>
              )}
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
  sectionsConfig: PropTypes.object,
};

DisconnectedFormFeedback.defaultProps = {
  errors: undefined,
  actionState: undefined,
  labels: undefined,
  sectionsConfig: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  errors: state.deposit.errors,
});

export const FormFeedback = connect(mapStateToProps, null)(DisconnectedFormFeedback);
