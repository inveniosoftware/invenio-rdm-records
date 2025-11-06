// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2025 Graz University of Technology.
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
import { DRAFT_PUBLISH_STARTED } from "../../state/types";
import { scrollTop } from "../../utils";
import { DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS } from "../../state/types";
import { PublishModal } from "./PublishModal";

class PublishButtonComponent extends Component {
  state = { isConfirmModalOpen: false };

  static contextType = DepositFormSubmitContext;

  openConfirmModal = () => this.setState({ isConfirmModalOpen: true });

  closeConfirmModal = () => this.setState({ isConfirmModalOpen: false });

  handlePublish = () => {
    const { setSubmitContext } = this.context;
    const {
      formik,
      isDOIRequired,
      noINeedDOI,
      doiReservationCheck,
      publishWithoutCommunity,
    } = this.props;
    const { handleSubmit } = formik;

    const doiCheckFailed = doiReservationCheck(
      isDOIRequired,
      noINeedDOI,
      formik,
      "DOI is needed. You need to reserve a DOI before publishing.",
      DRAFT_PUBLISH_FAILED_WITH_VALIDATION_ERRORS
    );

    if (!doiCheckFailed) {
      setSubmitContext(
        publishWithoutCommunity
          ? DepositFormSubmitActions.PUBLISH_WITHOUT_COMMUNITY
          : DepositFormSubmitActions.PUBLISH
      );
      handleSubmit();
    }
    this.closeConfirmModal();
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
      formik,
      publishModalExtraContent,
      noINeedDOI,
      isDOIRequired,
      ...ui
    } = this.props;
    const { isConfirmModalOpen } = this.state;
    const { values, isSubmitting } = formik;

    const uiProps = _omit(ui, [
      "dispatch",
      "doiReservationCheck",
      "publishWithoutCommunity",
    ]);

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
          <PublishModal
            isConfirmModalOpen={isConfirmModalOpen}
            onClose={this.closeConfirmModal}
            onSubmit={this.handlePublish}
            publishModalExtraContent={publishModalExtraContent}
            buttonLabel={buttonLabel}
          />
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
  doiReservationCheck: PropTypes.func.isRequired,
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

export const PublishButton = connect(
  mapStateToProps,
  null
)(connectFormik(PublishButtonComponent));
