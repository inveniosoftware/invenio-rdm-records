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
import { Button, Form, Icon } from "semantic-ui-react";
import Overridable from "react-overridable";
import { ArrayField, GroupField, SelectField, TextField } from "react-invenio-forms";
import { emptyAdditionalTitle } from "./initialValues";
import { LanguagesField } from "../LanguagesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { createFieldComponent, fieldCommonProps } from "../common/fieldComponents";

class AdditionalTitlesFieldComponent extends Component {
  render() {
    const { fieldPath, options, recordUI } = this.props;

    return (
      <Overridable
        id="InvenioRdmRecords.AdditionalTitlesField.list"
        defaultNewValue={emptyAdditionalTitle}
      >
        <ArrayField
          addButtonLabel={i18next.t("Add titles")}
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
              <Overridable id="InvenioRdmRecords.AdditionalTitlesField.item" optimized>
                <GroupField fieldPath={fieldPath} optimized>
                  <Overridable
                    id="InvenioRdmRecords.AdditionalTitlesField.Title.field"
                    required
                    width={5}
                  >
                    <TextField
                      fieldPath={`${fieldPathPrefix}.title`}
                      label={i18next.t("Additional title")}
                      required
                      width={5}
                    />
                  </Overridable>
                  <Overridable
                    id="InvenioRdmRecords.AdditionalTitlesField.Type.field"
                    optimized
                    options={options.type}
                    required
                    width={5}
                  >
                    <SelectField
                      fieldPath={`${fieldPathPrefix}.type`}
                      label={i18next.t("Type")}
                      optimized
                      options={options.type}
                      required
                      width={5}
                    />
                  </Overridable>
                  <Overridable
                    id="InvenioRdmRecords.AdditionalTitlesField.Language.field"
                    multiple={false}
                    labelIcon={null}
                    clearable
                    selectOnBlur={false}
                    width={5}
                    initialOptions={languagesInitialOptions}
                  >
                    <LanguagesField
                      serializeSuggestions={(suggestions) =>
                        suggestions.map((item) => ({
                          text: item.title_l10n,
                          value: item.id,
                          fieldPathPrefix: item.id,
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
                  </Overridable>

                  <Overridable
                    id="InvenioRdmRecords.AdditionalTitlesField.Remove.container"
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
  ...fieldCommonProps,
};

AdditionalTitlesFieldComponent.defaultProps = {
  options: undefined,
  recordUI: undefined,
};

export const AdditionalTitlesField = createFieldComponent(
  "InvenioRdmRecords.AdditionalTitlesField",
  AdditionalTitlesFieldComponent
);
