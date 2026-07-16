/*
 * SPDX-FileCopyrightText: 2020-2026 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import React, { Component } from "react";
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

class CreatibutorsFieldForm extends Component {
  // Refs hold the latest Formik array helpers. Formik recreates these functions
  // on every render, but we need stable references so the list doesn't re-render
  // when unrelated fields change.
  _removeRef = { current: null };
  _replaceRef = { current: null };
  _moveRef = { current: null };

  stableRemove = (index) => this._removeRef.current(index);
  stableReplace = (index, newValue) => this._replaceRef.current(index, newValue);
  stableMove = (from, to) => this._moveRef.current(from, to);

  // Cache sorted role options so a new array isn't created on every render.
  _lastRoleOptions = null;
  _sortedRoleOptions = null;
  getSortedRoleOptions() {
    const { roleOptions } = this.props;
    if (roleOptions !== this._lastRoleOptions) {
      this._lastRoleOptions = roleOptions;
      this._sortedRoleOptions = sortOptions(roleOptions);
    }
    return this._sortedRoleOptions;
  }

  // Cache the context value so CreatibutorsFieldItem consumers only re-render
  // when one of the static config props actually changes reference.
  _lastItemContextValue = null;
  getItemContextValue() {
    const {
      roleOptions,
      schema,
      autocompleteNames,
      modal: { addLabel, editLabel },
      serializeSuggestions,
      serializeCreatibutor,
      deserializeCreatibutor,
    } = this.props;
    if (
      !this._lastItemContextValue ||
      this._lastItemContextValue.roleOptions !== roleOptions ||
      this._lastItemContextValue.schema !== schema ||
      this._lastItemContextValue.autocompleteNames !== autocompleteNames ||
      this._lastItemContextValue.addLabel !== addLabel ||
      this._lastItemContextValue.editLabel !== editLabel ||
      this._lastItemContextValue.serializeSuggestions !== serializeSuggestions ||
      this._lastItemContextValue.serializeCreatibutor !== serializeCreatibutor ||
      this._lastItemContextValue.deserializeCreatibutor !== deserializeCreatibutor
    ) {
      this._lastItemContextValue = {
        roleOptions,
        schema,
        autocompleteNames,
        addLabel,
        editLabel,
        serializeSuggestions,
        serializeCreatibutor,
        deserializeCreatibutor,
      };
    }
    return this._lastItemContextValue;
  }

  handleOnCreatibutorChange = (selectedCreatibutor) => {
    const { push: formikArrayPush } = this.props;
    formikArrayPush({ ...selectedCreatibutor, highlighted: true }); // Highlight the new row on add / bulk-import
  };

  handleAddCreatibutorsFromFile = (entries) => {
    entries.forEach((entry) => this.handleOnCreatibutorChange(entry));
  };

  render() {
    const {
      form: { values, errors, initialErrors, initialValues },
      remove: formikArrayRemove,
      replace: formikArrayReplace,
      move: formikArrayMove,
      name: fieldPath,
      label,
      labelIcon,
      roleOptions,
      schema,
      modal,
      autocompleteNames,
      addButtonLabel,
      addButtonHelpText,
      serializeSuggestions,
      serializeCreatibutor,
      deserializeCreatibutor,
    } = this.props;

    // Keep refs pointing at the latest helpers without changing their identity.
    this._removeRef.current = formikArrayRemove;
    this._replaceRef.current = formikArrayReplace;
    this._moveRef.current = formikArrayMove;

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
        <CreatibutorsItemContext.Provider value={this.getItemContextValue()}>
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
                  removeCreatibutor={this.stableRemove}
                  replaceCreatibutor={this.stableReplace}
                  moveCreatibutor={this.stableMove}
                />
              )}

              <div className="creatibutors-action-bar mt-15">
                <CreatibutorsModal
                  onCreatibutorChange={this.handleOnCreatibutorChange}
                  action="add"
                  addLabel={modal.addLabel}
                  editLabel={modal.editLabel}
                  roleOptions={this.getSortedRoleOptions()}
                  schema={schema}
                  autocompleteNames={autocompleteNames}
                  serializeSuggestions={serializeSuggestions}
                  serializeCreatibutor={serializeCreatibutor}
                  deserializeCreatibutor={deserializeCreatibutor}
                  trigger={
                    <Button
                      type="button"
                      icon
                      labelPosition="left"
                      className={className}
                    >
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
                  onConfirm={this.handleAddCreatibutorsFromFile}
                  trigger={
                    <Button
                      type="button"
                      icon
                      labelPosition="left"
                      className={className}
                    >
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
  }
}

export class CreatibutorsFieldComponent extends Component {
  // Stable class-instance function so FieldArray never sees a new `component`
  // reference on unrelated Formik state changes.
  _renderForm = (formikProps) => (
    <CreatibutorsFieldForm {...formikProps} {...this.props} />
  );

  render() {
    const { fieldPath } = this.props;
    return <FieldArray name={fieldPath} component={this._renderForm} />;
  }
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

CreatibutorsFieldForm.defaultProps = {
  autocompleteNames: "search",
  label: i18next.t("Authors"),
  labelIcon: "user",
  modal: {
    addLabel: i18next.t("Add author"),
    editLabel: i18next.t("Edit author"),
  },
  addButtonLabel: i18next.t("Add author"),
  addButtonHelpText: undefined,
  serializeSuggestions: undefined,
  serializeCreatibutor: undefined,
  deserializeCreatibutor: undefined,
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

CreatibutorsFieldComponent.defaultProps = {
  autocompleteNames: "search",
  label: undefined,
  labelIcon: undefined,
  roleOptions: undefined,
  modal: {
    addLabel: i18next.t("Add author"),
    editLabel: i18next.t("Edit author"),
  },
  addButtonLabel: i18next.t("Add author"),
  addButtonHelpText: undefined,
  serializeSuggestions: undefined,
  serializeCreatibutor: undefined,
  deserializeCreatibutor: undefined,
};

export const CreatibutorsField = showHideOverridable(
  "InvenioRdmRecords.DepositForm.CreatibutorsField",
  CreatibutorsFieldComponent
);
