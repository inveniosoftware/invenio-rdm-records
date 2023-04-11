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
import { Button } from "semantic-ui-react";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "../../api/DepositFormSubmitContext";
import { DepositStatus } from "../../state/reducers/deposit";
import { SubmitReviewModal } from "./SubmitReviewModal";

class SubmitReviewButtonComponent extends Component {
  state = { isConfirmModalOpen: false };
  static contextType = DepositFormSubmitContext;

  openConfirmModal = () => this.setState({ isConfirmModalOpen: true });

  closeConfirmModal = () => this.setState({ isConfirmModalOpen: false });

  handleSubmitReview = ({ reviewComment }) => {
    const { formik, directPublish } = this.props;
    const { handleSubmit } = formik;
    const { setSubmitContext } = this.context;

    setSubmitContext(DepositFormSubmitActions.SUBMIT_REVIEW, {
      reviewComment,
      directPublish,
    });
    handleSubmit();
    this.closeConfirmModal();
  };

  isDisabled = (numberOfFiles, disableSubmitForReviewButton) => {
    const { formik } = this.props;
    const { values, isSubmitting } = formik;

    const filesEnabled = _get(values, "files.enabled", false);
    const filesMissing = filesEnabled && !numberOfFiles;
    return isSubmitting || filesMissing || disableSubmitForReviewButton;
  };

  render() {
    const {
      actionState,
      actionStateExtra,
      community,
      disableSubmitForReviewButton,
      directPublish,
      formik,
      isRecordSubmittedForReview,
      numberOfFiles,
      publishModalExtraContent,
      ...ui
    } = this.props;

    const { isSubmitting } = formik;

    const uiProps = _omit(ui, ["dispatch"]);

    const { isConfirmModalOpen } = this.state;

    const btnLblSubmitReview = isRecordSubmittedForReview
      ? i18next.t("Submitted for review")
      : i18next.t("Submit for review");
    const buttonLbl = directPublish
      ? i18next.t("Publish to community")
      : btnLblSubmitReview;

    return (
      <>
        <Button
          disabled={this.isDisabled(numberOfFiles, disableSubmitForReviewButton)}
          name="SubmitReview"
          onClick={this.openConfirmModal}
          positive={directPublish}
          primary={!directPublish}
          icon="upload"
          loading={isSubmitting && actionState === "DRAFT_SUBMIT_REVIEW_STARTED"}
          labelPosition="left"
          content={buttonLbl}
          {...uiProps}
          type="button" // needed so the formik form doesn't handle it as submit button i.e enable HTML validation on required input fields
        />
        {isConfirmModalOpen && (
          <SubmitReviewModal
            isConfirmModalOpen={isConfirmModalOpen}
            initialReviewComment={actionStateExtra.reviewComment}
            onSubmit={this.handleSubmitReview}
            community={community}
            onClose={this.closeConfirmModal}
            publishModalExtraContent={publishModalExtraContent}
            directPublish={directPublish}
          />
        )}
      </>
    );
  }
}

SubmitReviewButtonComponent.propTypes = {
  actionState: PropTypes.string,
  actionStateExtra: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  numberOfFiles: PropTypes.number,
  disableSubmitForReviewButton: PropTypes.bool,
  isRecordSubmittedForReview: PropTypes.bool.isRequired,
  directPublish: PropTypes.bool,
  formik: PropTypes.object.isRequired,
  publishModalExtraContent: PropTypes.string,
};

SubmitReviewButtonComponent.defaultProps = {
  actionState: undefined,
  numberOfFiles: undefined,
  disableSubmitForReviewButton: undefined,
  publishModalExtraContent: undefined,
  directPublish: false,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  actionStateExtra: state.deposit.actionStateExtra,
  community: state.deposit.editorState.selectedCommunity,
  isRecordSubmittedForReview: state.deposit.record.status === DepositStatus.IN_REVIEW,
  disableSubmitForReviewButton:
    state.deposit.editorState.ui.disableSubmitForReviewButton,
  numberOfFiles: Object.values(state.files.entries).length,
  publishModalExtraContent: state.deposit.config.publish_modal_extra,
});

export const SubmitReviewButton = connect(
  mapStateToProps,
  null
)(connectFormik(SubmitReviewButtonComponent));
