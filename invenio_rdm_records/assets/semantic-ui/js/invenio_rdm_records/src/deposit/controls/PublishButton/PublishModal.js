/*
 * SPDX-FileCopyrightText: 2025 CERN.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import Overridable from "react-overridable";
import PropTypes from "prop-types";
import { Component } from "react";
import { Button, Icon, Message, Modal, Form } from "semantic-ui-react";
import * as Yup from "yup";
import {
  PublishCheckboxComponent,
  ensureUniqueProps,
} from "./PublishCheckboxComponent";
import { PreviewButton } from "../PreviewButton";

const publishModalComponentDefaultPropExtraCheckboxes = [];
const publishModalComponentDefaultPropBeforeContent = () => undefined;
const publishModalComponentDefaultPropAfterContent = () => undefined;
function PublishModalComponent({extraCheckboxes = publishModalComponentDefaultPropExtraCheckboxes, isConfirmModalOpen, onClose, onSubmit, publishModalExtraContent = "", buttonLabel = i18next.t("Publish"), beforeContent = publishModalComponentDefaultPropBeforeContent, afterContent = publishModalComponentDefaultPropAfterContent, depositFormHandleSubmit = undefined}) {
  return (
      <Formik
        initialValues={initialValues}
        onSubmit={onSubmit}
        validationSchema={validationSchema}
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
                <Form>
                  {beforeContent && <div>{beforeContent()}</div>}
                  {extraCheckboxes.length > 0 &&
                    extraCheckboxes.map((checkbox) => (
                      <PublishCheckboxComponent
                        id={`${checkbox.fieldPath}-checkbox`}
                        key={checkbox.fieldPath}
                        fieldPath={checkbox.fieldPath}
                        text={checkbox.text}
                      />
                    ))}
                  {afterContent && <div>{afterContent()}</div>}
                </Form>
                {publishModalExtraContent && (
                  <div dangerouslySetInnerHTML={{ __html: publishModalExtraContent }} />
                )}
              </Modal.Content>
              <Modal.Actions>
                <Button onClick={onClose} floated="left">
                  {i18next.t("Cancel")}
                </Button>
                <PreviewButton depositFormHandleSubmit={depositFormHandleSubmit} />
                <Button
                  name="publish"
                  onClick={(event) => {
                    handleSubmit(event);
                  }}
                  positive
                  content={buttonLabel}
                />
              </Modal.Actions>
            </Modal>
          );
        }}
      </Formik>
    );
}

PublishModalComponent.propTypes = {
  isConfirmModalOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  publishModalExtraContent: PropTypes.string,
  buttonLabel: PropTypes.string,
  extraCheckboxes: PropTypes.arrayOf(
    PropTypes.shape({
      fieldPath: PropTypes.string,
      text: PropTypes.string,
    })
  ),
  beforeContent: PropTypes.func,
  afterContent: PropTypes.func,
  depositFormHandleSubmit: PropTypes.func,
};

export const PublishModal = Overridable.component(
  "InvenioRdmRecords.PublishModal.container",
  PublishModalComponent
);
