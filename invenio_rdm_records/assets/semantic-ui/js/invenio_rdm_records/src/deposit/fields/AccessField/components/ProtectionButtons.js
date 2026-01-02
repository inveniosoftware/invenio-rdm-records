// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021-2024 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import { Button, Popup, Icon } from "semantic-ui-react";
import { FastField } from "formik";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";

class ProtectionButtonsComponent extends Component {
  componentDidMount() {
    const { formik, disabled, fieldPath } = this.props;
    // If is disabled is set it means community is restricted and recort cannot be public
    // thus it has to be restricted
    if (disabled) {
      formik.form.setFieldValue(fieldPath, "restricted");
    }
  }

  handlePublicButtonClick = () => {
    const { formik, fieldPath } = this.props;
    formik.form.setFieldValue(fieldPath, "public");
    // NOTE: We reset values, so if embargo filled and click Public,
    //       user needs to fill embargo again. Otherwise, lots of
    //       bookkeeping.
    formik.form.setFieldValue("access.embargo", {
      active: false,
    });
  };

  handleRestrictionButtonClick = () => {
    const { formik, fieldPath } = this.props;
    formik.form.setFieldValue(fieldPath, "restricted");
  };

  render() {
    const { active, disabled, canRestrictRecord } = this.props;

    const publicColor = active ? "positive" : "";
    const restrictedColor = !active ? "negative" : "";

    return (
      <>
        {!canRestrictRecord && (
          <Popup
            trigger={<Icon className="right-floated" name="question circle outline" />}
            content={i18next.t(
              "Record visibility can not be changed to restricted anymore. Please contact support if you still need to make these changes."
            )}
          />
        )}
        <Button.Group widths="2">
          <Button
            className={publicColor}
            data-testid="protection-buttons-component-public"
            disabled={disabled}
            onClick={this.handlePublicButtonClick}
            active={active}
          >
            {i18next.t("Public")}
          </Button>

          <Button
            disabled={!canRestrictRecord}
            className={restrictedColor}
            data-testid="protection-buttons-component-restricted"
            active={!active}
            onClick={this.handleRestrictionButtonClick}
          >
            {i18next.t("Restricted")}
          </Button>
        </Button.Group>
      </>
    );
  }
}

ProtectionButtonsComponent.propTypes = {
  canRestrictRecord: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
  formik: PropTypes.object.isRequired,
  active: PropTypes.bool,
  disabled: PropTypes.bool,
};

ProtectionButtonsComponent.defaultProps = {
  active: true,
  disabled: false,
  canRestrictRecord: true,
};

export class ProtectionButtons extends Component {
  render() {
    const { fieldPath } = this.props;

    return (
      <FastField
        name={fieldPath}
        component={(formikProps) => (
          <ProtectionButtonsComponent formik={formikProps} {...this.props} />
        )}
      />
    );
  }
}

ProtectionButtons.defaultProps = {
  canRestrictRecord: true,
};

ProtectionButtons.propTypes = {
  canRestrictRecord: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
};
