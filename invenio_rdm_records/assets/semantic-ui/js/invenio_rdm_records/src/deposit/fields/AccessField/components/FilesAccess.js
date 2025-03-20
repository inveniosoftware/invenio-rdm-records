// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import PropTypes from "prop-types";
import React from "react";
import { ProtectionButtons } from "./ProtectionButtons";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { getIn } from "formik";
import { FeedbackLabel } from "react-invenio-forms";
import { Card } from "semantic-ui-react";

export const FilesAccess = ({
  access,
  accessCommunity,
  metadataOnly,
  values,
  initialValues,
  errors,
  initialErrors,
}) => {
  const publicFiles = access.files === "public";
  const publicMetadata = access.record === "public";
  const publicCommunity = accessCommunity === "public";

  const fullRecordRestricted = !publicCommunity || !publicMetadata;
  const filesRestricted = publicCommunity && !publicFiles && publicMetadata;

  const filesButtonsDisplayed = !metadataOnly && publicCommunity && publicMetadata;

  if (metadataOnly) {
    return (
      <Card.Meta data-testid="access-files">
        <em>{i18next.t("The record has no files.")}</em>
      </Card.Meta>
    );
  }

  const fieldPath = "access.files";
  const filesAccess = getIn(values, fieldPath, []);
  const formikInitialValues = getIn(initialValues, fieldPath, []);

  const error = getIn(errors, fieldPath, null);
  const initialError = getIn(initialErrors, fieldPath, null);
  const filesAccessError =
    error || (filesAccess === formikInitialValues && initialError);

  return (
    <div data-testid="access-files">
      {filesButtonsDisplayed && (
        <>
          {i18next.t("Files only")}
          {filesAccessError && <FeedbackLabel errorMessage={filesAccessError} />}
          <ProtectionButtons
            active={publicFiles}
            disable={!publicCommunity}
            fieldPath={fieldPath}
          />
        </>
      )}
      {fullRecordRestricted && (
        <Card.Description>
          <em>{i18next.t("The full record is restricted.")}</em>
        </Card.Description>
      )}
      {filesRestricted && (
        <Card.Description>
          <em>{i18next.t("The files of this record are restricted.")}</em>
        </Card.Description>
      )}
    </div>
  );
};

FilesAccess.propTypes = {
  access: PropTypes.object.isRequired,
  metadataOnly: PropTypes.bool,
  accessCommunity: PropTypes.string.isRequired,
  values: PropTypes.object,
  initialValues: PropTypes.object,
  errors: PropTypes.object,
  initialErrors: PropTypes.object,
  errors: PropTypes.object,
};

FilesAccess.defaultProps = {
  metadataOnly: false,
};
