// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import _get from "lodash/get";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Trans } from "react-i18next";
import {
  ErrorLabel,
  RadioField,
  TextAreaField,
  ErrorMessage,
} from "react-invenio-forms";
import { Button, Checkbox, Form, Icon, Message, Modal } from "semantic-ui-react";
import * as Yup from "yup";

export class SubmitReviewModal extends Component {
  componentDidMount() {
    // A11y: Focus the first input field in the form
    const firstFormFieldWrap = document.getElementById("accept-access-checkbox");
    const checkboxElem = firstFormFieldWrap.querySelector("input");
    checkboxElem?.focus();
  }

  ConfirmSubmitReviewSchema = Yup.object({
    acceptAccessToRecord: Yup.bool().oneOf([true], i18next.t("You must accept this.")),
    reviewComment: Yup.string(),
  });

  render() {
    const {
      initialReviewComment,
      isConfirmModalOpen,
      community,
      onClose,
      onSubmit,
      publishModalExtraContent,
      directPublish,
      errors,
      loading,
      record,
    } = this.props;
    const communityTitle = community.metadata.title;

    const directPublishCase = () => {
      headerTitle = i18next.t("Publish to community");
      msgWarningTitle = i18next.t(
        "Before publishing to the community, please read and check the following:"
      );
      msgWarningText1 = i18next.t(
        "Your upload will be <bold>immediately published</bold> in '{{communityTitle}}'. You will no longer be able to change the files in the upload! However, you will still be able to update the record's metadata later.",
        { communityTitle }
      );
      submitBtnLbl = i18next.t("Publish record to community");
    };

    let headerTitle, msgWarningTitle, msgWarningText1, submitBtnLbl;
    // if record is passed and it is published
    if (record?.is_published) {
      headerTitle = i18next.t("Submit to community");
      msgWarningTitle = i18next.t(
        "Before submitting to community, please read and check the following:"
      );
      submitBtnLbl = i18next.t("Submit to community");
    }
    // else record is a draft
    else {
      if (directPublish) {
        directPublishCase();
      } else {
        headerTitle = i18next.t("Submit for review");
        msgWarningTitle = i18next.t(
          "Before requesting review, please read and check the following:"
        );
        msgWarningText1 = i18next.t(
          "If your upload is accepted by the community curators, it will be <bold>immediately published</bold>. Before that, you will still be able to modify metadata and files of this upload."
        );
        submitBtnLbl = i18next.t("Submit record for review");
      }
    }

    // acceptAfterPublishRecord checkbox is absent if record is published
    const schema = () => {
      if (record) {
        return this.ConfirmSubmitReviewSchema;
      } else {
        const additionalValidationSchema = Yup.object({
          acceptAfterPublishRecord: Yup.bool().oneOf(
            [true],
            i18next.t("You must accept this.")
          ),
        });
        return this.ConfirmSubmitReviewSchema.concat(additionalValidationSchema);
      }
    };

    return (
      <Formik
        initialValues={{
          acceptAccessToRecord: false,
          acceptAfterPublishRecord: false,
          reviewComment: initialReviewComment || "",
        }}
        onSubmit={onSubmit}
        validationSchema={schema}
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
              <Modal.Header>{headerTitle}</Modal.Header>
              <Modal.Content>
                {errors && <ErrorMessage errors={errors} />}
                <Message visible warning>
                  <p>
                    <Icon name="warning sign" />
                    {msgWarningTitle}
                  </p>
                </Message>
                <Form>
                  <Form.Field id="accept-access-checkbox">
                    <RadioField
                      control={Checkbox}
                      fieldPath="acceptAccessToRecord"
                      label={
                        <Trans
                          defaults={i18next.t(
                            "The '{{communityTitle}}' curators will have access to <bold>view</bold> and <bold>edit</bold> your upload's metadata and files.",
                            { communityTitle }
                          )}
                          values={{
                            communityTitle,
                          }}
                          components={{ bold: <b /> }}
                          shouldUnescape
                        />
                      }
                      checked={_get(values, "acceptAccessToRecord") === true}
                      onChange={({ data, formikProps }) => {
                        formikProps.form.setFieldValue(
                          "acceptAccessToRecord",
                          data.checked
                        );
                      }}
                      optimized
                    />
                    <ErrorLabel
                      role="alert"
                      fieldPath="acceptAccessToRecord"
                      className="mt-0 mb-5"
                    />
                  </Form.Field>
                  {!record && (
                    <Form.Field>
                      <RadioField
                        control={Checkbox}
                        fieldPath="acceptAfterPublishRecord"
                        label={
                          <Trans
                            defaults={msgWarningText1}
                            values={{
                              communityTitle: communityTitle,
                            }}
                            components={{ bold: <b /> }}
                          />
                        }
                        checked={_get(values, "acceptAfterPublishRecord") === true}
                        onChange={({ data, formikProps }) => {
                          formikProps.form.setFieldValue(
                            "acceptAfterPublishRecord",
                            data.checked
                          );
                        }}
                        optimized
                      />
                      <ErrorLabel
                        role="alert"
                        fieldPath="acceptAfterPublishRecord"
                        className="mt-0 mb-5"
                      />
                    </Form.Field>
                  )}
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
                  content={submitBtnLbl}
                />
              </Modal.Actions>
            </Modal>
          );
        }}
      </Formik>
    );
  }
}

SubmitReviewModal.propTypes = {
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
};

SubmitReviewModal.defaultProps = {
  initialReviewComment: "",
  publishModalExtraContent: undefined,
  directPublish: false,
  errors: undefined,
  loading: false,
};
