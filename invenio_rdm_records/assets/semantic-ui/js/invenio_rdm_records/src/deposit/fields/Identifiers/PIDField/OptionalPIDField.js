/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-License-Identifier: MIT
 */

import _debounce from "lodash/debounce";
import _isEmpty from "lodash/isEmpty";
import PropTypes from "prop-types";
import { Component } from "react";
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
const optionalPIDFieldCmpDefaultPropPublishedDOI = {};
function OptionalPIDFieldCmp({canBeManaged, canBeUnmanaged, record, field = undefined, required, setNoINeedDOI, form, fieldPath, doiDefaultSelection, btnLabelDiscardPID, btnLabelGetPID, fieldLabel, managedHelpText = null, pidLabel, pidIcon, pidPlaceholder, unmanagedHelpText = null, pidType, optionalDOItransitions, publishedDOI = optionalPIDFieldCmpDefaultPropPublishedDOI}) {
  const [isManagedSelected, setIsManagedSelected] = React.useState(isManagedSelected);
  const [isNoNeedSelected, setIsNoNeedSelected] = React.useState(undefined);
  React.useEffect(() => {
    // When the component is mounted we need to call the callback to sync the state
    
    const { _isManagedSelected } = computeManagedUnmanaged();
    if (_isManagedSelected) {
      if (!required) {
        // We set the value as required so we can validate the action on submit
        setNoINeedDOI(true);
      }
    } else {
      setNoINeedDOI(false);
    }
  }, []);

  const onExternalIdentifierChanged = (identifier) => {
    const { form, fieldPath } = this.props;

    const pid = {
      identifier: identifier,
      provider: PROVIDER_EXTERNAL,
    };

    debounced && debounced.cancel();
    debounced = _debounce(() => {
      form.setFieldValue(fieldPath, pid);
    }, UPDATE_PID_DEBOUNCE_MS);
    debounced();
  };

  const computeManagedUnmanaged = () => {
    const { isManagedSelected, isNoNeedSelected } = this.state;
    const { field, record, doiDefaultSelection } = this.props;

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

    return {
      managedIdentifier,
      unmanagedIdentifier,
      hasDoi,
      hasParentDoi,
      _isManagedSelected,
      _isUnmanagedSelected,
      _isNoNeedSelected,
    };
  };

  const handleManagedUnmanagedChange = (userSelectedManaged, userSelectedNoNeed) => {
    const { form, fieldPath, required, setNoINeedDOI } = this.props;
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
      onExternalIdentifierChanged("");
      setNoINeedDOI(false);
    }
    form.setFieldError(fieldPath, false);
    this.setState({
      isManagedSelected: userSelectedManaged,
      isNoNeedSelected: userSelectedNoNeed,
    });
  };

  const {
      managedIdentifier,
      unmanagedIdentifier,
      hasParentDoi,
      _isManagedSelected,
      _isNoNeedSelected,
    } = computeManagedUnmanaged();

    const fieldError = getFieldErrors(form, fieldPath);
    const hasPublishedManagedDOI =
      publishedDOI?.identifier && publishedDOI?.provider !== PROVIDER_EXTERNAL;
    const isManagedProviderAllowed = _isEmpty(optionalDOItransitions)
      ? true // if no transitions are provided (i.e. new draft) we assume that the managed provider is allowed
      : // if any of the allowed providers is not external or not_needed we
        // can assume that the managed provider is allowed
        optionalDOItransitions?.allowed_providers?.some(
          (val) => !["external", "not_needed"].includes(val)
        );

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
                <FeedbackLabel fieldPath={fieldPath} />
              </Grid.Column>
            )}
          </Grid>
        </Form.Field>

        {canBeManagedAndUnmanaged && (
          <OptionalDOIoptions
            optionalDOItransitions={optionalDOItransitions}
            isManagedSelected={_isManagedSelected}
            isNoNeedSelected={_isNoNeedSelected}
            onManagedUnmanagedChange={handleManagedUnmanagedChange}
            pidLabel={pidLabel}
            required={required}
          />
        )}

        {canBeManaged && _isManagedSelected && (
          <ManagedIdentifierCmp
            // You cannot change the managed DOI option
            // or unreserve the DOI if you have already published with a local DOI
            // or if the managed provider is not allowed
            disabled={hasPublishedManagedDOI || !isManagedProviderAllowed}
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
              onExternalIdentifierChanged(identifier);
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

OptionalPIDFieldCmp.propTypes = {
  field: PropTypes.object,
  form: PropTypes.object.isRequired,
  btnLabelDiscardPID: PropTypes.string.isRequired,
  btnLabelGetPID: PropTypes.string.isRequired,
  canBeManaged: PropTypes.bool.isRequired,
  canBeUnmanaged: PropTypes.bool.isRequired,
  fieldPath: PropTypes.string.isRequired,
  fieldLabel: PropTypes.string.isRequired,
  managedHelpText: PropTypes.string,
  pidIcon: PropTypes.string.isRequired,
  pidLabel: PropTypes.string.isRequired,
  pidPlaceholder: PropTypes.string.isRequired,
  pidType: PropTypes.string.isRequired,
  required: PropTypes.bool.isRequired,
  unmanagedHelpText: PropTypes.string,
  record: PropTypes.object.isRequired,
  doiDefaultSelection: PropTypes.object.isRequired,
  optionalDOItransitions: PropTypes.object.isRequired,
  /* from Redux */
  publishedDOI: PropTypes.object,
  setNoINeedDOI: PropTypes.func.isRequired,
};

const mapStateToProps = (state) => ({
  publishedDOI: state.deposit.config?.published_record?.pids?.doi,
});

export const OptionalPIDField = connect(mapStateToProps, (dispatch) => {
  return {
    setNoINeedDOI: (value) =>
      dispatch({
        type: SET_DOI_NEEDED,
        payload: { noINeedDOI: value },
      }),
  };
})(OptionalPIDFieldCmp);
