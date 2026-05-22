/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import React, { Component } from "react";
import { Checkbox } from "semantic-ui-react";
import { FastField } from "formik";
import PropTypes from "prop-types";

class EmbargoCheckboxComponent extends Component {
  render() {
    const { fieldPath, formik, checked, disabled } = this.props;
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
}

EmbargoCheckboxComponent.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  formik: PropTypes.object.isRequired,
  checked: PropTypes.bool,
  disabled: PropTypes.bool,
};

EmbargoCheckboxComponent.defaultProps = {
  checked: false,
  disabled: true,
};

export class EmbargoCheckboxField extends Component {
  render() {
    const { disabled: embargoDisabled, fieldPath } = this.props;

    // NOTE: See the optimization pattern on AccessRightField for more details.
    //       This makes FastField only render when the things
    //       (access.embargo.active and embargo) it cares about change as it
    //       should be.
    const change = !embargoDisabled ? {} : { change: true };

    return (
      <FastField
        name={fieldPath}
        component={(formikProps) => (
          <EmbargoCheckboxComponent formik={formikProps} {...this.props} />
        )}
        {...change}
      />
    );
  }
}

EmbargoCheckboxField.propTypes = {
  disabled: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
};

EmbargoCheckboxField.defaultProps = {
  disabled: false,
};
