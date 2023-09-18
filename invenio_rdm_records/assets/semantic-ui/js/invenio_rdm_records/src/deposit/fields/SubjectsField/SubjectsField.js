// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { FieldLabel, GroupField, RemoteSelectField } from "react-invenio-forms";
import { Form } from "semantic-ui-react";
import { Field, getIn } from "formik";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class SubjectsField extends Component {
  state = {
    limitTo: "all",
  };

  serializeSubjects = (subjects) =>
    subjects.map((subject) => {
      const scheme = subject.scheme ? `(${subject.scheme}) ` : "";
      return {
        text: scheme + subject.subject,
        value: subject.subject,
        key: subject.subject,
        ...(subject.id ? { id: subject.id } : {}),
        subject: subject.subject,
      };
    });

  prepareSuggest = (searchQuery) => {
    const { limitTo } = this.state;

    const prefix = limitTo === "all" ? "" : `${limitTo}:`;
    return `${prefix}${searchQuery}`;
  };

  render() {
    const {
      fieldPath,
      label,
      labelIcon,
      required,
      multiple,
      placeholder,
      clearable,
      limitToOptions,
    } = this.props;
    return (
      <GroupField className="main-group-field">
        <Form.Field width={5} className="subjects-field">
          <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
          <GroupField>
            <Form.Field
              width={8}
              style={{ marginBottom: "auto", marginTop: "auto" }}
              className="p-0"
            >
              {i18next.t("Suggest from")}
            </Form.Field>
            <Form.Dropdown
              className="p-0"
              defaultValue={limitToOptions[0].value}
              fluid
              aria-label={i18next.t("Suggest from")}
              onChange={(event, data) => this.setState({ limitTo: data.value })}
              options={limitToOptions}
              selection
              width={8}
            />
          </GroupField>
        </Form.Field>
        <Field name={fieldPath}>
          {({ form: { values } }) => {
            return (
              <RemoteSelectField
                clearable={clearable}
                fieldPath={fieldPath}
                initialSuggestions={getIn(values, fieldPath, [])}
                multiple={multiple}
                noQueryMessage={i18next.t("Search or create subjects...")}
                placeholder={placeholder}
                preSearchChange={this.prepareSuggest}
                required={required}
                serializeSuggestions={this.serializeSubjects}
                serializeAddedValue={(value) => ({
                  text: value,
                  value: value,
                  key: value,
                  subject: value,
                })}
                suggestionAPIUrl="/api/subjects"
                onValueChange={({ formikProps }, selectedSuggestions) => {
                  formikProps.form.setFieldValue(
                    fieldPath,
                    // save the suggestion objects so we can extract information
                    // about which value added by the user
                    selectedSuggestions
                  );
                }}
                value={getIn(values, fieldPath, []).map((val) => val.subject)}
                label={
                  <>
                    {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
                    <label className="mobile-hidden">&nbsp;</label>
                  </>
                } /** For alignment purposes */
                allowAdditions
                width={11}
              />
            );
          }}
        </Field>
      </GroupField>
    );
  }
}

SubjectsField.propTypes = {
  limitToOptions: PropTypes.array.isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  multiple: PropTypes.bool,
  clearable: PropTypes.bool,
  placeholder: PropTypes.string,
};

SubjectsField.defaultProps = {
  required: false,
  label: i18next.t("Keywords and subjects"),
  labelIcon: "tag",
  multiple: true,
  clearable: true,
  placeholder: i18next.t("Search for a subject by name"),
};
