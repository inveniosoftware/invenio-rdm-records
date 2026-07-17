/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import _debounce from "lodash/debounce";
import PropTypes from "prop-types";
import { useRef } from "react";
import { FieldLabel } from "react-invenio-forms";
import { Form } from "semantic-ui-react";
import {
  ManagedIdentifierCmp,
  ManagedUnmanagedSwitch,
  UnmanagedIdentifierCmp,
} from "./components";
import { getFieldErrors } from "./components/helpers";

const PROVIDER_EXTERNAL = "external";
const UPDATE_PID_DEBOUNCE_MS = 200;

/**
 * Render managed or unamanged PID fields and update
 * Formik form on input changed.
 * The field value has the following format:
 * { 'doi': { identifier: '<value>', provider: '<value>', client: '<value>' } }
 */
export function RequiredPIDField({
  canBeManaged,
  canBeUnmanaged,
  record,
  field = undefined,
  form,
  fieldPath,
  btnLabelDiscardPID,
  btnLabelGetPID,
  fieldLabel,
  isEditingPublishedRecord,
  managedHelpText = null,
  pidLabel,
  pidIcon,
  pidPlaceholder,
  required,
  unmanagedHelpText = null,
  pidType,
  doiDefaultSelection,
}) {
  const [isManagedSelected, setIsManagedSelected] = React.useState(() => {
    const fieldValue = field?.value;
    const isInternalProvider = fieldValue?.provider !== PROVIDER_EXTERNAL;
    const isDraft = record?.is_draft === true;
    const hasIdentifier = fieldValue?.identifier;
    return isDraft && hasIdentifier && isInternalProvider ? true : undefined;
  });
  const debouncedRef = useRef(null);

  const onExternalIdentifierChanged = (identifier) => {
    const pid = {
      identifier: identifier,
      provider: PROVIDER_EXTERNAL,
    };

    debouncedRef.current && debouncedRef.current.cancel();
    debouncedRef.current = _debounce(() => {
      form.setFieldValue(fieldPath, pid);
    }, UPDATE_PID_DEBOUNCE_MS);
    debouncedRef.current();
  };

  const value = field?.value || {};
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
  const doi = record?.pids?.doi?.identifier || "";
  const parentDoi = record?.parent?.pids?.doi?.identifier || "";

  const hasDoi = doi !== "";
  const hasParentDoi = parentDoi !== "";
  const isDoiCreated = currentIdentifier !== "";

  const _isManagedSelected =
    isManagedSelected === undefined
      ? hasManagedIdentifier ||
        (currentIdentifier === "" && doiDefaultSelection === "no") // i.e pids: {}
      : isManagedSelected;

  const canBeManagedAndUnmanaged = canBeManaged && canBeUnmanaged;

  const fieldError = getFieldErrors(form, fieldPath);

  return (
    <>
      <Form.Field required={required || hasParentDoi} error={fieldError ? true : false}>
        <FieldLabel htmlFor={fieldPath} icon={pidIcon} label={fieldLabel} />
      </Form.Field>

      {canBeManagedAndUnmanaged && (
        <ManagedUnmanagedSwitch
          disabled={
            (isEditingPublishedRecord || hasManagedIdentifier) &&
            (hasDoi || isDoiCreated)
          }
          isManagedSelected={_isManagedSelected}
          onManagedUnmanagedChange={(userSelectedManaged) => {
            if (userSelectedManaged) {
              form.setFieldValue("pids", {});
            } else {
              onExternalIdentifierChanged("");
            }
            form.setFieldError(fieldPath, false);
            setIsManagedSelected(userSelectedManaged);
          }}
          pidLabel={pidLabel}
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

      {canBeUnmanaged && !_isManagedSelected && (
        <UnmanagedIdentifierCmp
          identifier={unmanagedIdentifier}
          onIdentifierChanged={(identifier) => {
            onExternalIdentifierChanged(identifier);
          }}
          form={form}
          fieldPath={fieldPath}
          pidPlaceholder={pidPlaceholder}
          helpText={unmanagedHelpText}
        />
      )}
    </>
  );
}

RequiredPIDField.propTypes = {
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
  doiDefaultSelection: PropTypes.string.isRequired,
};
