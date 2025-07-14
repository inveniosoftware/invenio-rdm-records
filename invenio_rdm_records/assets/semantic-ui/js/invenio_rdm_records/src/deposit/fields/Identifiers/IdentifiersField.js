// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import {
  ArrayField,
  FieldLabel,
  GroupField,
  SelectField,
  TextField,
} from "react-invenio-forms";
import { Button, Form } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { emptyIdentifier } from "./initialValues";
import Overridable from "react-overridable";
import { createFieldComponent, fieldCommonProps } from "../common/fieldComponents";

class IdentifiersFieldComponent extends Component {
  render() {
    const {
      fieldPath,
      label,
      labelIcon,
      required,
      disabled,
      schemeOptions,
      showEmptyValue,
    } = this.props;
    return (
      <Overridable
        id="InvenioRdmRecords.IdentifiersField.list"
        defaultNewValue={emptyIdentifier}
        labelIcon={labelIcon}
        label={label}
        required={required}
        disabled={disabled}
        showEmptyValue={showEmptyValue}
        options={schemeOptions}
      >
        <ArrayField
          addButtonLabel={i18next.t("Add identifier")}
          defaultNewValue={emptyIdentifier}
          fieldPath={fieldPath}
          label={
            <Overridable
              id="InvenioRdmRecords.IdentifiersField.label"
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
              <Overridable
                id="InvenioRdmRecords.IdentifiersField.item"
                optimized={false}
              >
                <GroupField>
                  <Overridable
                    id="InvenioRdmRecords.IdentifiersField.Identifier.field"
                    required
                    width={11}
                  >
                    <TextField
                      fieldPath={`${fieldPathPrefix}.identifier`}
                      label={i18next.t("Identifier")}
                      required
                      width={11}
                    />
                  </Overridable>
                  {schemeOptions && (
                    <Overridable
                      id="InvenioRdmRecords.IdentifiersField.Scheme.select"
                      options={schemeOptions}
                      optimized
                      required
                      width={5}
                    >
                      <SelectField
                        fieldPath={`${fieldPathPrefix}.scheme`}
                        label={i18next.t("Scheme")}
                        aria-label={i18next.t("Scheme")}
                        options={schemeOptions}
                        optimized
                        required
                        width={5}
                      />
                    </Overridable>
                  )}
                  {!schemeOptions && (
                    <Overridable
                      id="InvenioRdmRecords.IdentifiersField.Scheme.text"
                      required
                      width={5}
                    >
                      <TextField
                        fieldPath={`${fieldPathPrefix}.scheme`}
                        label={i18next.t("Scheme")}
                        aria-label={i18next.t("Scheme")}
                        required
                        width={5}
                      />
                    </Overridable>
                  )}

                  <Overridable
                    id="InvenioRdmRecords.RelatedWorksField.Remove.container"
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

IdentifiersFieldComponent.propTypes = {
  schemeOptions: PropTypes.arrayOf(
    PropTypes.shape({
      text: PropTypes.string,
      value: PropTypes.string,
    })
  ),
  showEmptyValue: PropTypes.bool,
  ...fieldCommonProps,
};

IdentifiersFieldComponent.defaultProps = {
  label: i18next.t("Identifiers"),
  labelIcon: "barcode",
  required: false,
  schemeOptions: undefined,
  showEmptyValue: false,
};

export const IdentifiersField = createFieldComponent(
  "InvenioRdmRecords.IdentifiersField",
  IdentifiersFieldComponent
);
