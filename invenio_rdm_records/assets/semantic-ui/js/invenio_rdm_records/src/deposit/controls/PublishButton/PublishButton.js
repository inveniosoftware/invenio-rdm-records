// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { connect as connectFormik } from "formik";
import _get from "lodash/get";
import _omit from "lodash/omit";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Button, Icon, Message, Modal } from "semantic-ui-react";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "../../api/DepositFormSubmitContext";
import { DRAFT_PUBLISH_STARTED } from "../../state/types";
import { scrollTop } from "../../utils";
import { DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS } from "../../state/types";

class PublishButtonComponent extends Component {
  state = { isConfirmModalOpen: false };

  static contextType = DepositFormSubmitContext;

  openConfirmModal = () => this.setState({ isConfirmModalOpen: true });

  closeConfirmModal = () => this.setState({ isConfirmModalOpen: false });

  handlePublish = (event, handleSubmit, publishWithoutCommunity) => {
    const { setSubmitContext } = this.context;
    const { formik, raiseDOINeededButNotReserved, isDOIRequired, noINeedDOI } =
      this.props;
    // Check for explicit DOI reservation via the "GET DOI button" only when DOI is
    // optional in the instance's settings. If it is required, backend will automatically
    // mint one even if it was not explicitly reserved
    const shouldCheckForExplicitDOIReservation =
      isDOIRequired !== undefined && // isDOIRequired is undefined when no value was provided from Invenio-app-rdm
      !isDOIRequired &&
      noINeedDOI &&
      Object.keys(formik?.values?.pids).length === 0;
    if (shouldCheckForExplicitDOIReservation) {
      const errors = {
        pids: {
          doi: i18next.t("DOI is needed. You need to reserve a DOI before publishing."),
        },
      };
      formik.setErrors(errors);
      raiseDOINeededButNotReserved(formik?.values, errors);
      this.closeConfirmModal();
    } else {
      setSubmitContext(
        publishWithoutCommunity
          ? DepositFormSubmitActions.PUBLISH_WITHOUT_COMMUNITY
          : DepositFormSubmitActions.PUBLISH
      );
      handleSubmit(event);
      this.closeConfirmModal();
    }
    // scroll top to show the global error
    scrollTop();
  };

  isDisabled = (values, isSubmitting, filesState) => {
    if (isSubmitting) {
      return true;
    }

    const filesEnabled = _get(values, "files.enabled", false);
    const filesArray = Object.values(filesState.entries ?? {});
    const filesMissing = filesEnabled && filesArray.length === 0;

    if (filesMissing) {
      return true;
    }

    // All files must be finished uploading
    const allCompleted = filesArray.every((file) => file.status === "finished");

    return !allCompleted;
  };

  render() {
    const {
      actionState,
      filesState,
      buttonLabel,
      publishWithoutCommunity,
      formik,
      publishModalExtraContent,
      raiseDOINeededButNotReserved,
      noINeedDOI,
      isDOIRequired,
      ...ui
    } = this.props;
    const { isConfirmModalOpen } = this.state;
    const { values, isSubmitting, handleSubmit } = formik;

    const uiProps = _omit(ui, ["dispatch"]);

    return (
      <>
        <Button
          disabled={this.isDisabled(values, isSubmitting, filesState)}
          name="publish"
          onClick={this.openConfirmModal}
          positive
          icon="upload"
          loading={isSubmitting && actionState === DRAFT_PUBLISH_STARTED}
          labelPosition="left"
          content={buttonLabel}
          {...uiProps}
          type="button" // needed so the formik form doesn't handle it as submit button i.e enable HTML validation on required input fields
        />
        {isConfirmModalOpen && (
          <Modal
            open={isConfirmModalOpen}
            onClose={this.closeConfirmModal}
            size="small"
            closeIcon
            closeOnDimmerClick={false}
          >
            <Modal.Header>
              {i18next.t("Are you sure you want to publish this record?")}
            </Modal.Header>
            {/* the modal text should only ever come from backend configuration */}
            <Modal.Content>
              <Message visible warning>
                <p>
                  <Icon name="warning sign" />{" "}
                  {i18next.t(
                    "Once the record is published you will no longer be able to change the files in the upload! However, you will still be able to update the record's metadata later."
                  )}
                </p>
              </Message>
              {publishModalExtraContent && (
                <div dangerouslySetInnerHTML={{ __html: publishModalExtraContent }} />
              )}
            </Modal.Content>
            <Modal.Actions>
              <Button onClick={this.closeConfirmModal} floated="left">
                {i18next.t("Cancel")}
              </Button>
              <Button
                onClick={(event) =>
                  this.handlePublish(event, handleSubmit, publishWithoutCommunity)
                }
                positive
                content={buttonLabel}
              />
            </Modal.Actions>
          </Modal>
        )}
      </>
    );
  }
}

PublishButtonComponent.propTypes = {
  buttonLabel: PropTypes.string,
  publishWithoutCommunity: PropTypes.bool,
  actionState: PropTypes.string,
  formik: PropTypes.object.isRequired,
  publishModalExtraContent: PropTypes.string,
  filesState: PropTypes.object,
  raiseDOINeededButNotReserved: PropTypes.func.isRequired,
  isDOIRequired: PropTypes.bool,
  noINeedDOI: PropTypes.bool,
};

PublishButtonComponent.defaultProps = {
  buttonLabel: i18next.t("Publish"),
  publishWithoutCommunity: false,
  actionState: undefined,
  publishModalExtraContent: undefined,
  filesState: undefined,
  isDOIRequired: undefined,
  noINeedDOI: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  publishModalExtraContent: state.deposit.config.publish_modal_extra,
  filesState: state.files,
  isDOIRequired: state.deposit.config.is_doi_required,
  noINeedDOI: state.deposit.noINeedDOI,
});

export const PublishButton = connect(mapStateToProps, (dispatch) => {
  return {
    raiseDOINeededButNotReserved: (data, errors) =>
      dispatch({
        type: DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS,
        payload: { data: data, errors: errors },
      }),
  };
})(connectFormik(PublishButtonComponent));
