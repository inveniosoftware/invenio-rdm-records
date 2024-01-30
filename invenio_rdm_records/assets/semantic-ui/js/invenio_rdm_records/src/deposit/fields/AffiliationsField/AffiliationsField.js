// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import { FieldLabel, RemoteSelectField } from "react-invenio-forms";
import { Field, getIn } from "formik";
import { i18next } from "@translations/invenio_rdm_records/i18next";

/**Affiliation input component */
export class AffiliationsField extends Component {
  serializeAffiliations = (affiliations) =>
    affiliations.map((affiliation) => ({
      text: affiliation.acronym
        ? `${affiliation.name} (${affiliation.acronym})`
        : affiliation.name,
      value: affiliation.id || affiliation.name,
      key: affiliation.id,
      id: affiliation.id,
      name: affiliation.name,
    }));

  render() {
    const { fieldPath, selectRef } = this.props;
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
              serializeSuggestions={this.serializeAffiliations}
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
                (val) => val.id || val.text || val.name
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
}

AffiliationsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  selectRef: PropTypes.object,
};

AffiliationsField.defaultProps = {
  selectRef: undefined,
};
