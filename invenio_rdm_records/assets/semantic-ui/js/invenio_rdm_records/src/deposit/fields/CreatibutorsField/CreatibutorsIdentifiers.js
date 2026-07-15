/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { Component } from "react";
import PropTypes from "prop-types";
import { SelectField } from "react-invenio-forms";
import _unickBy from "lodash/unionBy";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export function CreatibutorsIdentifiers({initialOptions, fieldPath, label = i18next.t("Identifiers"), placeholder = i18next.t("e.g. ORCID, ISNI or GND.")}) {
  const [selectedOptions, setSelectedOptions] = React.useState(initialOptions);

  const handleIdentifierAddition = (e, { value }) => {
    setSelectedOptions(prevSelectedOptions => ({
      selectedOptions: _unickBy(
        [
          {
            text: value,
            value: value,
            key: value,
          },
          ...prevSelectedOptions,
        ],
        "value"
      ),
    }));
  };

  const valuesToOptions = (options) => options.map((option) => ({
      text: option,
      value: option,
      key: option,
    }));

  const handleChange = ({ data, formikProps }) => {
    const { fieldPath } = this.props;
    setSelectedOptions(this.valuesToOptions(data.value));
    formikProps.form.setFieldValue(fieldPath, data.value);
  };

  return (
      <SelectField
        fieldPath={fieldPath}
        label={label}
        options={selectedOptions}
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

