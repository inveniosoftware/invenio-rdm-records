/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

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
