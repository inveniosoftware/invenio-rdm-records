/*
 * SPDX-FileCopyrightText: 2025 CERN.
 * SPDX-License-Identifier: MIT
 */

import _get from "lodash/get";
import { useFormikContext } from "formik";
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
