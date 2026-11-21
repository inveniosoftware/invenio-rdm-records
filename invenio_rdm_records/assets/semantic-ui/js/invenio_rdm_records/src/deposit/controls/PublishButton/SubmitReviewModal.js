/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import { useEffect } from "react";
import { Trans } from "react-i18next";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import Overridable from "react-overridable";
import PropTypes from "prop-types";
import { TextAreaField, ErrorMessage } from "react-invenio-forms";
import { Button, Form, Icon, Message, Modal } from "semantic-ui-react";
import * as Yup from "yup";
import {
  PublishCheckboxComponent,
  ensureUniqueProps,
} from "./PublishCheckboxComponent";

function SubmitReviewModalComponent({
  initialReviewComment = "",
  extraCheckboxes = [],
  record,
  isConfirmModalOpen,
  community,
  onClose,
  onSubmit,
  publishModalExtraContent = undefined,
  directPublish = false,
  errors = "",
  loading = false,
  beforeContent = () => undefined,
  afterContent = () => undefined,
}) {
  useEffect(() => {
    // A11y: Focus the first input field in the form
    const firstFormFieldWrap = document.getElementById("accept-access-checkbox");
    const checkboxElem = firstFormFieldWrap?.querySelector("input");
    checkboxElem?.focus();
  }, []);

  const getValidationSchema = (record) => {
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

  const getModalContent = (record, directPublish, communityTitle) => {
    const modalContent = {
      headerTitle: i18next.t("Submit for review"),
      msgWarningTitle: i18next.t(
        "Before requesting review, please read and check the following:"
      ),
      submitBtnLbl: i18next.t("Submit record for review"),
      acceptAccessToRecordText: (
        <Trans
          i18n={i18next}
          defaults="The '{{communityTitle}}' curators will have access to <bold>view and edit</bold> your upload's metadata and files."
          values={{ communityTitle }}
          components={{ bold: <b /> }}
        />
      ),
      acceptAfterPublishRecordText: (
        <Trans
          i18n={i18next}
          defaults="If your upload is accepted by the community curators, it will be <bold>immediately published</bold>. Before that, you will still be able to modify metadata and files of this upload."
          components={{ bold: <b /> }}
        />
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
        <Trans
          i18n={i18next}
          defaults="Your upload will be <bold>immediately published</bold> in '{{communityTitle}}'. You will no longer be able to change the files in the upload! However, you will still be able to update the record's metadata later."
          values={{ communityTitle }}
          components={{ bold: <b /> }}
        />
      );
      modalContent["submitBtnLbl"] = i18next.t("Publish record to community");
    }

    return modalContent;
  };

  const getInitialValues = (initialReviewComment, record) => ({
    reviewComment: initialReviewComment || "",
    acceptAccessToRecord: false,
    acceptAfterPublishRecord: record ? undefined : false,
  });

  const communityTitle = community.metadata.title;
  const modalContent = getModalContent(record, directPublish, communityTitle);

  return (
    <Formik
      initialValues={getInitialValues(initialReviewComment, record)}
      onSubmit={onSubmit}
      validationSchema={getValidationSchema(record)}
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
              {errors && (
                <ErrorMessage
                  header={i18next.t("Unable to submit request.")}
                  content={errors}
                  icon="exclamation"
                  negative
                />
              )}
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
                  <div dangerouslySetInnerHTML={{ __html: publishModalExtraContent }} />
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

SubmitReviewModalComponent.propTypes = {
  isConfirmModalOpen: PropTypes.bool.isRequired,
  community: PropTypes.object.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  initialReviewComment: PropTypes.string,
  publishModalExtraContent: PropTypes.string,
  directPublish: PropTypes.bool,
  errors: PropTypes.string, // TODO FIXME: Use a common error cmp to display errros.
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

export const SubmitReviewModal = Overridable.component(
  "InvenioRdmRecords.SubmitReviewModal.container",
  SubmitReviewModalComponent
);
