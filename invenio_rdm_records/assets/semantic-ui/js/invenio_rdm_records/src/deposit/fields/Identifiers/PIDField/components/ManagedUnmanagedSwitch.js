/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";

import PropTypes from "prop-types";
import { Component } from "react";
import { Form, Radio } from "semantic-ui-react";

/**
 * Manage radio buttons choices between managed
 * and unmanaged PID.
 */
export function ManagedUnmanagedSwitch({onManagedUnmanagedChange, disabled = false, isManagedSelected, pidLabel = undefined}) {
  const handleChange = (e, { value }) => {
    const { onManagedUnmanagedChange } = this.props;
    const isManagedSelected = value === "managed";
    onManagedUnmanagedChange(isManagedSelected);
  };

  return (
      <Form.Group inline>
        <Form.Field>
          {i18next.t("Do you already have a {{pidLabel}} for this upload?", {
            pidLabel: pidLabel,
          })}
        </Form.Field>
        <Form.Field width={4}>
          <Radio
            label={i18next.t("Yes, I already have one")}
            aria-label={i18next.t("Yes, I already have one")}
            name="radioGroup"
            value="unmanaged"
            disabled={disabled}
            checked={!isManagedSelected}
            onChange={handleChange}
          />
        </Form.Field>
        <Form.Field width={3}>
          <Radio
            label={i18next.t("No, I need one")}
            aria-label={i18next.t("No, I need one")}
            name="radioGroup"
            value="managed"
            disabled={disabled}
            checked={isManagedSelected}
            onChange={handleChange}
          />
        </Form.Field>
      </Form.Group>
    );
}

ManagedUnmanagedSwitch.propTypes = {
  disabled: PropTypes.bool,
  isManagedSelected: PropTypes.bool.isRequired,
  onManagedUnmanagedChange: PropTypes.func.isRequired,
  pidLabel: PropTypes.string,
};

