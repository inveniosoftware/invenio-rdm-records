/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { FastField } from "formik";
import PropTypes from "prop-types";
import { Component } from "react";
import { RequiredPIDField } from "./RequiredPIDField";
import { OptionalPIDField } from "./OptionalPIDField";

/**
 * Render the PIDField using a custom Formik component
 */
export function PIDField({canBeManaged = true, canBeUnmanaged = true, fieldPath, required = false}) {
  const validatePropValues = () => {
    const { canBeManaged, canBeUnmanaged, fieldPath } = this.props;

    if (!canBeManaged && !canBeUnmanaged) {
      throw Error(`${fieldPath} must be managed, unmanaged or both.`);
    }
  };

  const cmp = required ? RequiredPIDField : OptionalPIDField;

    return <FastField name={fieldPath} component={cmp} {...props} />;
}

PIDField.propTypes = {
  btnLabelDiscardPID: PropTypes.string,
  btnLabelGetPID: PropTypes.string,
  canBeManaged: PropTypes.bool,
  canBeUnmanaged: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
  fieldLabel: PropTypes.string.isRequired,
  isEditingPublishedRecord: PropTypes.bool.isRequired,
  managedHelpText: PropTypes.string,
  pidIcon: PropTypes.string,
  pidLabel: PropTypes.string.isRequired,
  pidPlaceholder: PropTypes.string,
  pidType: PropTypes.string.isRequired,
  required: PropTypes.bool,
  unmanagedHelpText: PropTypes.string,
  record: PropTypes.object.isRequired,
  doiDefaultSelection: PropTypes.object.isRequired,
  optionalDOItransitions: PropTypes.object.isRequired,
};

