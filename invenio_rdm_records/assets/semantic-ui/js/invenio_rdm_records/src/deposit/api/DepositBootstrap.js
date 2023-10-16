// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import { BaseForm } from "react-invenio-forms";
import { connect } from "react-redux";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "./DepositFormSubmitContext";
import {
  delete_,
  discardPID,
  preview,
  publish,
  reservePID,
  save,
  submitReview,
} from "../state/actions";
import { scrollTop } from "../utils";

class DepositBootstrapComponent extends Component {
  componentDidMount() {
    window.addEventListener("beforeunload", (e) => {
      const { fileUploadOngoing } = this.props;
      if (fileUploadOngoing) {
        e.returnValue = "";
        return "";
      }
    });
    window.addEventListener("unload", async () => {
      // TODO: cancel all uploads
      // Investigate if it's possible to wait for the deletion request to complete
      // before unloading the page
    });
  }

  submitContext = undefined;

  setSubmitContext = (actionName, extra = {}) => {
    this.submitContext = {
      actionName: actionName,
      extra: extra,
    };
  };

  onFormSubmit = async (values, formikBag) => {
    const {
      saveAction,
      publishAction,
      submitReview,
      previewAction,
      deleteAction,
      reservePIDAction,
      discardPIDAction,
    } = this.props;
    const { actionName, extra } = this.submitContext;

    let actionFunc = undefined;
    const params = {};
    switch (actionName) {
      case DepositFormSubmitActions.SAVE:
        actionFunc = saveAction;
        break;
      case DepositFormSubmitActions.PUBLISH:
        actionFunc = publishAction;
        break;
      case DepositFormSubmitActions.PUBLISH_WITHOUT_COMMUNITY:
        actionFunc = publishAction;
        params["removeSelectedCommunity"] = true;
        break;
      case DepositFormSubmitActions.SUBMIT_REVIEW:
        actionFunc = submitReview;
        params["reviewComment"] = extra["reviewComment"];
        params["directPublish"] = extra["directPublish"];
        break;
      case DepositFormSubmitActions.PREVIEW:
        actionFunc = previewAction;
        break;
      case DepositFormSubmitActions.DELETE:
        actionFunc = deleteAction;
        params["isDiscardingVersion"] = extra["isDiscardingVersion"];
        break;
      case DepositFormSubmitActions.RESERVE_PID:
        actionFunc = reservePIDAction;
        params["pidType"] = extra["pidType"];
        break;
      case DepositFormSubmitActions.DISCARD_PID:
        actionFunc = discardPIDAction;
        params["pidType"] = extra["pidType"];
        break;
      default:
        throw Error("The submit btn must set the form action name.");
    }

    try {
      await actionFunc(values, params);
    } catch (error) {
      // make sure the error contains form errors, and not global errors.
      if (error && error.errors) {
        formikBag.setErrors(error.errors);
      } else {
        // scroll top to show the global error
        scrollTop();
      }
    } finally {
      // reset the action name after having handled it
      this.submitContext = {};
    }
  };

  render() {
    const { errors, record, children } = this.props;
    return (
      <DepositFormSubmitContext.Provider
        value={{ setSubmitContext: this.setSubmitContext }}
      >
        <BaseForm
          onSubmit={this.onFormSubmit}
          formik={{
            // enableReinitialise needed due to
            // updated draft PID (and the endpoint URL as a consequence).
            // After saving draft for the first time, a new PID is obtained,
            // initial values need to be updated with draft record containing
            // the new PID in its payload, otherwise a new PID
            // is requested on each action, generating countless drafts
            enableReinitialize: true,
            initialValues: record,
            // errors need to be repopulated after form is reinitialised
            ...(errors && { initialErrors: errors }),
          }}
        >
          {children}
        </BaseForm>
      </DepositFormSubmitContext.Provider>
    );
  }
}

DepositBootstrapComponent.propTypes = {
  errors: PropTypes.object,
  record: PropTypes.object.isRequired,
  children: PropTypes.node,
  saveAction: PropTypes.func.isRequired,
  publishAction: PropTypes.func.isRequired,
  submitReview: PropTypes.func.isRequired,
  previewAction: PropTypes.func.isRequired,
  deleteAction: PropTypes.func.isRequired,
  reservePIDAction: PropTypes.func.isRequired,
  discardPIDAction: PropTypes.func.isRequired,
  fileUploadOngoing: PropTypes.bool,
};

DepositBootstrapComponent.defaultProps = {
  errors: undefined,
  children: undefined,
  fileUploadOngoing: false,
};

const mapStateToProps = (state) => {
  const { isFileUploadInProgress, ...files } = state.files;
  return {
    record: state.deposit.record,
    errors: state.deposit.errors,
    formState: state.deposit.formState,
    fileUploadOngoing: isFileUploadInProgress,
    files: files,
  };
};

const mapDispatchToProps = (dispatch) => ({
  publishAction: (values, { removeSelectedCommunity = false }) =>
    dispatch(publish(values, { removeSelectedCommunity })),
  submitReview: (values, { reviewComment, directPublish }) =>
    dispatch(submitReview(values, { reviewComment, directPublish })),
  saveAction: (values) => dispatch(save(values)),
  previewAction: (values) => dispatch(preview(values)),
  deleteAction: (values, { isDiscardingVersion }) =>
    dispatch(delete_(values, { isDiscardingVersion })),
  reservePIDAction: (values, { pidType }) => dispatch(reservePID(values, { pidType })),
  discardPIDAction: (values, { pidType }) => dispatch(discardPID(values, { pidType })),
});

export const DepositBootstrap = connect(
  mapStateToProps,
  mapDispatchToProps
)(DepositBootstrapComponent);
