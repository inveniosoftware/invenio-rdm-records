// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import Overridable from "react-overridable";
import { TextField, GroupField, ArrayField, FieldLabel } from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";
import { emptyReference } from "./initialValues";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { createFieldComponent, fieldCommonProps } from "../common/fieldComponents";

class ReferencesFieldComponent extends Component {
  render() {
    const { fieldPath, label, labelIcon, required, disabled, showEmptyValue } =
      this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.ReferencesField.list"
        defaultNewValue={emptyReference}
        required={required}
        disabled={disabled}
        showEmptyValue={showEmptyValue}
      >
        <ArrayField
          addButtonLabel={i18next.t("Add reference")}
          defaultNewValue={emptyReference}
          fieldPath={fieldPath}
          label={
            <Overridable
              id="InvenioRdmRecords.ReferencesField.label"
              labelIcon={labelIcon}
              label={label}
            >
              <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            </Overridable>
          }
          required={required}
          disabled={disabled}
          showEmptyValue={showEmptyValue}
        >
          {({ arrayHelpers, indexPath }) => {
            const fieldPathPrefix = `${fieldPath}.${indexPath}`;

            return (
              <Overridable id="InvenioRdmRecords.ReferencesField.item" optimized>
                <GroupField optimized>
                  <Overridable
                    id="InvenioRdmRecords.ReferencesField.Reference.field"
                    required
                    width={16}
                  >
                    <TextField
                      fieldPath={`${fieldPathPrefix}.reference`}
                      label={i18next.t("Reference string")}
                      required
                      width={16}
                    />
                  </Overridable>

                  <Overridable
                    id="InvenioRdmRecords.ReferencesField.Remove.container"
                    icon="close"
                  >
                    <Form.Field>
                      <Button
                        aria-label={i18next.t("Remove field")}
                        className="close-btn"
                        icon="close"
                        onClick={() => arrayHelpers.remove(indexPath)}
                      />
                    </Form.Field>
                  </Overridable>
                </GroupField>
              </Overridable>
            );
          }}
        </ArrayField>
      </Overridable>
    );
  }
}

ReferencesFieldComponent.propTypes = {
  showEmptyValue: PropTypes.bool,
  ...fieldCommonProps,
};

ReferencesFieldComponent.defaultProps = {
  label: i18next.t("References"),
  labelIcon: "bookmark",
  required: false,
  showEmptyValue: false,
};

export const ReferencesField = createFieldComponent(
  "InvenioRdmRecords.ReferencesField",
  ReferencesFieldComponent
);
