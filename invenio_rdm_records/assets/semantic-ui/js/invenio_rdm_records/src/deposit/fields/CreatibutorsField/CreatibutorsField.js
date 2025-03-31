// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { getIn, FieldArray } from "formik";
import { Button, Form, List, Icon } from "semantic-ui-react";
import _get from "lodash/get";
import { FeedbackLabel, FieldLabel } from "react-invenio-forms";

import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";

import { CreatibutorsModal } from "./CreatibutorsModal";
import { CreatibutorsFieldItem } from "./CreatibutorsFieldItem";
import { CREATIBUTOR_TYPE } from "./type";
import { sortOptions } from "../../utils";
import { i18next } from "@translations/invenio_rdm_records/i18next";

const creatibutorNameDisplay = (value) => {
  const creatibutorType = _get(value, "person_or_org.type", CREATIBUTOR_TYPE.PERSON);
  const isPerson = creatibutorType === CREATIBUTOR_TYPE.PERSON;

  const familyName = _get(value, "person_or_org.family_name", "");
  const givenName = _get(value, "person_or_org.given_name", "");
  const affiliations = value?.affiliations.map(
    (affiliation) => affiliation.text || affiliation.name
  );
  const name = _get(value, `person_or_org.name`);

  const affiliation = affiliations.length ? ` (${affiliations.join(", ")})` : "";

  if (isPerson) {
    const givenNameSuffix = givenName ? `, ${givenName}` : "";
    return `${familyName}${givenNameSuffix}${affiliation}`;
  }

  return `${name}${affiliation}`;
};

class CreatibutorsFieldForm extends Component {
  handleOnContributorChange = (selectedCreatibutor) => {
    const { push: formikArrayPush } = this.props;
    formikArrayPush(selectedCreatibutor);
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
    } = this.props;

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

    return (
      <DndProvider backend={HTML5Backend}>
        <Form.Field required={schema === "creators"} className={className}>
          <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
          <List>
            {creatibutorsList.map((value, index) => {
              const key = `${fieldPath}.${index}`;
              const displayName = creatibutorNameDisplay(value);

              return (
                <CreatibutorsFieldItem
                  key={key}
                  creatibutorError={
                    creatibutorsError &&
                    typeof creatibutorsError !== "string" &&
                    creatibutorsError[index]
                  }
                  {...{
                    displayName,
                    index,
                    roleOptions,
                    schema,
                    compKey: key,
                    initialCreatibutor: value,
                    removeCreatibutor: formikArrayRemove,
                    replaceCreatibutor: formikArrayReplace,
                    moveCreatibutor: formikArrayMove,
                    addLabel: modal.addLabel,
                    editLabel: modal.editLabel,
                    autocompleteNames: autocompleteNames,
                  }}
                />
              );
            })}
          </List>
          <CreatibutorsModal
            onCreatibutorChange={this.handleOnContributorChange}
            action="add"
            addLabel={modal.addLabel}
            editLabel={modal.editLabel}
            roleOptions={sortOptions(roleOptions)}
            schema={schema}
            autocompleteNames={autocompleteNames}
            trigger={
              <Button type="button" icon labelPosition="left" className={className}>
                <Icon name="add" />
                {addButtonLabel}
              </Button>
            }
          />
          {generalCreatibutorsError && (
            <FeedbackLabel errorMessage={generalCreatibutorsError} />
          )}
        </Form.Field>
      </DndProvider>
    );
  }
}

export class CreatibutorsField extends Component {
  render() {
    const { fieldPath } = this.props;

    return (
      <FieldArray
        name={fieldPath}
        component={(formikProps) => (
          <CreatibutorsFieldForm {...formikProps} {...this.props} />
        )}
      />
    );
  }
}

CreatibutorsFieldForm.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  addButtonLabel: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  roleOptions: PropTypes.array.isRequired,
  form: PropTypes.object.isRequired,
  remove: PropTypes.func.isRequired,
  replace: PropTypes.func.isRequired,
  move: PropTypes.func.isRequired,
  push: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
};

CreatibutorsFieldForm.defaultProps = {
  autocompleteNames: "search",
  label: i18next.t("Creators"),
  labelIcon: "user",
  modal: {
    addLabel: i18next.t("Add creator"),
    editLabel: i18next.t("Edit creator"),
  },
  addButtonLabel: i18next.t("Add creator"),
};

CreatibutorsField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  addButtonLabel: PropTypes.string,
  modal: PropTypes.shape({
    addLabel: PropTypes.string.isRequired,
    editLabel: PropTypes.string.isRequired,
  }),
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  roleOptions: PropTypes.array,
};

CreatibutorsField.defaultProps = {
  autocompleteNames: "search",
  label: undefined,
  labelIcon: undefined,
  roleOptions: undefined,
  modal: {
    addLabel: i18next.t("Add creator"),
    editLabel: i18next.t("Edit creator"),
  },
  addButtonLabel: i18next.t("Add creator"),
};
