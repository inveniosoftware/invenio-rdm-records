/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2024 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import { Component } from "react";
import PropTypes from "prop-types";
import { FieldLabel } from "react-invenio-forms";
import { Form, Segment } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export function ComingSoonField({fieldPath, label = undefined, labelIcon = undefined}) {
  return (
      <Form.Field id={fieldPath} name={fieldPath}>
        <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
        <Segment size="massive" tertiary textAlign="center">
          {i18next.t("Coming soon")}
        </Segment>
      </Form.Field>
    );
}

ComingSoonField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
};

