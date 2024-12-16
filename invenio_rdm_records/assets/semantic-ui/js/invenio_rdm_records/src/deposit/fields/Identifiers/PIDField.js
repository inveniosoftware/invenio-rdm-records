// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { FastField, Field, getIn } from "formik";
import _debounce from "lodash/debounce";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { FieldLabel } from "react-invenio-forms";
import { connect } from "react-redux";
import { Form, Popup, Radio } from "semantic-ui-react";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "../../api/DepositFormSubmitContext";
import { DISCARD_PID_STARTED, RESERVE_PID_STARTED } from "../../state/types";

const PROVIDER_EXTERNAL = "external";
const UPDATE_PID_DEBOUNCE_MS = 200;

const getFieldErrors = (form, fieldPath) => {
  return (
    getIn(form.errors, fieldPath, null) || getIn(form.initialErrors, fieldPath, null)
  );
};

/**
 * Button component to reserve a PID.
 */
class ReservePIDBtn extends Component {
  render() {
    const { disabled, handleReservePID, label, loading, fieldError } = this.props;
    return (
      <Field>
        {({ form: formik }) => (
          <Form.Button
            className="positive"
            size="mini"
            loading={loading}
            disabled={disabled || loading}
            onClick={(e) => handleReservePID(e, formik)}
            content={label}
            error={fieldError}
          />
        )}
      </Field>
    );
  }
}

ReservePIDBtn.propTypes = {
  disabled: PropTypes.bool,
  handleReservePID: PropTypes.func.isRequired,
  fieldError: PropTypes.object,
  label: PropTypes.string.isRequired,
  loading: PropTypes.bool,
};

ReservePIDBtn.defaultProps = {
  disabled: false,
  loading: false,
  fieldError: null,
};

/**
 * Button component to unreserve a PID.
 */
class UnreservePIDBtn extends Component {
  render() {
    const { disabled, handleDiscardPID, label, loading } = this.props;
    return (
      <Popup
        content={label}
        trigger={
          <Field>
            {({ form: formik }) => (
              <Form.Button
                disabled={disabled || loading}
                loading={loading}
                icon="close"
                onClick={(e) => handleDiscardPID(e, formik)}
                size="mini"
              />
            )}
          </Field>
        }
      />
    );
  }
}

UnreservePIDBtn.propTypes = {
  disabled: PropTypes.bool,
  handleDiscardPID: PropTypes.func.isRequired,
  label: PropTypes.string.isRequired,
  loading: PropTypes.bool,
};

UnreservePIDBtn.defaultProps = {
  disabled: false,
  loading: false,
};

/**
 * Manage radio buttons choices between managed
 * and unmanaged PID.
 */
class ManagedUnmanagedSwitch extends Component {
  handleChange = (e, { value }) => {
    const { onManagedUnmanagedChange } = this.props;
    const isManagedSelected = value === "managed";
    const isNoNeedSelected = value === "notneeded";
    onManagedUnmanagedChange(isManagedSelected, isNoNeedSelected);
  };

  render() {
    const { disabled, isManagedSelected, isNoNeedSelected, pidLabel, required } =
      this.props;

    return (
      <Form.Group inline>
        <Form.Field>
          {i18next.t("Do you already have a {{pidLabel}} for this upload?", {
            pidLabel: pidLabel,
          })}
        </Form.Field>
        <Form.Field width={4}>
          <Radio
            label={i18next.t("Yes, I already have one")}
            aria-label={i18next.t("Yes, I already have one")}
            name="radioGroup"
            value="unmanaged"
            disabled={disabled}
            checked={!isManagedSelected && !isNoNeedSelected}
            onChange={this.handleChange}
          />
        </Form.Field>
        <Form.Field width={3}>
          <Radio
            label={i18next.t("No, I need one")}
            aria-label={i18next.t("No, I need one")}
            name="radioGroup"
            value="managed"
            disabled={disabled}
            checked={isManagedSelected && !isNoNeedSelected}
            onChange={this.handleChange}
          />
        </Form.Field>
        {!required && (
          <Form.Field width={4}>
            <Radio
              label={i18next.t("No, I don't need one")}
              aria-label={i18next.t("No, I don't need one")}
              name="radioGroup"
              value="notneeded"
              disabled={disabled}
              checked={isNoNeedSelected}
              onChange={this.handleChange}
            />
          </Form.Field>
        )}
      </Form.Group>
    );
  }
}

ManagedUnmanagedSwitch.propTypes = {
  disabled: PropTypes.bool,
  isManagedSelected: PropTypes.bool.isRequired,
  isNoNeedSelected: PropTypes.bool.isRequired,
  onManagedUnmanagedChange: PropTypes.func.isRequired,
  pidLabel: PropTypes.string,
  required: PropTypes.bool.isRequired,
};

ManagedUnmanagedSwitch.defaultProps = {
  disabled: false,
  pidLabel: undefined,
};

/**
 * Render identifier field and reserve/unreserve
 * button components for managed PID.
 */
class ManagedIdentifierComponent extends Component {
  static contextType = DepositFormSubmitContext;

  handleReservePID = (event, formik) => {
    const { pidType } = this.props;
    const { setSubmitContext } = this.context;
    setSubmitContext(DepositFormSubmitActions.RESERVE_PID, {
      pidType: pidType,
    });
    formik.handleSubmit(event);
  };

  handleDiscardPID = (event, formik) => {
    const { pidType } = this.props;
    const { setSubmitContext } = this.context;
    setSubmitContext(DepositFormSubmitActions.DISCARD_PID, {
      pidType: pidType,
    });
    formik.handleSubmit(event);
  };

  render() {
    const {
      actionState,
      actionStateExtra,
      btnLabelDiscardPID,
      btnLabelGetPID,
      disabled,
      helpText,
      identifier,
      pidPlaceholder,
      pidType,
      form,
      fieldPath,
    } = this.props;
    const hasIdentifier = identifier !== "";

    const ReserveBtn = (
      <ReservePIDBtn
        disabled={disabled || hasIdentifier}
        label={btnLabelGetPID}
        loading={
          actionState === RESERVE_PID_STARTED && actionStateExtra.pidType === pidType
        }
        handleReservePID={this.handleReservePID}
        fieldError={getFieldErrors(form, fieldPath)}
      />
    );

    const UnreserveBtn = (
      <UnreservePIDBtn
        disabled={disabled}
        label={btnLabelDiscardPID}
        handleDiscardPID={this.handleDiscardPID}
        loading={
          actionState === DISCARD_PID_STARTED && actionStateExtra.pidType === pidType
        }
        pidType={pidType}
      />
    );

    return (
      <>
        <Form.Group inline>
          {hasIdentifier ? (
            <Form.Field>
              <label>{identifier}</label>
            </Form.Field>
          ) : (
            <Form.Field width={4}>
              <Form.Input disabled value="" placeholder={pidPlaceholder} width={16} />
            </Form.Field>
          )}

          <Form.Field>{identifier ? UnreserveBtn : ReserveBtn}</Form.Field>
        </Form.Group>
        {helpText && <label className="helptext">{helpText}</label>}
      </>
    );
  }
}

ManagedIdentifierComponent.propTypes = {
  btnLabelGetPID: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  helpText: PropTypes.string,
  identifier: PropTypes.string.isRequired,
  btnLabelDiscardPID: PropTypes.string.isRequired,
  pidPlaceholder: PropTypes.string.isRequired,
  pidType: PropTypes.string.isRequired,
  form: PropTypes.object.isRequired,
  fieldPath: PropTypes.string.isRequired,
  /* from Redux */
  actionState: PropTypes.string,
  actionStateExtra: PropTypes.object,
};

ManagedIdentifierComponent.defaultProps = {
  disabled: false,
  helpText: null,
  /* from Redux */
  actionState: "",
  actionStateExtra: {},
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  actionStateExtra: state.deposit.actionStateExtra,
});

const ManagedIdentifierCmp = connect(mapStateToProps, null)(ManagedIdentifierComponent);

/**
 * Render identifier field to allow user to input
 * the unmanaged PID.
 */
class UnmanagedIdentifierCmp extends Component {
  constructor(props) {
    super(props);

    const { identifier } = props;

    this.state = {
      localIdentifier: identifier,
    };
  }

  componentDidUpdate(prevProps) {
    // called after the form field is updated and therefore re-rendered.
    const { identifier } = this.props;
    if (identifier !== prevProps.identifier) {
      this.handleIdentifierUpdate(identifier);
    }
  }

  handleIdentifierUpdate = (newIdentifier) => {
    this.setState({ localIdentifier: newIdentifier });
  };

  onChange = (value) => {
    const { onIdentifierChanged } = this.props;
    this.setState({ localIdentifier: value }, () => onIdentifierChanged(value));
  };

  render() {
    const { localIdentifier } = this.state;
    const { form, fieldPath, helpText, pidPlaceholder, disabled } = this.props;
    const fieldError = getFieldErrors(form, fieldPath);
    return (
      <>
        <Form.Field width={8} error={fieldError}>
          <Form.Input
            onChange={(e, { value }) => this.onChange(value)}
            value={localIdentifier}
            placeholder={pidPlaceholder}
            width={16}
            error={fieldError}
            disabled={disabled}
          />
        </Form.Field>
        {helpText && <label className="helptext">{helpText}</label>}
      </>
    );
  }
}

UnmanagedIdentifierCmp.propTypes = {
  form: PropTypes.object.isRequired,
  fieldPath: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  identifier: PropTypes.string.isRequired,
  onIdentifierChanged: PropTypes.func.isRequired,
  pidPlaceholder: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
};

UnmanagedIdentifierCmp.defaultProps = {
  helpText: null,
  disabled: false,
};

/**
 * Render managed or unamanged PID fields and update
 * Formik form on input changed.
 * The field value has the following format:
 * { 'doi': { identifier: '<value>', provider: '<value>', client: '<value>' } }
 */
class CustomPIDField extends Component {
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
    } = this.props;

    let { doiDefaultSelection } = this.props;

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
    const isDoiCreated = currentIdentifier !== "";
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
          <FieldLabel htmlFor={fieldPath} icon={pidIcon} label={fieldLabel} />
        </Form.Field>

        {this.canBeManagedAndUnmanaged && (
          <ManagedUnmanagedSwitch
            disabled={
              (isEditingPublishedRecord || hasManagedIdentifier) &&
              (hasDoi || isDoiCreated || _isNoNeedSelected)
            }
            isManagedSelected={_isManagedSelected}
            isNoNeedSelected={_isNoNeedSelected}
            onManagedUnmanagedChange={(userSelectedManaged, userSelectedNoNeed) => {
              if (userSelectedManaged) {
                form.setFieldValue("pids", {});
                if (!required) {
                  // We set the
                  form.setFieldValue("noINeedDOI", true);
                }
              } else if (userSelectedNoNeed) {
                form.setFieldValue("pids", {});
                form.setFieldValue("noINeedDOI", false);
              } else {
                this.onExternalIdentifierChanged("");
                form.setFieldValue("noINeedDOI", false);
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
            disabled={_isNoNeedSelected || isEditingPublishedRecord}
          />
        )}
      </>
    );
  }
}

CustomPIDField.propTypes = {
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
};

CustomPIDField.defaultProps = {
  managedHelpText: null,
  unmanagedHelpText: null,
  field: undefined,
};

/**
 * Render the PIDField using a custom Formik component
 */
export class PIDField extends Component {
  constructor(props) {
    super(props);

    this.validatePropValues();
  }

  validatePropValues = () => {
    const { canBeManaged, canBeUnmanaged, fieldPath } = this.props;

    if (!canBeManaged && !canBeUnmanaged) {
      throw Error(`${fieldPath} must be managed, unmanaged or both.`);
    }
  };

  render() {
    const { fieldPath } = this.props;

    return <FastField name={fieldPath} component={CustomPIDField} {...this.props} />;
  }
}

PIDField.propTypes = {
  btnLabelDiscardPID: PropTypes.string,
  btnLabelGetPID: PropTypes.string,
  canBeManaged: PropTypes.bool,
  canBeUnmanaged: PropTypes.bool,
  fieldPath: PropTypes.string.isRequired,
  fieldLabel: PropTypes.string.isRequired,
  isEditingPublishedRecord: PropTypes.bool.isRequired,
  managedHelpText: PropTypes.string,
  pidIcon: PropTypes.string,
  pidLabel: PropTypes.string.isRequired,
  pidPlaceholder: PropTypes.string,
  pidType: PropTypes.string.isRequired,
  required: PropTypes.bool,
  unmanagedHelpText: PropTypes.string,
  record: PropTypes.object.isRequired,
  doiDefaultSelection: PropTypes.object.isRequired,
};

PIDField.defaultProps = {
  btnLabelDiscardPID: "Discard",
  btnLabelGetPID: "Reserve",
  canBeManaged: true,
  canBeUnmanaged: true,
  managedHelpText: null,
  pidIcon: "barcode",
  pidPlaceholder: "",
  required: false,
  unmanagedHelpText: null,
};
