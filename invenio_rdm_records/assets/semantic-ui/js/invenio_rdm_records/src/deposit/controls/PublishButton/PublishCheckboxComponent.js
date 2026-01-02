// This file is part of CDS RDM
// Copyright (C) 2025 CERN.
//
// CDS RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _get from "lodash/get";
import { useFormikContext } from "formik";
import React from "react";
import PropTypes from "prop-types";
import { ErrorLabel, RadioField } from "react-invenio-forms";
import { Checkbox, Form } from "semantic-ui-react";

export function ensureUniqueProps(values, propName) {
  const duplicates = values.filter((v, i, arr) => arr.indexOf(v) !== i);
  if (duplicates.length > 0) {
    throw new Error(
      `Extra checkboxes must have unique "${propName}". Duplicates found: ${duplicates}.`
    );
  }
}

export const PublishCheckboxComponent = ({ id, fieldPath, text }) => {
  const { values } = useFormikContext();
  return (
    <Form.Field id={id}>
      <RadioField
        control={Checkbox}
        fieldPath={fieldPath}
        label={text}
        checked={_get(values, fieldPath) === true}
        onChange={({ data, formikProps }) => {
          formikProps.form.setFieldValue(fieldPath, data.checked);
        }}
        optimized
      />
      <ErrorLabel role="alert" fieldPath={fieldPath} className="mt-0 mb-5" />
    </Form.Field>
  );
};

PublishCheckboxComponent.propTypes = {
  id: PropTypes.string.isRequired,
  fieldPath: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
};
