// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { FieldLabel } from "react-invenio-forms";
import { Form, Segment } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export class ComingSoonField extends Component {
  render() {
    const { fieldPath, label, labelIcon } = this.props;
    return (
      <Form.Field id={fieldPath} name={fieldPath}>
        <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
        <Segment size="massive" tertiary textAlign="center">
          {i18next.t("Coming soon")}
        </Segment>
      </Form.Field>
    );
  }
}

ComingSoonField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
};

ComingSoonField.defaultProps = {
  label: undefined,
  labelIcon: undefined,
};
