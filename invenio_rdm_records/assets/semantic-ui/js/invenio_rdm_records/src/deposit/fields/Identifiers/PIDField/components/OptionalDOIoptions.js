/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";

import PropTypes from "prop-types";
import { Component } from "react";
import { connect } from "react-redux";
import { Form, Radio, Popup } from "semantic-ui-react";
import { DepositStatus } from "../../../../state/reducers/deposit";

const PROVIDER_EXTERNAL = "external";
/**
 * Manage radio buttons choices between managed (i.e. datacite), unmanaged (i.e. external) and no need for a PID.
 */
function OptionalDOIoptionsCmp({onManagedUnmanagedChange, isManagedSelected, isNoNeedSelected, pidLabel = undefined, optionalDOItransitions, record}) {
  const handleChange = (e, { value }) => {
    const { onManagedUnmanagedChange } = this.props;
    const isManagedSelected = value === "managed";
    const isNoNeedSelected = value === "notneeded";
    onManagedUnmanagedChange(isManagedSelected, isNoNeedSelected);
  };

  const _render = (cmp, shouldWrapPopup, message) => shouldWrapPopup && message ? <Popup content={message} trigger={cmp} /> : cmp;

  const doi = record?.pids?.doi?.identifier || "";
    const alreadyPublished = [
      DepositStatus.PUBLISHED,
      DepositStatus.NEW_VERSION_DRAFT,
    ].includes(record.status);

    const hasDoi = doi !== "";
    const hasInternalProvider =
      hasDoi && record?.pids?.doi?.provider !== PROVIDER_EXTERNAL;
    const hasManagedDOI = hasInternalProvider && isManagedSelected;

    

    const isUnManagedDisabled = isDisabled("external");
    const isNoNeedDisabled = isDisabled("not_needed");

    const managedProviderAllowed = optionalDOItransitions?.allowed_providers?.some(
      (val) => !["external", "not_needed"].includes(val)
    );
    // The locally managed DOI is disabled either if the external provider is allowed or if the no need option is allowed
    const isManagedDisabled = alreadyPublished
      ? !managedProviderAllowed
      : hasDoi && isManagedSelected;

    const yesIHaveOne = (
      <Form.Field width={4}>
        <Radio
          label={i18next.t("Yes, I already have one")}
          aria-label={i18next.t("Yes, I already have one")}
          name="radioGroup"
          value="unmanaged"
          disabled={isUnManagedDisabled}
          checked={!isManagedSelected && !isNoNeedSelected}
          onChange={handleChange}
        />
      </Form.Field>
    );

    const noINeedOne = (
      <Form.Field width={3}>
        <Radio
          label={i18next.t("No, I need one")}
          aria-label={i18next.t("No, I need one")}
          name="radioGroup"
          value="managed"
          disabled={isManagedDisabled}
          checked={isManagedSelected && !isNoNeedSelected}
          onChange={handleChange}
        />
      </Form.Field>
    );

    const noNeed = (
      <Form.Field width={4}>
        <Radio
          label={i18next.t("No, I don't need one")}
          aria-label={i18next.t("No, I don't need one")}
          name="radioGroup"
          value="notneeded"
          disabled={isNoNeedDisabled}
          checked={isNoNeedSelected}
          onChange={handleChange}
        />
      </Form.Field>
    );

    return (
      <Form.Group inline>
        <Form.Field>
          {i18next.t("Do you already have a {{pidLabel}} for this upload?", {
            pidLabel: pidLabel,
          })}
        </Form.Field>
        {_render(
          yesIHaveOne,
          isUnManagedDisabled,
          optionalDOItransitions?.message
        )}
        {_render(noINeedOne, isManagedDisabled, optionalDOItransitions?.message)}
        {_render(noNeed, isNoNeedDisabled, optionalDOItransitions?.message)}
      </Form.Group>
    );
}

OptionalDOIoptionsCmp.propTypes = {
  isManagedSelected: PropTypes.bool.isRequired,
  isNoNeedSelected: PropTypes.bool.isRequired,
  onManagedUnmanagedChange: PropTypes.func.isRequired,
  pidLabel: PropTypes.string,
  optionalDOItransitions: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
};

const mapStateToProps = (state) => ({
  record: state.deposit.record,
});

export const OptionalDOIoptions = connect(mapStateToProps, null)(OptionalDOIoptionsCmp);
