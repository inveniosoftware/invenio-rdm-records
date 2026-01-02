// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { Field } from "formik";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Form } from "semantic-ui-react";

/**
 * Button component to reserve a PID.
 */

export class ReservePIDBtn extends Component {
  render() {
    const { disabled, handleReservePID, label, loading, fieldError } = this.props;
    return (
      <Field>
        {({ form: formik }) => (
          <Form.Button
            className="positive"
            size="mini"
            loading={loading}
            disabled={disabled || loading}
            onClick={(e) => handleReservePID(e, formik)}
            content={label}
            error={fieldError}
          />
        )}
      </Field>
    );
  }
}

ReservePIDBtn.propTypes = {
  disabled: PropTypes.bool,
  handleReservePID: PropTypes.func.isRequired,
  fieldError: PropTypes.object,
  label: PropTypes.string.isRequired,
  loading: PropTypes.bool,
};

ReservePIDBtn.defaultProps = {
  disabled: false,
  loading: false,
  fieldError: null,
};
