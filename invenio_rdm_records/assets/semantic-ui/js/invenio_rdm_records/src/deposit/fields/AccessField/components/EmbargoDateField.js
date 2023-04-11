// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React from "react";
import { FieldLabel, TextField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export function EmbargoDateField({
  fieldPath,
  label,
  labelIcon,
  placeholder,
  required,
  helpText,
}) {
  return (
    <TextField
      fieldPath={fieldPath}
      label={<FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />}
      placeholder={placeholder}
      required={required}
      helpText={helpText}
    />
  );
}

EmbargoDateField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
  helpText: PropTypes.string,
};

EmbargoDateField.defaultProps = {
  required: false,
  labelIcon: "calendar",
  placeholder: i18next.t("YYYY-MM-DD"),
  label: i18next.t("Embargo until"),
  helpText: `${i18next.t("Format")}: ${i18next.t("YYYY-MM-DD")}`,
};
