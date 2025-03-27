// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Grid, Message, Label, Icon } from "semantic-ui-react";
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
    feedback: "warning",
    message: i18next.t("Record saved with validation feedback in"),
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
      "The draft was not published. Record saved with validation feedback in"
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
      "The draft was not submitted for review. Record saved with validation feedback in"
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

const feedbackConfig = {
  positive: { icon: "check", type: "positive" },
  suggestive: { icon: "info circle", type: "info" },
  negative: { icon: "times circle", type: "negative" },
  warning: { icon: "exclamation triangle", type: "warning" },
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

  getErrorSections(errors) {
    const errorSections = new Map();

    // Iterate over each error path in the errors object
    Object.keys(errors).forEach((path) => {
      let errorCount = Array.isArray(errors[path]) ? errors[path].length : 1;

      // Try to match error to a section based on field paths
      for (const [section, fields] of Object.entries(this.sections)) {
        if (fields.some((field) => path.startsWith(field))) {
          const sectionElement = document.getElementById(section);
          const label = sectionElement?.getAttribute("label") || "Unknown section";
          errorSections.set(section, {
            label,
            count: (errorSections.get(section)?.count || 0) + errorCount,
          });
          return;
        }
      }

      // If not matched in predefined sections, check dynamically in accordions
      const sectionElement = document
        .querySelector(`label[for^="${path.replace(/^(.*?)(\[\d+\].*)?$/, "$1")}"]`)
        ?.closest(".accordion");
      if (sectionElement) {
        const sectionId = sectionElement.id;
        const label = sectionElement.getAttribute("label") || "Unknown section";
        errorSections.set(sectionId, {
          label,
          count: (errorSections.get(sectionId)?.count || 0) + errorCount,
        });
      }
    });

    // Order sections based on their DOM appearance and return error links
    const accordions = Array.from(document.querySelectorAll(".accordion")).map(
      (accordion) => accordion.id
    );

    const orderedSections = [
      ...accordions.filter((id) => errorSections.has(id)), // Keep sections that exist in order
      ...[...errorSections.keys()].filter((id) => !accordions.includes(id)), // Append missing sections
    ];

    return orderedSections.map((sectionId, i) => {
      const { label, count } = errorSections.get(sectionId);
      return (
        <a key={sectionId} className="pl-5" href={`#${sectionId}`}>
          {label}{" "}
          <Label circular size="tiny">
            {count}
          </Label>
        </a>
      );
    });
  }

  render() {
    const { errors: errorsProp, actionState } = this.props;
    const errors = errorsProp || {};

    const { feedback: initialFeedback, message } = _get(ACTIONS, actionState, {
      feedback: undefined,
      message: undefined,
    });

    if (!message) {
      return null;
    }

    const { flattenedErrors, severityChecks } = flattenAndCategorizeErrors(errors);
    const errorSections = this.getErrorSections({
      ...flattenedErrors,
      ...severityChecks,
    });

    const noSeverityChecksWithErrors = Object.values(severityChecks).every(
      (severityObject) => severityObject.severity !== "error"
    );

    // Determine final feedback without reassigning
    const feedback =
      errorSections && _isEmpty(flattenedErrors) && noSeverityChecksWithErrors
        ? "suggestive"
        : initialFeedback;

    const backendErrorMessage = errors.message;

    // Retrieve the corresponding icon and type
    const { icon, type } = feedbackConfig[feedback] || {};

    return (
      <Message visible {...{ [type]: true }} className="flashed top attached">
        <Grid container>
          <Grid.Column width={15} textAlign="left">
            <strong>
              <Icon name={icon} middle aligned /> {backendErrorMessage || message}
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
