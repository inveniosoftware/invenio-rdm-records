/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2025 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { connect as connectFormik } from "formik";
import _get from "lodash/get";
import _omit from "lodash/omit";
import PropTypes from "prop-types";
import { Component } from "react";
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

function PublishButtonComponent({formik, isDOIRequired = undefined, noINeedDOI = undefined, doiReservationCheck, publishWithoutCommunity = false, actionState = undefined, filesState = undefined, buttonLabel = i18next.t("Publish"), publishModalExtraContent = undefined, ...ui}) {
  const contextValue = React.useContext(DepositFormSubmitContext);

  const openConfirmModal = () => this.setState({ isConfirmModalOpen: true });

  const closeConfirmModal = () => this.setState({ isConfirmModalOpen: false });

  const handlePublish = () => {
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
    closeConfirmModal();
    // scroll top to show the global error
    scrollTop();
  };

  const isDisabled = (values, isSubmitting, filesState) => {
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

  const { values, isSubmitting } = formik;

    const uiProps = _omit(ui, [
      "dispatch",
      "doiReservationCheck",
      "publishWithoutCommunity",
    ]);

    return (
      <>
        <Button
          disabled={isDisabled(values, isSubmitting, filesState)}
          name="publish"
          onClick={openConfirmModal}
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
            onClose={closeConfirmModal}
            onSubmit={handlePublish}
            publishModalExtraContent={publishModalExtraContent}
            buttonLabel={buttonLabel}
            depositFormHandleSubmit={formik.handleSubmit}
          />
        )}
      </>
    );
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
