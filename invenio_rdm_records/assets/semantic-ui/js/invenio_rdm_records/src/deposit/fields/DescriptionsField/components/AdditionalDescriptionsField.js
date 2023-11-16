// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021      Graz University of Technology.
// Copyright (C) 2022      TU Wien.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Form, Grid, Icon } from "semantic-ui-react";
import { ArrayField, SelectField, RichInputField } from "react-invenio-forms";
import { emptyAdditionalDescription } from "./initialValues";
import { LanguagesField } from "../../LanguagesField";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { sortOptions } from "../../../utils";

export class AdditionalDescriptionsField extends Component {
  render() {
    const { fieldPath, options, recordUI, editorConfig } = this.props;
    return (
      <ArrayField
        addButtonLabel={i18next.t("Add description")}
        defaultNewValue={emptyAdditionalDescription}
        fieldPath={fieldPath}
        className="additional-descriptions"
      >
        {({ arrayHelpers, indexPath }) => {
          const fieldPathPrefix = `${fieldPath}.${indexPath}`;

          return (
            <Grid className="description">
              <Grid.Row>
                <Grid.Column mobile={16} tablet={10} computer={12}>
                  <RichInputField
                    fieldPath={`${fieldPathPrefix}.description`}
                    label={i18next.t("Additional Description")}
                    editorConfig={editorConfig}
                    optimized
                    required
                  />
                </Grid.Column>
                <Grid.Column mobile={16} tablet={6} computer={4}>
                  <Form.Field>
                    <Button
                      aria-label={i18next.t("Remove field")}
                      className="close-btn"
                      floated="right"
                      icon
                      onClick={() => arrayHelpers.remove(indexPath)}
                    >
                      <Icon name="close" />
                    </Button>
                  </Form.Field>
                  <SelectField
                    fieldPath={`${fieldPathPrefix}.type`}
                    label={i18next.t("Type")}
                    options={sortOptions(options.type)}
                    required
                    optimized
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
                      recordUI?.additional_descriptions &&
                      recordUI.additional_descriptions[indexPath]?.lang
                        ? [recordUI.additional_descriptions[indexPath].lang]
                        : []
                    }
                    fieldPath={`${fieldPathPrefix}.lang`}
                    label={i18next.t("Language")}
                    multiple={false}
                    placeholder={i18next.t("Select language")}
                    labelIcon=""
                    clearable
                    selectOnBlur={false}
                  />
                </Grid.Column>
              </Grid.Row>
            </Grid>
          );
        }}
      </ArrayField>
    );
  }
}

AdditionalDescriptionsField.propTypes = {
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
  }).isRequired,
  recordUI: PropTypes.object,
  editorConfig: PropTypes.object,
};

AdditionalDescriptionsField.defaultProps = {
  recordUI: {},
  editorConfig: undefined,
};
