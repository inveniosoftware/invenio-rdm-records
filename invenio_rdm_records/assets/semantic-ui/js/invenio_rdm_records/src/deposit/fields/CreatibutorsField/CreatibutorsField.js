/*
 * SPDX-FileCopyrightText: 2020-2026 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { memo, useCallback, useMemo, useRef } from "react";
import PropTypes from "prop-types";
import { getIn, FieldArray } from "formik";
import { Button, Form, Icon } from "semantic-ui-react";
import {
  FeedbackLabel,
  FieldLabel,
  mandatoryFieldCommonProps,
  showHideOverridable,
} from "react-invenio-forms";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";
import { CreatibutorsModal } from "./CreatibutorsModal";
import { CreatibutorsInlinePanel } from "./CreatibutorsDisplay/CreatibutorsInlinePanel";
import { CreatibutorsFileModal } from "./CreatibutorsFileModal";
import { CreatibutorsItemContext } from "./CreatibutorsFieldItem";
import { sortOptions } from "../../utils";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import Overridable from "react-overridable";

// Kept at module level so the default keeps a stable identity across renders.
const DEFAULT_MODAL = {
  addLabel: i18next.t("Add author"),
  editLabel: i18next.t("Edit author"),
};
const DEFAULT_ADD_BUTTON_LABEL = i18next.t("Add author");
const DEFAULT_LABEL = i18next.t("Authors");

// Re-render only when related Formik data changed, helps immensely with performance
// due to inline search changing the list.
const arePropsEqual = (prevProps, nextProps) => {
  const { name, form } = prevProps;
  const nextForm = nextProps.form;
  if (getIn(form.values, name) !== getIn(nextForm.values, name)) return false;
  if (getIn(form.errors, name) !== getIn(nextForm.errors, name)) return false;
  if (getIn(form.initialErrors, name) !== getIn(nextForm.initialErrors, name))
    return false;
  if (getIn(form.initialValues, name) !== getIn(nextForm.initialValues, name))
    return false;
  return true;
};

const CreatibutorsFieldForm = memo(function CreatibutorsFieldForm({
  form: { values, errors, initialErrors, initialValues },
  remove: formikArrayRemove,
  replace: formikArrayReplace,
  move: formikArrayMove,
  push: formikArrayPush,
  name: fieldPath,
  roleOptions,
  schema,
  addButtonHelpText,
  serializeSuggestions,
  serializeCreatibutor,
  deserializeCreatibutor,
  autocompleteNames = "search",
  label = DEFAULT_LABEL,
  labelIcon = "user",
  modal = DEFAULT_MODAL,
  addButtonLabel = DEFAULT_ADD_BUTTON_LABEL,
}) {
  const highlightRef = useRef({ from: 0, until: 0, shown: new Set() });

  // Refs hold the latest Formik array helpers. Formik recreates these functions
  // on every render, but we need stable references so the list doesn't re-render
  // when unrelated fields change.
  const helpersRef = useRef(null);
  helpersRef.current = {
    remove: formikArrayRemove,
    replace: formikArrayReplace,
    move: formikArrayMove,
    push: formikArrayPush,
    values,
    fieldPath,
  };

  const stableRemove = useCallback((index) => helpersRef.current.remove(index), []);
  const stableReplace = useCallback(
    (index, newValue) => helpersRef.current.replace(index, newValue),
    []
  );
  const stableMove = useCallback((from, to) => helpersRef.current.move(from, to), []);

  // Cache sorted role options so a new array isn't created on every render.
  const sortedRoleOptions = useMemo(() => sortOptions(roleOptions), [roleOptions]);

  const { addLabel, editLabel } = modal;

  // Cache the context value so CreatibutorsFieldItem consumers only re-render
  // when one of the static config props actually changes reference.
  const itemContextValue = useMemo(
    () => ({
      roleOptions,
      schema,
      autocompleteNames,
      addLabel,
      editLabel,
      serializeSuggestions,
      serializeCreatibutor,
      deserializeCreatibutor,
      highlight: highlightRef.current,
    }),
    [
      roleOptions,
      schema,
      autocompleteNames,
      addLabel,
      editLabel,
      serializeSuggestions,
      serializeCreatibutor,
      deserializeCreatibutor,
    ]
  );

  const handleOnCreatibutorChange = useCallback((selectedCreatibutor) => {
    const { push, values: formValues, fieldPath: name } = helpersRef.current;
    const h = highlightRef.current;
    h.from = getIn(formValues, name, []).length;
    h.until = Date.now() + 2000; // 2 seconds
    h.shown.clear();
    push(selectedCreatibutor);
  }, []);

  const handleAddCreatibutorsFromFile = useCallback(
    (entries) => {
      entries.forEach((entry) => handleOnCreatibutorChange(entry));
    },
    [handleOnCreatibutorChange]
  );

  const creatibutorsList = getIn(values, fieldPath, []);
  const formikInitialValues = getIn(initialValues, fieldPath, []);

  const error = getIn(errors, fieldPath, null);
  const initialError = getIn(initialErrors, fieldPath, null);
  const creatibutorsError =
    error || (creatibutorsList === formikInitialValues && initialError);

  let className = "";
  if (creatibutorsError) {
    className =
      typeof creatibutorsError !== "string" ? creatibutorsError.severity : "error";
  }

  // Check if there is a general error (since there can also be errors for specific creatibutors).
  let generalCreatibutorsError;
  if (typeof creatibutorsError === "string") {
    // If there is a string at the top level, it means that this is a general error.
    generalCreatibutorsError = creatibutorsError;
  } else if (typeof creatibutorsError === "object" && creatibutorsError !== null) {
    // If there is an object at the top level, try to extract the new error format.
    generalCreatibutorsError = {
      message: creatibutorsError?.message,
      severity: creatibutorsError?.severity,
      description: creatibutorsError?.description,
    };
  }

  const isContributors = schema === "contributors";
  const totalCount = creatibutorsList.length;

  // Display label for the inline filter placeholder.
  const type = isContributors ? "contributors" : "authors/creators";

  return (
    <Overridable
      id="InvenioRdmRecords.DepositForm.CreatibutorsField.Container"
      labelIcon={labelIcon}
      label={label}
      roleOptions={roleOptions}
      schema={schema}
      addLabel={modal.addLabel}
      editLabel={modal.editLabel}
      addButtonLabel={addButtonLabel}
      addButtonHelpText={addButtonHelpText}
      className={className}
    >
      <CreatibutorsItemContext.Provider value={itemContextValue}>
        <DndProvider backend={HTML5Backend}>
          <Form.Field required={schema === "creators"} className={className}>
            <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />

            {totalCount > 0 && (
              <CreatibutorsInlinePanel
                list={creatibutorsList}
                keyPrefix={fieldPath}
                type={type}
                creatibutorErrors={
                  creatibutorsError && typeof creatibutorsError !== "string"
                    ? creatibutorsError
                    : undefined
                }
                removeCreatibutor={stableRemove}
                replaceCreatibutor={stableReplace}
                moveCreatibutor={stableMove}
              />
            )}

            <div className="creatibutors-action-bar mt-15">
              <CreatibutorsModal
                onCreatibutorChange={handleOnCreatibutorChange}
                action="add"
                addLabel={modal.addLabel}
                editLabel={modal.editLabel}
                roleOptions={sortedRoleOptions}
                schema={schema}
                autocompleteNames={autocompleteNames}
                serializeSuggestions={serializeSuggestions}
                serializeCreatibutor={serializeCreatibutor}
                deserializeCreatibutor={deserializeCreatibutor}
                trigger={
                  <Button type="button" icon labelPosition="left" className={className}>
                    <Icon name="add" />
                    {addButtonLabel}
                  </Button>
                }
              />

              <CreatibutorsFileModal
                roleOptions={roleOptions}
                schema={schema}
                autocompleteNames={autocompleteNames}
                addLabel={modal.addLabel}
                editLabel={modal.editLabel}
                serializeSuggestions={serializeSuggestions}
                serializeCreatibutor={serializeCreatibutor}
                deserializeCreatibutor={deserializeCreatibutor}
                onConfirm={handleAddCreatibutorsFromFile}
                trigger={
                  <Button type="button" icon labelPosition="left" className={className}>
                    <Icon name="upload" />
                    {isContributors
                      ? i18next.t("Add contributors from file")
                      : i18next.t("Add authors from file")}
                  </Button>
                }
              />
            </div>

            {addButtonHelpText && (
              <label className="helptext">{addButtonHelpText}</label>
            )}
            {generalCreatibutorsError && <FeedbackLabel fieldPath={fieldPath} />}
          </Form.Field>
        </DndProvider>
      </CreatibutorsItemContext.Provider>
    </Overridable>
  );
},
arePropsEqual);

export function CreatibutorsFieldComponent(props) {
  const { fieldPath } = props;

  // Keep a ref to the latest props so that `renderForm` can stay stable: passing a
  // new `component` to `FieldArray` on every render would remount the whole subtree.
  const propsRef = useRef(null);
  propsRef.current = props;

  const renderForm = useCallback(
    (formikProps) => <CreatibutorsFieldForm {...formikProps} {...propsRef.current} />,
    []
  );

  return <FieldArray name={fieldPath} component={renderForm} />;
}

CreatibutorsFieldForm.propTypes = {
  addButtonLabel: PropTypes.string,
  addButtonHelpText: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  roleOptions: PropTypes.array.isRequired,
  form: PropTypes.object.isRequired,
  remove: PropTypes.func.isRequired,
  replace: PropTypes.func.isRequired,
  move: PropTypes.func.isRequired,
  push: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
  ...mandatoryFieldCommonProps,
};

CreatibutorsFieldComponent.propTypes = {
  addButtonLabel: PropTypes.string,
  addButtonHelpText: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  roleOptions: PropTypes.array,
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
  ...mandatoryFieldCommonProps,
};

export const CreatibutorsField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.CreatibutorsField",
  CreatibutorsFieldComponent
);
