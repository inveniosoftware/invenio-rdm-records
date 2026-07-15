/*
 * SPDX-FileCopyrightText: 2020-2026 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { Component } from "react";
import { Form } from "semantic-ui-react";
import { getFieldErrors } from "./helpers";

/**
 * Render identifier field to allow user to input
 * the unmanaged PID.
 */
export function UnmanagedIdentifierCmp({identifier, onIdentifierChanged, form, fieldPath, helpText = null, pidPlaceholder, disabled = false}) {
  const [localIdentifier, setLocalIdentifier] = React.useState(identifier);
  React.useEffect(() => {
    // called after the form field is updated and therefore re-rendered.
    
    if (identifier !== identifier) {
      handleIdentifierUpdate(identifier);
    }
  }, [identifier, onIdentifierChanged, form, fieldPath, helpText, pidPlaceholder, disabled]);

  const handleIdentifierUpdate = (newIdentifier) => {
    setLocalIdentifier(newIdentifier);
  };

  const onChange = (value) => {
    const { onIdentifierChanged } = this.props;
    this.setState({ localIdentifier: value }, () => onIdentifierChanged(value));
  };

  const fieldError = getFieldErrors(form, fieldPath);
    const displayError =
      fieldError && typeof fieldError === "object" && fieldError.message
        ? fieldError.message
        : fieldError;
    return (
      <>
        <Form.Field width={8} error={displayError}>
          <Form.Input
            onChange={(e, { value }) => onChange(value)}
            value={localIdentifier}
            placeholder={pidPlaceholder}
            width={16}
            error={displayError}
            disabled={disabled}
          />
        </Form.Field>
        {helpText && <label className="helptext">{helpText}</label>}
      </>
    );
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

