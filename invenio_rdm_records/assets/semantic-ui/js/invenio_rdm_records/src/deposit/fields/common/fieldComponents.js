// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React from "react";
import Overridable from "react-overridable";

// Props used for fields that are mandatory for all records
export const mandatoryFieldCommonProps = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  helpText: PropTypes.string,
  placeholder: PropTypes.string,
};

// Also includes props that allow not including a field in the form, which are not applicable
// to mandatory fields.
export const fieldCommonProps = {
  ...mandatoryFieldCommonProps,
  hidden: PropTypes.bool,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
};

export const createCommonDepositFieldComponent = (id, Child) => {
  const Component = ({ hidden, ...props }) => {
    if (props.disabled && props.required) {
      throw new Error(`Cannot make field component ${id} both required and disabled`);
    }

    if (hidden) return null;
    return <Child {...props} />;
  };

  Component.propTypes = Child.propTypes;
  return Overridable.component(id, Component);
};
