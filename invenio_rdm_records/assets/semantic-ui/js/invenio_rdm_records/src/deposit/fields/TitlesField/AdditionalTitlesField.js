// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Form } from "semantic-ui-react";
import {
  ArrayField,
  GroupField,
  SelectField,
  TextField,
  showHideOverridable,
  fieldCommonProps,
} from "react-invenio-forms";
import { emptyAdditionalTitle } from "./initialValues";
import { LanguagesField } from "../LanguagesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";

class AdditionalTitlesFieldComponent extends Component {
  render() {
    const { fieldPath, options, recordUI, helpText, addButtonLabel, optimized } =
      this.props;

    return (
      <ArrayField
        addButtonLabel={addButtonLabel}
        helpText={helpText}
        defaultNewValue={emptyAdditionalTitle}
        fieldPath={fieldPath}
        className="additional-titles"
      >
        {({ arrayHelpers, indexPath }) => {
          const fieldPathPrefix = `${fieldPath}.${indexPath}`;
          const languagesInitialOptions =
            recordUI?.additional_titles && recordUI.additional_titles[indexPath]?.lang
              ? [recordUI.additional_titles[indexPath].lang]
              : [];

          return (
            <GroupField fieldPath={fieldPath} optimized={optimized}>
              <TextField
                fieldPath={`${fieldPathPrefix}.title`}
                label={i18next.t("Additional title")}
                required
                width={5}
              />
              <SelectField
                fieldPath={`${fieldPathPrefix}.type`}
                label={i18next.t("Type")}
                optimized={optimized}
                options={options.type}
                required
                width={5}
              />
              <LanguagesField
                serializeSuggestions={(suggestions) =>
                  suggestions.map((item) => ({
                    text: item.title_l10n,
                    value: item.id,
                    key: item.id,
                  }))
                }
                initialOptions={languagesInitialOptions}
                fieldPath={`${fieldPathPrefix}.lang`}
                label={i18next.t("Language")}
                multiple={false}
                placeholder={i18next.t("Select language")}
                labelIcon={null}
                clearable
                selectOnBlur={false}
                width={5}
              />

              <Form.Field>
                <Button
                  aria-label={i18next.t("Remove field")}
                  className="close-btn"
                  icon="close"
                  type="button"
                  onClick={() => arrayHelpers.remove(indexPath)}
                />
              </Form.Field>
            </GroupField>
          );
        }}
      </ArrayField>
    );
  }
}

AdditionalTitlesFieldComponent.propTypes = {
  options: PropTypes.shape({
    type: PropTypes.arrayOf(
      PropTypes.shape({
        icon: PropTypes.string,
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
    lang: PropTypes.arrayOf(
      PropTypes.shape({
        text: PropTypes.string,
        value: PropTypes.string,
      })
    ),
  }),
  recordUI: PropTypes.object,
  addButtonLabel: PropTypes.string,
  optimized: PropTypes.bool,
  ...fieldCommonProps,
};

AdditionalTitlesFieldComponent.defaultProps = {
  options: undefined,
  recordUI: undefined,
  addButtonLabel: i18next.t("Add titles"),
  optimized: true,
};

export const AdditionalTitlesField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.AdditionalTitlesField",
  AdditionalTitlesFieldComponent
);
