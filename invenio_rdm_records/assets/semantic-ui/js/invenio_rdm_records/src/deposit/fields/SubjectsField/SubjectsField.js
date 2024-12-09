// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2024 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import {
  FieldLabel,
  GroupField,
  SubjectAutocompleteDropdown,
} from "react-invenio-forms";
import { Form } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class SubjectsField extends Component {
  state = {
    limitTo: "all",
  };

  render() {
    const { fieldPath, label, labelIcon, limitToOptions, ...dropdownProps } =
      this.props;
    const { limitTo } = this.state;
    const displaySuggestFromField = limitToOptions.length > 2; // 2 because of "all", that is always present
    return (
      <GroupField className="main-group-field">
        {displaySuggestFromField && (
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
        )}

        <SubjectAutocompleteDropdown
          {...dropdownProps}
          fieldPath={fieldPath}
          label={
            !displaySuggestFromField && (
              <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            ) // Add label to second field if suggest from is hidden
          }
          limitTo={limitTo}
          width={displaySuggestFromField ? 11 : 16}
        />
      </GroupField>
    );
  }
}

SubjectsField.propTypes = {
  limitToOptions: PropTypes.array.isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  placeholder: PropTypes.string,
};

SubjectsField.defaultProps = {
  label: i18next.t("Keywords and subjects"),
  labelIcon: "tag",
  placeholder: i18next.t("Search for a subject by name"),
};
