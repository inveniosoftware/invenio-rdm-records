// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Form, Icon } from "semantic-ui-react";

import { ArrayField, GroupField, SelectField, TextField } from "react-invenio-forms";
import { emptyAdditionalTitle } from "./initialValues";
import { LanguagesField } from "../LanguagesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class AdditionalTitlesField extends Component {
  render() {
    const { fieldPath, options, recordUI } = this.props;
    return (
      <ArrayField
        addButtonLabel={i18next.t("Add titles")}
        defaultNewValue={emptyAdditionalTitle}
        fieldPath={fieldPath}
        className="additional-titles"
      >
        {({ arrayHelpers, indexPath }) => {
          const fieldPathPrefix = `${fieldPath}.${indexPath}`;

          return (
            <GroupField fieldPath={fieldPath} optimized>
              <TextField
                fieldPath={`${fieldPathPrefix}.title`}
                label="Additional title"
                required
                width={5}
              />
              <SelectField
                fieldPath={`${fieldPathPrefix}.type`}
                label="Type"
                optimized
                options={options.type}
                required
                width={5}
              />
              <LanguagesField
                serializeSuggestions={(suggestions) =>
                  suggestions.map((item) => ({
                    text: item.title_l10n,
                    value: item.id,
                    fieldPathPrefix: item.id,
                  }))
                }
                initialOptions={
                  recordUI?.additional_titles &&
                  recordUI.additional_titles[indexPath]?.lang
                    ? [recordUI.additional_titles[indexPath].lang]
                    : []
                }
                fieldPath={`${fieldPathPrefix}.lang`}
                label="Language"
                multiple={false}
                placeholder="Select language"
                labelIcon={null}
                clearable
                selectOnBlur={false}
                width={5}
              />
              <Form.Field>
                <Button
                  aria-label={i18next.t("Remove field")}
                  className="close-btn"
                  icon
                  onClick={() => arrayHelpers.remove(indexPath)}
                >
                  <Icon name="close" />
                </Button>
              </Form.Field>
            </GroupField>
          );
        }}
      </ArrayField>
    );
  }
}

AdditionalTitlesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
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
};

AdditionalTitlesField.defaultProps = {
  options: undefined,
  recordUI: undefined,
};
