/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { Field } from "formik";
import PropTypes from "prop-types";
import { Component } from "react";
import { Form } from "semantic-ui-react";

/**
 * Button component to reserve a PID.
 */

export function ReservePIDBtn({disabled = false, handleReservePID, label, loading = false, fieldError = null}) {
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

ReservePIDBtn.propTypes = {
  disabled: PropTypes.bool,
  handleReservePID: PropTypes.func.isRequired,
  fieldError: PropTypes.object,
  label: PropTypes.string.isRequired,
  loading: PropTypes.bool,
};

