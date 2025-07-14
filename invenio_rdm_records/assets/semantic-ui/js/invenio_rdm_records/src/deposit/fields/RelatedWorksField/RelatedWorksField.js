// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";

import {
  TextField,
  GroupField,
  ArrayField,
  FieldLabel,
  SelectField,
} from "react-invenio-forms";
import { Button, Form, Icon } from "semantic-ui-react";
import Overridable from "react-overridable";
import { emptyRelatedWork } from "./initialValues";
import { ResourceTypeField } from "../ResourceTypeField";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { createFieldComponent, fieldCommonProps } from "../common/fieldComponents";

class RelatedWorksFieldComponent extends Component {
  render() {
    const { fieldPath, label, labelIcon, required, disabled, options, showEmptyValue } =
      this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.RelatedWorksField.container"
        required={required}
        disabled={disabled}
        showEmptyValue={showEmptyValue}
        defaultNewValue={emptyRelatedWork}
        labelIcon={labelIcon}
        label={label}
      >
        <>
          <Overridable id="InvenioRdmRecords.RelatedWorksField.help">
            <label className="helptext" style={{ marginBottom: "10px" }}>
              {i18next.t(
                "Specify identifiers of related works. Supported identifiers include DOI, Handle, ARK, PURL, ISSN, ISBN, PubMed ID, PubMed Central ID, ADS Bibliographic Code, arXiv, Life Science Identifiers (LSID), EAN-13, ISTC, URNs, and URLs."
              )}
            </label>
          </Overridable>

          <Overridable
            id="InvenioRdmRecords.RelatedWorksField.list"
            required={required}
            disabled={disabled}
            showEmptyValue={showEmptyValue}
            defaultNewValue={emptyRelatedWork}
            labelIcon={labelIcon}
            label={label}
          >
            <ArrayField
              addButtonLabel={i18next.t("Add related work")}
              defaultNewValue={emptyRelatedWork}
              fieldPath={fieldPath}
              label={
                <Overridable
                  id="InvenioRdmRecords.RelatedWorksField.label"
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
                  <Overridable id="InvenioRdmRecords.RelatedWorksField.item" optimized>
                    <GroupField optimized>
                      <Overridable
                        id="InvenioRdmRecords.RelatedWorksField.Relation.field"
                        clearable
                        optimized
                        options={options.relations}
                        required
                        width={3}
                      >
                        <SelectField
                          clearable
                          fieldPath={`${fieldPathPrefix}.relation_type`}
                          label={i18next.t("Relation")}
                          aria-label={i18next.t("Relation")}
                          optimized
                          options={options.relations}
                          placeholder={{
                            role: "option",
                            content: "Select relation...",
                          }}
                          required
                          width={3}
                        />
                      </Overridable>

                      <Overridable
                        id="InvenioRdmRecords.RelatedWorksField.Identifier.field"
                        required
                        width={4}
                      >
                        <TextField
                          fieldPath={`${fieldPathPrefix}.identifier`}
                          label={i18next.t("Identifier")}
                          required
                          width={4}
                        />
                      </Overridable>

                      <Overridable
                        id="InvenioRdmRecords.RelatedWorksField.Scheme.field"
                        clearable
                        optimized
                        options={options.scheme}
                        required
                        width={2}
                      >
                        <SelectField
                          clearable
                          fieldPath={`${fieldPathPrefix}.scheme`}
                          label={i18next.t("Scheme")}
                          aria-label={i18next.t("Scheme")}
                          optimized
                          options={options.scheme}
                          required
                          width={2}
                        />
                      </Overridable>

                      <Overridable
                        id="InvenioRdmRecords.RelatedWorksField.ResourceType.field"
                        clearable
                        options={options.resource_type}
                        labelIcon=""
                        width={7}
                      >
                        <ResourceTypeField
                          clearable
                          fieldPath={`${fieldPathPrefix}.resource_type`}
                          labelIcon="" // Otherwise breaks alignment
                          options={options.resource_type}
                          width={7}
                          labelclassname="small field-label-class"
                        />
                      </Overridable>

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
        </>
      </Overridable>
    );
  }
}

RelatedWorksFieldComponent.propTypes = {
  options: PropTypes.object.isRequired,
  showEmptyValue: PropTypes.bool,
  ...fieldCommonProps,
};

RelatedWorksFieldComponent.defaultProps = {
  label: i18next.t("Related works"),
  labelIcon: "barcode",
  required: undefined,
  showEmptyValue: false,
};

export const RelatedWorksField = createFieldComponent(
  "InvenioRdmRecords.RelatedWorksField",
  RelatedWorksFieldComponent
);
