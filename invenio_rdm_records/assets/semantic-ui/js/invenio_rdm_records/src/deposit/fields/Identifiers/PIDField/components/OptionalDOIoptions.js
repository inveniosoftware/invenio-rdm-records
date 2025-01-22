// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";

import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Form, Radio, Popup } from "semantic-ui-react";
import { DepositStatus } from "../../../../state/reducers/deposit";

/**
 * Manage radio buttons choices between managed (i.e. datacite), unmanaged (i.e. external) and no need for a PID.
 */
class OptionalDOIoptionsCmp extends Component {
  handleChange = (e, { value }) => {
    const { onManagedUnmanagedChange } = this.props;
    const isManagedSelected = value === "managed";
    const isNoNeedSelected = value === "notneeded";
    onManagedUnmanagedChange(isManagedSelected, isNoNeedSelected);
  };

  _render = (cmp, shouldWrapPopup, message) =>
    shouldWrapPopup && message ? <Popup content={message} trigger={cmp} /> : cmp;

  render() {
    const {
      isManagedSelected,
      isNoNeedSelected,
      pidLabel,
      optionalDOItransitions,
      record,
    } = this.props;

    const doi = record?.pids?.doi?.identifier || "";
    const alreadyPublished = [
      DepositStatus.PUBLISHED,
      DepositStatus.NEW_VERSION_DRAFT,
    ].includes(record.status);

    const hasDoi = doi !== "";
    const isUnManagedDisabled = alreadyPublished
      ? !optionalDOItransitions.allowed_providers.includes("external")
      : hasDoi && isManagedSelected;

    const isNoNeedDisabled = alreadyPublished
      ? !optionalDOItransitions.allowed_providers.includes("not_needed")
      : hasDoi && isManagedSelected;

    const isManagedTransition = optionalDOItransitions?.allowed_providers?.some(
      (val) => !["external", "not_needed"].includes(val)
    );
    // The locally managed DOI is disabled either if the external provider is allowed or if the no need option is allowed
    const isManagedDisabled = alreadyPublished
      ? !isManagedTransition
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
          onChange={this.handleChange}
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
          onChange={this.handleChange}
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
          onChange={this.handleChange}
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
        {this._render(
          yesIHaveOne,
          isUnManagedDisabled,
          optionalDOItransitions?.message
        )}
        {this._render(noINeedOne, isManagedDisabled, optionalDOItransitions?.message)}
        {this._render(noNeed, isNoNeedDisabled, optionalDOItransitions?.message)}
      </Form.Group>
    );
  }
}

OptionalDOIoptionsCmp.propTypes = {
  isManagedSelected: PropTypes.bool.isRequired,
  isNoNeedSelected: PropTypes.bool.isRequired,
  onManagedUnmanagedChange: PropTypes.func.isRequired,
  pidLabel: PropTypes.string,
  optionalDOItransitions: PropTypes.array.isRequired,
  record: PropTypes.object.isRequired,
};

OptionalDOIoptionsCmp.defaultProps = {
  pidLabel: undefined,
};

const mapStateToProps = (state) => ({
  record: state.deposit.record,
});

export const OptionalDOIoptions = connect(mapStateToProps, null)(OptionalDOIoptionsCmp);
