// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import _get from "lodash/get";
import Overridable from "react-overridable";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { TextAreaField, ErrorMessage } from "react-invenio-forms";
import { Button, Form, Icon, Message, Modal } from "semantic-ui-react";
import * as Yup from "yup";
import {
  PublishCheckboxComponent,
  ensureUniqueProps,
} from "./PublishCheckboxComponent";

class SubmitReviewModalComponent extends Component {
  constructor(props) {
    super(props);
    const { initialReviewComment, extraCheckboxes, record } = props;
    this.validationSchema = this.getValidationSchema(record);
    this.initialValues = this.getInitialValues(initialReviewComment, record);

    // Get extra checkbox component and define its schema and defaults
    if (extraCheckboxes.length > 0) {
      // Validate id and fieldpath are unique
      const fieldPaths = extraCheckboxes.map((checkbox) => checkbox.fieldPath);
      fieldPaths.push("acceptAccessToRecord", "acceptAfterPublishRecord");
      ensureUniqueProps(fieldPaths, "fieldPath");
      const ids = extraCheckboxes.map((checkbox) => checkbox.id);
      ids.push("accept-access-checkbox", "accept-after-publish-checkbox");
      ensureUniqueProps(ids, "id");

      extraCheckboxes.forEach((checkbox) => {
        this.validationSchema = this.validationSchema.concat(
          Yup.object({
            [checkbox.fieldPath]: Yup.bool().oneOf(
              [true],
              i18next.t("You must accept this.")
            ),
          })
        );
        this.initialValues[checkbox.fieldPath] = false;
      });
    }
  }

  componentDidMount() {
    // A11y: Focus the first input field in the form
    const firstFormFieldWrap = document.getElementById("accept-access-checkbox");
    const checkboxElem = firstFormFieldWrap.querySelector("input");
    checkboxElem?.focus();
  }

  getValidationSchema = (record) => {
    let baseSchema = Yup.object({
      acceptAccessToRecord: Yup.bool().oneOf(
        [true],
        i18next.t("You must accept this.")
      ),
      reviewComment: Yup.string(),
    });

    // acceptAfterPublishRecord checkbox is absent if record is published
    if (!record) {
      baseSchema = baseSchema.concat(
        Yup.object({
          acceptAfterPublishRecord: Yup.bool().oneOf(
            [true],
            i18next.t("You must accept this.")
          ),
        })
      );
    }
    return baseSchema;
  };

  getModalContent = (record, directPublish, communityTitle) => {
    const modalContent = {
      headerTitle: i18next.t("Submit for review"),
      msgWarningTitle: i18next.t(
        "Before requesting review, please read and check the following:"
      ),
      submitBtnLbl: i18next.t("Submit record for review"),
      acceptAccessToRecordText: (
        <>
          {i18next.t("The '{{communityTitle}}' curators will have access to", {
            communityTitle,
          })}{" "}
          <b>{i18next.t("view and edit")}</b>{" "}
          {i18next.t("your upload's metadata and files.")}
        </>
      ),
      acceptAfterPublishRecordText: (
        <>
          {i18next.t(
            "If your upload is accepted by the community curators, it will be"
          )}{" "}
          <b>{i18next.t("immediately published")}</b>.{" "}
          {i18next.t(
            "Before that, you will still be able to modify metadata and files of this upload."
          )}
        </>
      ),
    };

    if (record?.is_published) {
      modalContent["headerTitle"] = i18next.t("Submit to community");
      modalContent["msgWarningTitle"] = i18next.t(
        "Before submitting to community, please read and check the following:"
      );
      modalContent["submitBtnLbl"] = i18next.t("Submit to community");
    } else if (directPublish) {
      modalContent["headerTitle"] = i18next.t("Publish to community");
      modalContent["msgWarningTitle"] = i18next.t(
        "Before publishing to the community, please read and check the following:"
      );
      modalContent["acceptAfterPublishRecordText"] = (
        <>
          {i18next.t("Your upload will be")} <b>{i18next.t("immediately published")}</b>{" "}
          {i18next.t(
            "in '{{communityTitle}}'. You will no longer be able to change the files in the upload!",
            {
              communityTitle,
            }
          )}{" "}
          {i18next.t(
            "However, you will still be able to update the record's metadata later."
          )}
        </>
      );
      modalContent["submitBtnLbl"] = i18next.t("Publish record to community");
    }

    return modalContent;
  };

  getInitialValues = (initialReviewComment, record) => ({
    reviewComment: initialReviewComment || "",
    acceptAccessToRecord: false,
    acceptAfterPublishRecord: record ? undefined : false,
  });

  render() {
    const {
      isConfirmModalOpen,
      community,
      onClose,
      onSubmit,
      publishModalExtraContent,
      directPublish,
      errors,
      loading,
      record,
      extraCheckboxes,
      beforeContent,
      afterContent,
    } = this.props;

    const communityTitle = community.metadata.title;
    const modalContent = this.getModalContent(record, directPublish, communityTitle);

    return (
      <Formik
        initialValues={this.initialValues}
        onSubmit={onSubmit}
        validationSchema={this.validationSchema}
        validateOnChange={false}
        validateOnBlur={false}
      >
        {({ values, handleSubmit }) => {
          return (
            <Modal
              open={isConfirmModalOpen}
              onClose={onClose}
              size="small"
              closeIcon
              closeOnDimmerClick={false}
            >
              <Modal.Header>{modalContent.headerTitle}</Modal.Header>
              <Modal.Content>
                {errors && <ErrorMessage errors={errors} />}
                <Message visible warning>
                  <p>
                    <Icon name="warning sign" />
                    {modalContent.msgWarningTitle}
                  </p>
                </Message>
                <Form>
                  {beforeContent && <div>{beforeContent()}</div>}
                  <PublishCheckboxComponent
                    id="accept-access-checkbox"
                    fieldPath="acceptAccessToRecord"
                    text={modalContent.acceptAccessToRecordText}
                  />
                  {!record && (
                    <PublishCheckboxComponent
                      id="accept-after-publish-checkbox"
                      fieldPath="acceptAfterPublishRecord"
                      text={modalContent.acceptAfterPublishRecordText}
                    />
                  )}
                  {extraCheckboxes.length > 0 &&
                    extraCheckboxes.map((checkbox) => (
                      <PublishCheckboxComponent
                        id={`${checkbox.fieldPath}-checkbox`}
                        key={checkbox.fieldPath}
                        fieldPath={checkbox.fieldPath}
                        text={checkbox.text}
                      />
                    ))}
                  {!directPublish && (
                    <TextAreaField
                      fieldPath="reviewComment"
                      label={i18next.t("Message to curators (optional)")}
                    />
                  )}
                  {publishModalExtraContent && (
                    <div
                      dangerouslySetInnerHTML={{ __html: publishModalExtraContent }}
                    />
                  )}
                  {afterContent && <div>{afterContent()}</div>}
                </Form>
              </Modal.Content>
              <Modal.Actions>
                <Button
                  onClick={onClose}
                  floated="left"
                  loading={loading}
                  disabled={loading}
                >
                  {i18next.t("Cancel")}
                </Button>
                <Button
                  name="submitReview"
                  onClick={(event) => {
                    handleSubmit(event);
                  }}
                  loading={loading}
                  disabled={loading}
                  positive={directPublish}
                  primary={!directPublish}
                  content={modalContent.submitBtnLbl}
                />
              </Modal.Actions>
            </Modal>
          );
        }}
      </Formik>
    );
  }
}

SubmitReviewModalComponent.propTypes = {
  isConfirmModalOpen: PropTypes.bool.isRequired,
  community: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  initialReviewComment: PropTypes.string,
  publishModalExtraContent: PropTypes.string,
  directPublish: PropTypes.bool,
  errors: PropTypes.node, // TODO FIXME: Use a common error cmp to display errros.
  loading: PropTypes.bool,
  record: PropTypes.object.isRequired,
  extraCheckboxes: PropTypes.arrayOf(
    PropTypes.shape({
      fieldPath: PropTypes.string,
      text: PropTypes.string,
    })
  ),
  beforeContent: PropTypes.func,
  afterContent: PropTypes.func,
};

SubmitReviewModalComponent.defaultProps = {
  initialReviewComment: "",
  publishModalExtraContent: undefined,
  directPublish: false,
  errors: undefined,
  loading: false,
  extraCheckboxes: [],
  beforeContent: () => undefined,
  afterContent: () => undefined,
};

export const SubmitReviewModal = Overridable.component(
  "InvenioRdmRecords.SubmitReviewModal.container",
  SubmitReviewModalComponent
);
