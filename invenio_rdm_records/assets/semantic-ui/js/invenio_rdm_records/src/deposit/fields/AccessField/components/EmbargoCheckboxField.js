/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { Checkbox } from "semantic-ui-react";
import { FastField } from "formik";
import PropTypes from "prop-types";

function EmbargoCheckboxComponent({
  fieldPath,
  formik,
  checked = false,
  disabled = true,
}) {
  return (
    <Checkbox
      id={fieldPath}
      data-testid="embargo-checkbox-component"
      disabled={disabled}
      checked={checked}
      onChange={() => {
        if (formik.field.value) {
          // NOTE: We reset values, so if embargo filled and user unchecks,
          //       user needs to fill embargo again. Otherwise, lots of
          //       bookkeeping.
          formik.form.setFieldValue("access.embargo", {
            active: false,
          });
        } else {
          formik.form.setFieldValue(fieldPath, true);
        }
      }}
    />
  );
}

EmbargoCheckboxComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  formik: PropTypes.object.isRequired,
  checked: PropTypes.bool,
  disabled: PropTypes.bool,
};

export function EmbargoCheckboxField({ disabled = false, fieldPath, ...props }) {
  // NOTE: See the optimization pattern on AccessRightField for more details.
  //       This makes FastField only render when the things
  //       (access.embargo.active and embargo) it cares about change as it
  //       should be.
  const change = !disabled ? {} : { change: true };

  return (
    <FastField
      name={fieldPath}
      component={(formikProps) => (
        <EmbargoCheckboxComponent
          formik={formikProps}
          fieldPath={fieldPath}
          disabled={disabled}
          {...props}
        />
      )}
      {...change}
    />
  );
}

EmbargoCheckboxField.propTypes = {
  disabled: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
};
