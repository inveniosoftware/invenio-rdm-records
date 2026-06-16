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
import { FileImportReviewModal } from "./FileImportReviewModal";
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

  handleOnCreatibutorChange = (selectedCreatibutor) => {
    const { push: formikArrayPush } = this.props;
    formikArrayPush(selectedCreatibutor);
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
      scrollThreshold,
      batchSize,
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
        <DndProvider backend={HTML5Backend}>
          <Form.Field required={schema === "creators"} className={className}>
            <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />

            {totalCount > 0 && (
              <CreatibutorsInlinePanel
                list={creatibutorsList}
                keyPrefix={fieldPath}
                schema={schema}
                scrollThreshold={scrollThreshold}
                batchSize={batchSize}
                creatibutorErrors={
                  creatibutorsError && typeof creatibutorsError !== "string"
                    ? creatibutorsError
                    : undefined
                }
                removeCreatibutor={this.stableRemove}
                replaceCreatibutor={this.stableReplace}
                moveCreatibutor={this.stableMove}
                roleOptions={roleOptions}
                addLabel={modal.addLabel}
                editLabel={modal.editLabel}
                autocompleteNames={autocompleteNames}
                serializeSuggestions={serializeSuggestions}
                serializeCreatibutor={serializeCreatibutor}
                deserializeCreatibutor={deserializeCreatibutor}
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
                  <Button type="button" icon labelPosition="left" className={className}>
                    <Icon name="add" />
                    {addButtonLabel}
                  </Button>
                }
              />

              <FileImportReviewModal
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
                  <Button type="button" icon labelPosition="left" className={className}>
                    <Icon name="upload" />
                    {isContributors
                      ? i18next.t("Add contributors from file")
                      : i18next.t("Add authors from file")}
                  </Button>
                }
                scrollThreshold={scrollThreshold}
                batchSize={batchSize}
              />
            </div>

            {addButtonHelpText && (
              <label className="helptext">{addButtonHelpText}</label>
            )}
            {generalCreatibutorsError && <FeedbackLabel fieldPath={fieldPath} />}
          </Form.Field>
        </DndProvider>
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
    return <FieldArray name={this.props.fieldPath} component={this._renderForm} />;
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
  scrollThreshold: PropTypes.number,
  batchSize: PropTypes.number,
  ...mandatoryFieldCommonProps,
};

CreatibutorsFieldForm.defaultProps = {
  scrollThreshold: 10,
  batchSize: 20,
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
  scrollThreshold: PropTypes.number,
  batchSize: PropTypes.number,
  ...mandatoryFieldCommonProps,
};

CreatibutorsFieldComponent.defaultProps = {
  scrollThreshold: 10,
  batchSize: 20,
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
