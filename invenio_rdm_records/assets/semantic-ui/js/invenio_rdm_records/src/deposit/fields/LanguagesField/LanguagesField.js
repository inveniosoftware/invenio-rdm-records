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
  FieldLabel,
  RemoteSelectField,
  showHideOverridable,
  fieldCommonProps,
} from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import Overridable from "react-overridable";

class LanguagesFieldComponent extends Component {
  render() {
    const {
      fieldPath,
      label,
      labelIcon,
      multiple,
      placeholder,
      clearable,
      initialOptions,
      serializeSuggestions: serializeSuggestionsFunc,
      required,
      disabled,
      helpText,
      noQueryMessage,
      ...uiProps
    } = this.props;
    const serializeSuggestions = serializeSuggestionsFunc || null;

    return (
      <Overridable
        id="InvenioRdmRecords.DepositForm.LanguagesField.Input"
        fieldPath={fieldPath}
        placeholder={placeholder}
        required={required}
        disabled={disabled}
        clearable={clearable}
        multiple={multiple}
        initialSuggestions={initialOptions}
        labelIcon={labelIcon}
        label={label}
        helpText={helpText}
        noQueryMessage={noQueryMessage}
      >
        <RemoteSelectField
          fieldPath={fieldPath}
          suggestionAPIUrl="/api/vocabularies/languages"
          suggestionAPIHeaders={{
            Accept: "application/vnd.inveniordm.v1+json",
          }}
          placeholder={placeholder}
          helpText={helpText}
          required={required}
          disabled={disabled}
          clearable={clearable}
          multiple={multiple}
          initialSuggestions={initialOptions}
          label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
          noQueryMessage={noQueryMessage}
          {...(serializeSuggestions && { serializeSuggestions })}
          {...uiProps}
        />
      </Overridable>
    );
  }
}

LanguagesFieldComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  multiple: PropTypes.bool,
  clearable: PropTypes.bool,
  placeholder: PropTypes.string,
  noQueryMessage: PropTypes.string,
  initialOptions: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string,
      value: PropTypes.string,
      text: PropTypes.string,
    })
  ),
  serializeSuggestions: PropTypes.func,
  ...fieldCommonProps,
};

LanguagesFieldComponent.defaultProps = {
  label: i18next.t("Languages"),
  labelIcon: "globe",
  multiple: true,
  clearable: true,
  placeholder: i18next.t('Search for a language by name (e.g "eng", "fr" or "Polish")'),
  noQueryMessage: i18next.t("Search for languages..."),
  required: false,
  initialOptions: undefined,
  serializeSuggestions: undefined,
};

export const LanguagesField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.LanguagesField",
  LanguagesFieldComponent
);
