// This file is part of Invenio-RDM-Records
// Copyright (C) 2025 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import Overridable from "react-overridable";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Button, Icon, Message, Modal, Form } from "semantic-ui-react";
import * as Yup from "yup";
import {
  PublishCheckboxComponent,
  ensureUniqueProps,
} from "./PublishCheckboxComponent";

class PublishModalComponent extends Component {
  constructor(props) {
    super(props);
    const { extraCheckboxes } = props;
    this.validationSchema = Yup.object().shape({}).noUnknown();
    this.initialValues = {};

    // Get extra checkbox component and define its schema and defaults
    if (extraCheckboxes.length > 0) {
      // Validate id and fieldpath are unique
      const fieldPaths = extraCheckboxes.map((checkbox) => checkbox.fieldPath);
      ensureUniqueProps(fieldPaths, "fieldPath");
      const ids = extraCheckboxes.map((checkbox) => checkbox.id);
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

  render() {
    const {
      isConfirmModalOpen,
      onClose,
      onSubmit,
      publishModalExtraContent,
      buttonLabel,
      extraCheckboxes,
      beforeContent,
      afterContent,
    } = this.props;
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
};

PublishModalComponent.defaultProps = {
  publishModalExtraContent: "",
  buttonLabel: i18next.t("Publish"),
  extraCheckboxes: [],
  beforeContent: () => undefined,
  afterContent: () => undefined,
};

export const PublishModal = Overridable.component(
  "InvenioRdmRecords.PublishModal.container",
  PublishModalComponent
);
