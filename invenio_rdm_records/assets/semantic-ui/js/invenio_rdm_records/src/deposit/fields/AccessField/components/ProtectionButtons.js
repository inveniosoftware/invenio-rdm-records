/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021-2024 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { Component } from "react";
import { Button, Popup, Icon } from "semantic-ui-react";
import { FastField } from "formik";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";

function ProtectionButtonsComponent({formik, disabled = false, fieldPath, active = true, canRestrictRecord = true}) {
  React.useEffect(() => {
    // If is disabled is set it means community is restricted and recort cannot be public
    // thus it has to be restricted
    if (disabled) {
      formik.form.setFieldValue(fieldPath, "restricted");
    }
  }, []);

  const handlePublicButtonClick = () => {
    const { formik, fieldPath } = this.props;
    formik.form.setFieldValue(fieldPath, "public");
    // NOTE: We reset values, so if embargo filled and click Public,
    //       user needs to fill embargo again. Otherwise, lots of
    //       bookkeeping.
    formik.form.setFieldValue("access.embargo", {
      active: false,
    });
  };

  const handleRestrictionButtonClick = () => {
    const { formik, fieldPath } = this.props;
    formik.form.setFieldValue(fieldPath, "restricted");
  };

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
            onClick={handlePublicButtonClick}
            active={active}
          >
            {i18next.t("Public")}
          </Button>

          <Button
            disabled={!canRestrictRecord}
            className={restrictedColor}
            data-testid="protection-buttons-component-restricted"
            active={!active}
            onClick={handleRestrictionButtonClick}
          >
            {i18next.t("Restricted")}
          </Button>
        </Button.Group>
      </>
    );
}

ProtectionButtonsComponent.propTypes = {
  canRestrictRecord: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
  formik: PropTypes.object.isRequired,
  active: PropTypes.bool,
  disabled: PropTypes.bool,
};

export function ProtectionButtons({fieldPath}) {
  return (
      <FastField
        name={fieldPath}
        component={(formikProps) => (
          <ProtectionButtonsComponent formik={formikProps} {...props} />
        )}
      />
    );
}

ProtectionButtons.defaultProps = {
  canRestrictRecord: true,
};

ProtectionButtons.propTypes = {
  canRestrictRecord: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
};
