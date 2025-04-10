// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _debounce from "lodash/debounce";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import { FieldLabel, FeedbackLabel } from "react-invenio-forms";
import { Form, Grid } from "semantic-ui-react";
import {
  ManagedIdentifierCmp,
  OptionalDOIoptions,
  UnmanagedIdentifierCmp,
} from "./components";
import { getFieldErrors } from "./components/helpers";
import { SET_DOI_NEEDED } from "../../../state/types";

const PROVIDER_EXTERNAL = "external";
const UPDATE_PID_DEBOUNCE_MS = 200;

/**
 * Render managed or unamanged PID fields and update
 * Formik form on input changed.
 * The field value has the following format:
 * { 'doi': { identifier: '<value>', provider: '<value>', client: '<value>' } }
 */
class OptionalPIDFieldCmp extends Component {
  constructor(props) {
    super(props);

    const { canBeManaged, canBeUnmanaged, record, field } = this.props;
    this.canBeManagedAndUnmanaged = canBeManaged && canBeUnmanaged;
    const value = field?.value;
    const isInternalProvider = value?.provider !== PROVIDER_EXTERNAL;
    const isDraft = record?.is_draft === true;
    const hasIdentifier = value?.identifier;
    const isManagedSelected =
      isDraft && hasIdentifier && isInternalProvider ? true : undefined;

    this.state = {
      isManagedSelected: isManagedSelected,
      isNoNeedSelected: undefined,
    };
  }

  onExternalIdentifierChanged = (identifier) => {
    const { form, fieldPath } = this.props;

    const pid = {
      identifier: identifier,
      provider: PROVIDER_EXTERNAL,
    };

    this.debounced && this.debounced.cancel();
    this.debounced = _debounce(() => {
      form.setFieldValue(fieldPath, pid);
    }, UPDATE_PID_DEBOUNCE_MS);
    this.debounced();
  };

  render() {
    const { isManagedSelected, isNoNeedSelected } = this.state;
    const {
      btnLabelDiscardPID,
      btnLabelGetPID,
      canBeManaged,
      canBeUnmanaged,
      form,
      fieldPath,
      fieldLabel,
      isEditingPublishedRecord,
      managedHelpText,
      pidLabel,
      pidIcon,
      pidPlaceholder,
      required,
      unmanagedHelpText,
      pidType,
      field,
      record,
      optionalDOItransitions,
      setNoINeedDOI,
    } = this.props;

    const { doiDefaultSelection } = this.props;
    const value = field.value || {};
    const currentIdentifier = value.identifier || "";
    const currentProvider = value.provider || "";

    let managedIdentifier = "",
      unmanagedIdentifier = "";
    if (currentIdentifier !== "") {
      const isProviderExternal = currentProvider === PROVIDER_EXTERNAL;
      managedIdentifier = !isProviderExternal ? currentIdentifier : "";
      unmanagedIdentifier = isProviderExternal ? currentIdentifier : "";
    }

    const hasManagedIdentifier = managedIdentifier !== "";
    const hasUnmanagedIdentifier = unmanagedIdentifier !== "";
    const doi = record?.pids?.doi?.identifier || "";
    const parentDoi = record.parent?.pids?.doi?.identifier || "";

    const hasDoi = doi !== "";
    const hasParentDoi = parentDoi !== "";
    const isDraft = record.is_draft;

    const _isUnmanagedSelected =
      isManagedSelected === undefined
        ? hasUnmanagedIdentifier ||
          (currentIdentifier === "" && doiDefaultSelection === "yes")
        : !isManagedSelected;

    const _isManagedSelected =
      isManagedSelected === undefined
        ? hasManagedIdentifier ||
          (currentIdentifier === "" && doiDefaultSelection === "no") // i.e pids: {}
        : isManagedSelected;

    const _isNoNeedSelected =
      isNoNeedSelected === undefined
        ? (!_isManagedSelected && !_isUnmanagedSelected) ||
          (isDraft !== true &&
            currentIdentifier === "" &&
            doiDefaultSelection === "not_needed")
        : isNoNeedSelected;

    const fieldError = getFieldErrors(form, fieldPath);

    return (
      <>
        <Form.Field
          required={required || hasParentDoi}
          error={fieldError ? true : false}
        >
          <Grid>
            <Grid.Column width={5}>
              <FieldLabel htmlFor={fieldPath} icon={pidIcon} label={fieldLabel} />
            </Grid.Column>
            {fieldError && (
              <Grid.Column width={11}>
                <FeedbackLabel errorMessage={fieldError} />
              </Grid.Column>
            )}
          </Grid>
        </Form.Field>

        {this.canBeManagedAndUnmanaged && (
          <OptionalDOIoptions
            optionalDOItransitions={optionalDOItransitions}
            isManagedSelected={_isManagedSelected}
            isNoNeedSelected={_isNoNeedSelected}
            onManagedUnmanagedChange={(userSelectedManaged, userSelectedNoNeed) => {
              if (userSelectedManaged) {
                form.setFieldValue("pids", {});
                if (!required) {
                  // We set the value as required so we can validate the action on submit
                  setNoINeedDOI(true);
                }
              } else if (userSelectedNoNeed) {
                form.setFieldValue("pids", {});
                setNoINeedDOI(false);
              } else {
                this.onExternalIdentifierChanged("");
                setNoINeedDOI(false);
              }
              form.setFieldError(fieldPath, false);
              this.setState({
                isManagedSelected: userSelectedManaged,
                isNoNeedSelected: userSelectedNoNeed,
              });
            }}
            pidLabel={pidLabel}
            required={required}
          />
        )}

        {canBeManaged && _isManagedSelected && (
          <ManagedIdentifierCmp
            disabled={hasDoi && isEditingPublishedRecord}
            btnLabelDiscardPID={btnLabelDiscardPID}
            btnLabelGetPID={btnLabelGetPID}
            form={form}
            fieldPath={fieldPath}
            identifier={managedIdentifier}
            helpText={managedHelpText}
            pidPlaceholder={pidPlaceholder}
            pidType={pidType}
            pidLabel={pidLabel}
          />
        )}

        {canBeUnmanaged && (!_isManagedSelected || _isNoNeedSelected) && (
          <UnmanagedIdentifierCmp
            identifier={unmanagedIdentifier}
            onIdentifierChanged={(identifier) => {
              this.onExternalIdentifierChanged(identifier);
            }}
            form={form}
            fieldPath={fieldPath}
            pidPlaceholder={pidPlaceholder}
            helpText={unmanagedHelpText}
            disabled={_isNoNeedSelected}
          />
        )}
      </>
    );
  }
}

OptionalPIDFieldCmp.propTypes = {
  field: PropTypes.object,
  form: PropTypes.object.isRequired,
  btnLabelDiscardPID: PropTypes.string.isRequired,
  btnLabelGetPID: PropTypes.string.isRequired,
  canBeManaged: PropTypes.bool.isRequired,
  canBeUnmanaged: PropTypes.bool.isRequired,
  fieldPath: PropTypes.string.isRequired,
  fieldLabel: PropTypes.string.isRequired,
  isEditingPublishedRecord: PropTypes.bool.isRequired,
  managedHelpText: PropTypes.string,
  pidIcon: PropTypes.string.isRequired,
  pidLabel: PropTypes.string.isRequired,
  pidPlaceholder: PropTypes.string.isRequired,
  pidType: PropTypes.string.isRequired,
  required: PropTypes.bool.isRequired,
  unmanagedHelpText: PropTypes.string,
  record: PropTypes.object.isRequired,
  doiDefaultSelection: PropTypes.object.isRequired,
  optionalDOItransitions: PropTypes.array.isRequired,
  setNoINeedDOI: PropTypes.func.isRequired,
};

OptionalPIDFieldCmp.defaultProps = {
  managedHelpText: null,
  unmanagedHelpText: null,
  field: undefined,
};

export const OptionalPIDField = connect(null, (dispatch) => {
  return {
    setNoINeedDOI: (value) =>
      dispatch({
        type: SET_DOI_NEEDED,
        payload: { noINeedDOI: value },
      }),
  };
})(OptionalPIDFieldCmp);
