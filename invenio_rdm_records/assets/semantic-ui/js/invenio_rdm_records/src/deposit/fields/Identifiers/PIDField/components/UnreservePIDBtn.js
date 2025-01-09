// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Field } from "formik";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Form, Popup } from "semantic-ui-react";

/**
 * Button component to unreserve a PID.
 */
export class UnreservePIDBtn extends Component {
  render() {
    const { disabled, handleDiscardPID, label, loading } = this.props;
    return (
      <Popup
        content={label}
        trigger={
          <Field>
            {({ form: formik }) => (
              <Form.Button
                disabled={disabled || loading}
                loading={loading}
                icon="close"
                onClick={(e) => handleDiscardPID(e, formik)}
                size="mini"
              />
            )}
          </Field>
        }
      />
    );
  }
}

UnreservePIDBtn.propTypes = {
  disabled: PropTypes.bool,
  handleDiscardPID: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
  loading: PropTypes.bool,
};

UnreservePIDBtn.defaultProps = {
  disabled: false,
  loading: false,
};
