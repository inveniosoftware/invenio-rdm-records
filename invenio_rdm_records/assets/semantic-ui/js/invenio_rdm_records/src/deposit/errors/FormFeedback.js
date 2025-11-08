// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021-2025 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { FormFeedbackSummary } from "./FormFeedbackSummary";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Grid, Message, Icon } from "semantic-ui-react";
import {
  DISCARD_PID_FAILED,
  DRAFT_DELETE_FAILED,
  DRAFT_HAS_VALIDATION_ERRORS,
  DRAFT_PREVIEW_FAILED,
  DRAFT_PUBLISH_FAILED,
  DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS,
  DRAFT_SAVE_FAILED,
  DRAFT_SAVE_SUCCEEDED,
  DRAFT_LOADED_WITH_VALIDATION_ERRORS,
  DRAFT_SUBMIT_REVIEW_FAILED,
  DRAFT_SUBMIT_REVIEW_FAILED_WITH_VALIDATION_ERRORS,
  FILE_IMPORT_FAILED,
  FILE_UPLOAD_SAVE_DRAFT_FAILED,
  RESERVE_PID_FAILED,
} from "../state/types";
import PropTypes from "prop-types";

const ACTIONS = {
  [DRAFT_SAVE_SUCCEEDED]: {
    feedback: "positive",
    message: i18next.t("Record successfully saved."),
  },
  [DRAFT_HAS_VALIDATION_ERRORS]: {
    feedback: "warning",
    message: i18next.t("Record saved with validation feedback in"),
  },
  [DRAFT_LOADED_WITH_VALIDATION_ERRORS]: {
    feedback: "warning",
    message: i18next.t("Draft has validation feedback in"),
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
  }

  render() {
    const { errors: errorsProp, actionState, sectionsConfig } = this.props;
    const errors = errorsProp || {};

    const { feedback: initialFeedback, message } = _get(ACTIONS, actionState, {
      feedback: undefined,
      message: undefined,
    });

    if (!message) {
      return null;
    }

    const noSeverityChecksWithErrors = Object.values(errors).every(
      (severityObject) => severityObject.severity !== "error"
    );

    // Determine final feedback without reassigning
    const feedback =
      _isEmpty(errors) && noSeverityChecksWithErrors ? "suggestive" : initialFeedback;

    // if no field is specified on the backend, then the validation message is on the `_schema` field
    // if the backend returns an explicit message e.g server error, then we use that instead of the default one
    const backendErrorMessage = errors.message || errors._schema;

    // Retrieve the corresponding icon and type if the feedback is a valid key,
    // else fallback to warning.
    const { icon, type } = feedbackConfig[feedback] || feedbackConfig["warning"];

    // generate dynamic id for easy getElementById calls.
    // see feedbackConfig for possible values.
    return (
      <Message
        visible
        {...{ [type]: true }}
        className="flashed top attached"
        id={type + "-feedback-div"}
      >
        <Grid container>
          <Grid.Column width={15} textAlign="left">
            <strong>
              <Icon name={icon} /> {backendErrorMessage || message}
              <FormFeedbackSummary sectionsConfig={sectionsConfig} errors={errors} />
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
