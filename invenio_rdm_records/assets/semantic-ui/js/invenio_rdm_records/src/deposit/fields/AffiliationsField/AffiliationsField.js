/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { Component } from "react";
import {
  FieldLabel,
  RemoteSelectField,
  AffiliationsSuggestions,
} from "react-invenio-forms";
import { Field, getIn } from "formik";
import { i18next } from "@translations/invenio_rdm_records/i18next";

/**Affiliation input component */
export function AffiliationsField({fieldPath, selectRef = undefined}) {
  return (
      <Field name={fieldPath}>
        {({ form: { values } }) => {
          return (
            <RemoteSelectField
              fieldPath={fieldPath}
              suggestionAPIUrl="/api/affiliations"
              suggestionAPIHeaders={{
                Accept: "application/vnd.inveniordm.v1+json",
              }}
              initialSuggestions={getIn(values, fieldPath, [])}
              serializeSuggestions={(affiliations) => {
                return AffiliationsSuggestions(affiliations, true);
              }}
              placeholder={i18next.t("Search or create affiliation")}
              label={
                <FieldLabel
                  htmlFor={`${fieldPath}.name`}
                  label={i18next.t("Affiliations")}
                />
              }
              noQueryMessage={i18next.t("Search for affiliations..")}
              allowAdditions
              clearable
              multiple
              onValueChange={({ formikProps }, selectedSuggestions) => {
                formikProps.form.setFieldValue(
                  fieldPath,
                  // save the suggestion objects so we can extract information
                  // about which value added by the user
                  selectedSuggestions
                );
              }}
              value={getIn(values, fieldPath, []).map(
                ({ id, name, text }) => id ?? name ?? text
              )}
              ref={selectRef}
              // Disable UI-side filtering of search results
              search={(options) => options}
            />
          );
        }}
      </Field>
    );
}

AffiliationsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  selectRef: PropTypes.object,
};

