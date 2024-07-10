// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2024 Graz University of Technology.
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
import { Button, Icon, Message, Modal, Popup } from "semantic-ui-react";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "../../api/DepositFormSubmitContext";
import { DRAFT_PUBLISH_STARTED } from "../../state/types";

class PublishButtonComponent extends Component {
  state = { isConfirmModalOpen: false };

  static contextType = DepositFormSubmitContext;

  openConfirmModal = () => this.setState({ isConfirmModalOpen: true });

  closeConfirmModal = () => this.setState({ isConfirmModalOpen: false });

  handlePublish = (event, handleSubmit, publishWithoutCommunity) => {
    const { setSubmitContext } = this.context;

    setSubmitContext(
      publishWithoutCommunity
        ? DepositFormSubmitActions.PUBLISH_WITHOUT_COMMUNITY
        : DepositFormSubmitActions.PUBLISH
    );
    handleSubmit(event);
    this.closeConfirmModal();
  };

  isDisabled = (values, isSubmitting, filesState, hasPublishPermission) => {
    if (isSubmitting || !hasPublishPermission) {
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

  hasPermission = (permissions) => {
    return permissions.can_publish;
  };

  getDisabledButtonPopupText = (hasPublishPermission) => {
    let text = i18next.t("Required fields are missing");

    if (!hasPublishPermission) {
      text = i18next.t("You don't have permission to publish");
    }
    return text;
  };

  render() {
    const {
      actionState,
      filesState,
      buttonLabel,
      publishWithoutCommunity,
      formik,
      publishModalExtraContent,
      permissions,
      ...ui
    } = this.props;
    const { isConfirmModalOpen } = this.state;
    const { values, isSubmitting, handleSubmit } = formik;

    const uiProps = _omit(ui, ["dispatch"]);

    const hasPublishPermission = this.hasPermission(permissions);
    const publishDisabled = this.isDisabled(
      values,
      isSubmitting,
      filesState,
      hasPublishPermission
    );

    // only used when button is disabled
    const popupText = this.getDisabledButtonPopupText(hasPublishPermission);

    return (
      <>
        <Popup
          disabled={!publishDisabled}
          content={popupText}
          trigger={
            <span>
              <Button
                disabled={publishDisabled}
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
            </span>
          }
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
  permissions: PropTypes.object.isRequired,
};

PublishButtonComponent.defaultProps = {
  buttonLabel: i18next.t("Publish"),
  publishWithoutCommunity: false,
  actionState: undefined,
  publishModalExtraContent: undefined,
  filesState: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  publishModalExtraContent: state.deposit.config.publish_modal_extra,
  filesState: state.files,
  permissions: state.deposit.permissions,
});

export const PublishButton = connect(
  mapStateToProps,
  null
)(connectFormik(PublishButtonComponent));
