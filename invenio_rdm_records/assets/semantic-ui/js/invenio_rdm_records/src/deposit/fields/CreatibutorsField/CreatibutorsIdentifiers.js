/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { useFormikContext } from "formik";
import { SelectField } from "react-invenio-forms";
import _get from "lodash/get";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export function CreatibutorsIdentifiers({
  initialOptions,
  fieldPath,
  label = i18next.t("Identifiers"),
  placeholder = i18next.t("e.g. ORCID, ISNI or GND."),
}) {
  const { values } = useFormikContext();
  const identifiers = _get(values, fieldPath);

  const valuesToOptions = (options) =>
    options.map((option) => ({
      text: option,
      value: option,
      key: option,
    }));

  const handleChange = ({ data, formikProps }) => {
    formikProps.form.setFieldValue(fieldPath, data.value);
  };

  const handleIdentifierAddition = ({ formikProps }, { value }) => {
    formikProps.form.setFieldValue(
      fieldPath,
      Array.from(new Set([value, ..._get(formikProps.form.values, fieldPath, [])]))
    );
  };

  return (
    <SelectField
      fieldPath={fieldPath}
      label={label}
      options={
        identifiers === undefined ? initialOptions : valuesToOptions(identifiers)
      }
      placeholder={placeholder}
      noResultsMessage={i18next.t("Type the value of an identifier...")}
      search
      multiple
      selection
      allowAdditions
      onChange={handleChange}
      // `icon` is set to `null` in order to hide the dropdown default icon
      icon={null}
      onAddItem={handleIdentifierAddition}
      optimized
    />
  );
}

CreatibutorsIdentifiers.propTypes = {
  initialOptions: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      text: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
    })
  ).isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  placeholder: PropTypes.string,
};
