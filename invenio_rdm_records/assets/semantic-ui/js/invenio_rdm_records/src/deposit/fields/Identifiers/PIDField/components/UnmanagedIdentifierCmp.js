// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React, { Component } from "react";
import { Form } from "semantic-ui-react";
import { getFieldErrors } from "./helpers";

/**
 * Render identifier field to allow user to input
 * the unmanaged PID.
 */
export class UnmanagedIdentifierCmp extends Component {
  constructor(props) {
    super(props);

    const { identifier } = props;

    this.state = {
      localIdentifier: identifier,
    };
  }

  componentDidUpdate(prevProps) {
    // called after the form field is updated and therefore re-rendered.
    const { identifier } = this.props;
    if (identifier !== prevProps.identifier) {
      this.handleIdentifierUpdate(identifier);
    }
  }

  handleIdentifierUpdate = (newIdentifier) => {
    this.setState({ localIdentifier: newIdentifier });
  };

  onChange = (value) => {
    const { onIdentifierChanged } = this.props;
    this.setState({ localIdentifier: value }, () => onIdentifierChanged(value));
  };

  render() {
    const { localIdentifier } = this.state;
    const { form, fieldPath, helpText, pidPlaceholder, disabled } = this.props;
    const fieldError = getFieldErrors(form, fieldPath);
    return (
      <>
        <Form.Field width={8} error={fieldError}>
          <Form.Input
            onChange={(e, { value }) => this.onChange(value)}
            value={localIdentifier}
            placeholder={pidPlaceholder}
            width={16}
            error={fieldError}
            disabled={disabled}
          />
        </Form.Field>
        {helpText && <label className="helptext">{helpText}</label>}
      </>
    );
  }
}

UnmanagedIdentifierCmp.propTypes = {
  form: PropTypes.object.isRequired,
  fieldPath: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  identifier: PropTypes.string.isRequired,
  onIdentifierChanged: PropTypes.func.isRequired,
  pidPlaceholder: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
};

UnmanagedIdentifierCmp.defaultProps = {
  helpText: null,
  disabled: false,
};
