// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { Field } from "formik";
import { FieldLabel } from "react-invenio-forms";
import { Card, Divider, Form, Header } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import {
  MetadataAccess,
  FilesAccess,
  EmbargoAccess,
  AccessMessage,
} from "./components";

export class AccessRightFieldCmp extends Component {
  /** Top-level Access Right Component */

  render() {
    const {
      fieldPath,
      formik, // this is our access to the shared current draft
      label,
      labelIcon,
      showMetadataAccess,
      community,
      record,
      recordRestrictionGracePeriod,
      allowRecordRestriction,
    } = this.props;

    const isGhostCommunity = community?.is_ghost === true;
    const communityAccess =
      (community && !isGhostCommunity && community.access.visibility) || "public";
    const isMetadataOnly = !formik.form.values.files.enabled;

    return (
      <Card className="access-right">
        <Form.Field required>
          <Card.Content>
            <Card.Header>
              <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            </Card.Header>
          </Card.Content>
          <Card.Content>
            {showMetadataAccess && (
              <>
                <MetadataAccess
                  recordAccess={formik.field.value.record}
                  communityAccess={communityAccess}
                  record={record}
                  recordRestrictionGracePeriod={recordRestrictionGracePeriod}
                  allowRecordRestriction={allowRecordRestriction}
                />
                <Divider hidden />
              </>
            )}
            <FilesAccess
              access={formik.field.value}
              accessCommunity={communityAccess}
              metadataOnly={isMetadataOnly}
            />

            <Divider hidden />

            <AccessMessage
              access={formik.field.value}
              accessCommunity={communityAccess}
              metadataOnly={isMetadataOnly}
            />

            <Divider hidden />
          </Card.Content>
          <Card.Content>
            <Card.Header as={Header} size="tiny">
              {i18next.t("Options")}
            </Card.Header>
          </Card.Content>
          <Card.Content extra>
            <EmbargoAccess
              access={formik.field.value}
              accessCommunity={communityAccess}
              metadataOnly={isMetadataOnly}
            />
          </Card.Content>
        </Form.Field>
      </Card>
    );
  }
}

AccessRightFieldCmp.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  formik: PropTypes.object.isRequired,
  label: PropTypes.string.isRequired,
  labelIcon: PropTypes.string.isRequired,
  showMetadataAccess: PropTypes.bool,
  community: PropTypes.object,
  record: PropTypes.object.isRequired,
  recordRestrictionGracePeriod: PropTypes.number.isRequired,
  allowRecordRestriction: PropTypes.bool.isRequired,
};

AccessRightFieldCmp.defaultProps = {
  showMetadataAccess: true,
  community: undefined,
};

const mapStateToPropsAccessRightFieldCmp = (state) => ({
  community: state.deposit.editorState.selectedCommunity,
});

export const AccessRightFieldComponent = connect(
  mapStateToPropsAccessRightFieldCmp,
  null
)(AccessRightFieldCmp);

export class AccessRightField extends Component {
  render() {
    const { fieldPath } = this.props;

    return (
      <Field name={fieldPath}>
        {(formik) => <AccessRightFieldComponent formik={formik} {...this.props} />}
      </Field>
    );
  }
}

AccessRightField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  labelIcon: PropTypes.string,
  isMetadataOnly: PropTypes.bool,
  record: PropTypes.object.isRequired,
  recordRestrictionGracePeriod: PropTypes.number.isRequired,
  allowRecordRestriction: PropTypes.bool.isRequired,
};

AccessRightField.defaultProps = {
  labelIcon: undefined,
  isMetadataOnly: undefined,
};
