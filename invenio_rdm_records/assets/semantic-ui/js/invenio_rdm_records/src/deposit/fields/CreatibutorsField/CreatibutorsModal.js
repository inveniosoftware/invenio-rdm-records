/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-FileCopyrightText: 2022 data-futures.org.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import _find from "lodash/find";
import _get from "lodash/get";
import _isEmpty from "lodash/isEmpty";
import _map from "lodash/map";
import PropTypes from "prop-types";
import { Component, createRef } from "react";
import {
  RadioField,
  RemoteSelectField,
  SelectField,
  TextField,
  AffiliationsSuggestions,
} from "react-invenio-forms";
import { Button, Form, Modal } from "semantic-ui-react";
import * as Yup from "yup";
import { AffiliationsField } from "./../AffiliationsField";
import { CreatibutorsIdentifiers } from "./CreatibutorsIdentifiers";
import { CREATIBUTOR_TYPE } from "./type";
import Overridable from "react-overridable";

const ModalActions = {
  ADD: "add",
  EDIT: "edit",
};

const NamesAutocompleteOptions = {
  SEARCH: "search",
  SEARCH_ONLY: "search_only",
  OFF: "off",
};

const creatibutorsModalDefaultPropRoleOptions = [];
const creatibutorsModalDefaultPropInitialCreatibutor = {};
export function CreatibutorsModal({autocompleteNames = "search", initialCreatibutor = creatibutorsModalDefaultPropInitialCreatibutor, action, addLabel, editLabel, serializeCreatibutor = undefined, deserializeCreatibutor = undefined, schema, onCreatibutorChange, roleOptions = creatibutorsModalDefaultPropRoleOptions, trigger, serializeSuggestions = undefined}) {
  const [open, setOpen] = React.useState(false);
  const [saveAndContinueLabel, setSaveAndContinueLabel] = React.useState(i18next.t("Save and add another"));
  const [action, setAction] = React.useState(null);
  const [showPersonForm, setShowPersonForm] = React.useState(autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY ||
        !_isEmpty(initialCreatibutor));
  const [isOrganization, setIsOrganization] = React.useState(!_isEmpty(initialCreatibutor) &&
        initialCreatibutor.person_or_org.type === CREATIBUTOR_TYPE.ORGANIZATION);
  const [personIdentifiers, setPersonIdentifiers] = React.useState([]);
  const [personAffiliations, setPersonAffiliations] = React.useState([]);
  const [organizationIdentifiers, setOrganizationIdentifiers] = React.useState([]);
  const [organizationAffiliations, setOrganizationAffiliations] = React.useState([]);
  const inputRef = React.useRef(null);
  const identifiersRef = React.useRef(null);
  const affiliationsRef = React.useRef(null);
  const namesAutocompleteRef = React.useRef(null);

  function initStatesFromInitialCreatibutor(initialCreatibutor) {
    const { affiliations = [] } = initialCreatibutor;
    const { isOrganization } = this.state;
    const identifiers = initialCreatibutor.person_or_org.identifiers?.map(
      (identifier) => identifier.identifier
    );
    this.setState({
      personIdentifiers: isOrganization ? [] : identifiers,
      personAffiliations: isOrganization ? [] : affiliations,
      organizationIdentifiers: isOrganization ? identifiers : [],
      organizationAffiliations: isOrganization ? affiliations : [],
    });
  }

  CreatorSchema = Yup.object({
    person_or_org: Yup.object({
      type: Yup.string(),
      family_name: Yup.string().when("type", (type, schema) => {
        if (type === CREATIBUTOR_TYPE.PERSON && this.isCreator()) {
          return schema.required(i18next.t("Family name is a required field."));
        }
      }),
      name: Yup.string().when("type", (type, schema) => {
        if (type === CREATIBUTOR_TYPE.ORGANIZATION && this.isCreator()) {
          return schema.required(i18next.t("Name is a required field."));
        }
      }),
    }),
    role: Yup.string().when("_", (_, schema) => {
      if (!this.isCreator()) {
        return schema.required(i18next.t("Role is a required field."));
      }
    }),
  })

  const openModal = () => {
    this.setState({ open: true, action: null }, () => {
      const { initialCreatibutor } = this.props;
      if (!_isEmpty(initialCreatibutor)) {
        const { isOrganization } = this.state;

        if (isOrganization) {
          // Set family and given name to empty for organizations
          initialCreatibutor.person_or_org.family_name = "";
          initialCreatibutor.person_or_org.given_name = "";
        } else {
          // Set name to empty for persons
          initialCreatibutor.person_or_org.name = "";
        }

        initStatesFromInitialCreatibutor(initialCreatibutor);
      }
    });
  };

  const closeModal = () => {
    this.setState({
      personAffiliations: [],
      personIdentifiers: [],
      organizationAffiliations: [],
      organizationIdentifiers: [],
      open: false,
      action: null,
    });
  };

  const changeContent = () => {
    setSaveAndContinueLabel(i18next.t("Added"));
    // change in 2 sec
    setTimeout(() => {
      setSaveAndContinueLabel(i18next.t("Save and add another"));
    }, 2000);
  };

  const displayActionLabel = () => {
    const { action, addLabel, editLabel } = this.props;

    return action === ModalActions.ADD ? addLabel : editLabel;
  };

  const serializeCreatibutor = (submittedCreatibutor) => {
    const { personIdentifiers } = this.state;
    const { initialCreatibutor, serializeCreatibutor } = this.props;
    if (serializeCreatibutor) {
      return serializeCreatibutor(submittedCreatibutor, initialCreatibutor);
    }

    const identifiersFieldPath = "person_or_org.identifiers";
    const affiliationsFieldPath = "affiliations";
    // The modal is saving only identifiers values, thus
    // identifiers with existing scheme are trimmed
    const initialIdentifiers = _get(initialCreatibutor, identifiersFieldPath, []);
    const submittedIdentifiers = _get(submittedCreatibutor, identifiersFieldPath, []);

    // Here we merge back the known scheme for the submitted identifiers
    const identifiers = submittedIdentifiers.map((identifier) => {
      // First search in state with the newly submitted identifiers
      const stateField = _find(personIdentifiers, { identifier: identifier });
      if (stateField) {
        return stateField;
      }
      // If not found, search in initial identifiers
      const initialField = _find(initialIdentifiers, { identifier: identifier });
      if (initialField) {
        return initialField;
      }
      // If not found, return as key-value pair
      return { identifier: identifier };
    });

    const submittedAffiliations = _get(submittedCreatibutor, affiliationsFieldPath, []);

    return {
      ...submittedCreatibutor,
      person_or_org: {
        ...submittedCreatibutor.person_or_org,
        identifiers,
      },
      affiliations: submittedAffiliations,
    };
  };

  const deserializeCreatibutor = (initialCreatibutor) => {
    const { deserializeCreatibutor } = this.props;
    if (deserializeCreatibutor) {
      return deserializeCreatibutor(initialCreatibutor);
    }
    const identifiersFieldPath = "person_or_org.identifiers";

    return {
      // default type to personal
      person_or_org: {
        type: CREATIBUTOR_TYPE.PERSON,
        ...initialCreatibutor.person_or_org,
        identifiers: _map(
          _get(initialCreatibutor, identifiersFieldPath, []),
          "identifier"
        ),
      },
      affiliations: _get(initialCreatibutor, "affiliations", []),
      role: _get(initialCreatibutor, "role", ""),
    };
  };

  const isCreator = () => {
    const { schema } = this.props;

    return schema === "creators";
  };

  const onSubmit = (values, formikBag) => {
    const { onCreatibutorChange } = this.props;
    const { action } = this.state;

    onCreatibutorChange(serializeCreatibutor(values));
    formikBag.setSubmitting(false);
    formikBag.resetForm();
    switch (action) {
      case "saveAndContinue":
        // Needed to close and open the modal to reset the internal
        // state of the cmp inside the modal
        closeModal();
        openModal();
        changeContent();
        break;
      case "saveAndClose":
        closeModal();
        break;
      default:
        break;
    }
  };

  const serializeSuggestions = (creatibutors) => {
    const { isOrganization } = this.state;
    // TODO: AffiliationsSuggestions is wrongly named, since it also serializes authors,
    // this has to be fixed upstream though
    return AffiliationsSuggestions(creatibutors, isOrganization);
  };

  function updateIdentifiersAndAffiliations(
    formikProps,
    identifiers,
    affiliations,
    identifiersRef,
    affiliationsRef
  ) {
    const personOrOrgPath = `person_or_org`;
    const identifiersFieldPath = `${personOrOrgPath}.identifiers`;
    const affiliationsFieldPath = "affiliations";

    let chosen = {
      [identifiersFieldPath]: identifiers,
      [affiliationsFieldPath]: affiliations,
    };

    Object.entries(chosen).forEach(([path, value]) => {
      formikProps.form.setFieldValue(path, value);
    });

    // Update identifiers render
    identifiersRef.current.setState({
      selectedOptions: identifiersRef.current.valuesToOptions(identifiers),
    });

    // Update affiliations render
    const affiliationsState = affiliations.map(({ id, name }) => ({
      text: name,
      value: id ?? name,
      key: id ?? name,
      name,
    }));
    affiliationsRef.current.setState({
      suggestions: affiliationsState,
      selectedSuggestions: affiliationsState,
      searchQuery: null,
      error: false,
      open: false,
    });
  }

  const onOrganizationSearchChange = ({ formikProps }, selectedSuggestions) => {
    const selectedSuggestion = selectedSuggestions[0].extra;
    this.setState(
      {
        organizationIdentifiers: selectedSuggestion.identifiers
          .filter((identifier) => identifier.scheme !== "grid") // Filtering out org scheme (RDM_RECORDS_PERSONORG_SCHEMES) for unsupported one i.e. "grid"
          .map((identifier) => identifier.identifier),
        organizationAffiliations: [],
      },
      () => {
        const { organizationIdentifiers, organizationAffiliations } = this.state;

        formikProps.form.setFieldValue("person_or_org.name", selectedSuggestion.name);

        updateIdentifiersAndAffiliations(
          formikProps,
          organizationIdentifiers,
          organizationAffiliations,
          identifiersRef,
          affiliationsRef
        );
      }
    );
  };

  const onPersonSearchChange = ({ formikProps }, selectedSuggestions) => {
    if (selectedSuggestions[0].key === "manual-entry") {
      // Empty the autocomplete's selected values
      namesAutocompleteRef.current.setState({
        suggestions: [],
        selectedSuggestions: [],
      });
      setShowPersonForm(true);
      return;
    }

    const selectedSuggestion = selectedSuggestions[0].extra;
    this.setState(
      {
        showPersonForm: true,
        personIdentifiers: selectedSuggestion.identifiers.map(
          (identifier) => identifier
        ),
        personAffiliations: selectedSuggestion.affiliations.map(
          (affiliation) => affiliation
        ),
      },
      () => {
        const { personIdentifiers, personAffiliations } = this.state;
        const personOrOrgPath = `person_or_org`;
        const familyNameFieldPath = `${personOrOrgPath}.family_name`;
        const givenNameFieldPath = `${personOrOrgPath}.given_name`;

        let chosen = {
          [givenNameFieldPath]: selectedSuggestion.given_name,
          [familyNameFieldPath]: selectedSuggestion.family_name,
        };
        Object.entries(chosen).forEach(([path, value]) => {
          formikProps.form.setFieldValue(path, value);
        });

        updateIdentifiersAndAffiliations(
          formikProps,
          personIdentifiers.map((identifier) => identifier.identifier), // Only identifer value is needed for the form
          personAffiliations,
          identifiersRef,
          affiliationsRef
        );
      }
    );
  };

  const ActionLabel = displayActionLabel();
    return (
      <Formik
        initialValues={deserializeCreatibutor(initialCreatibutor)}
        onSubmit={onSubmit}
        enableReinitialize
        validationSchema={CreatorSchema}
        validateOnChange={false}
        validateOnBlur={false}
      >
        {({ values, resetForm, handleSubmit }) => {
          const personOrOrgPath = `person_or_org`;
          const typeFieldPath = `${personOrOrgPath}.type`;
          const familyNameFieldPath = `${personOrOrgPath}.family_name`;
          const givenNameFieldPath = `${personOrOrgPath}.given_name`;
          const organizationNameFieldPath = `${personOrOrgPath}.name`;
          const identifiersFieldPath = `${personOrOrgPath}.identifiers`;
          const affiliationsFieldPath = "affiliations";
          const roleFieldPath = "role";
          return (
            <Modal
              centered={false}
              onOpen={() => openModal()}
              open={open}
              trigger={trigger}
              onClose={() => {
                closeModal();
                resetForm();
              }}
              closeIcon
              closeOnDimmerClick={false}
            >
              <Modal.Header as="h2" className="pt-10 pb-10">
                {ActionLabel}
              </Modal.Header>
              <Modal.Content>
                <Form>
                  <Form.Group>
                    <RadioField
                      fieldPath={typeFieldPath}
                      label={i18next.t("Person")}
                      checked={_get(values, typeFieldPath) === CREATIBUTOR_TYPE.PERSON}
                      value={CREATIBUTOR_TYPE.PERSON}
                      onChange={({ formikProps }) => {
                        setIsOrganization(false);
                        formikProps.form.setFieldValue(
                          typeFieldPath,
                          CREATIBUTOR_TYPE.PERSON
                        );
                        formikProps.form.setFieldValue(
                          identifiersFieldPath,
                          personIdentifiers
                        );
                        formikProps.form.setFieldValue(
                          affiliationsFieldPath,
                          personAffiliations
                        );
                      }}
                      // eslint-disable-next-line
                      autoFocus
                      optimized
                    />
                    <RadioField
                      fieldPath={typeFieldPath}
                      label={i18next.t("Organization")}
                      checked={
                        _get(values, typeFieldPath) === CREATIBUTOR_TYPE.ORGANIZATION
                      }
                      value={CREATIBUTOR_TYPE.ORGANIZATION}
                      onChange={({ formikProps }) => {
                        setIsOrganization(true);
                        formikProps.form.setFieldValue(
                          typeFieldPath,
                          CREATIBUTOR_TYPE.ORGANIZATION
                        );
                        formikProps.form.setFieldValue(
                          affiliationsFieldPath,
                          organizationAffiliations
                        );
                        formikProps.form.setFieldValue(
                          identifiersFieldPath,
                          organizationIdentifiers
                        );
                      }}
                      optimized
                    />
                  </Form.Group>
                  {_get(values, typeFieldPath, "") === CREATIBUTOR_TYPE.PERSON ? (
                    <>
                      {autocompleteNames !== NamesAutocompleteOptions.OFF && (
                        <Overridable
                          id="InvenioRdmRecords.DepositForm.CreatibutorsModal.PersonRemoteSelectField"
                          initialCreatibutor={initialCreatibutor}
                          serializeSuggestions={
                            serializeSuggestions || serializeSuggestions
                          }
                          onValueChange={onPersonSearchChange}
                          ref={namesAutocompleteRef}
                        >
                          <RemoteSelectField
                            selectOnBlur={false}
                            selectOnNavigation={false}
                            searchInput={{
                              autoFocus: _isEmpty(initialCreatibutor),
                            }}
                            fieldPath="creators"
                            clearable
                            multiple={false}
                            allowAdditions={false}
                            placeholder={i18next.t(
                              "Search for persons by name, identifier, or affiliation..."
                            )}
                            noQueryMessage={i18next.t(
                              "Search for persons by name, identifier, or affiliation..."
                            )}
                            required={false}
                            // Disable UI-side filtering of search results
                            search={(options) => options}
                            suggestionAPIUrl="/api/names"
                            serializeSuggestions={
                              serializeSuggestions || serializeSuggestions
                            }
                            onValueChange={onPersonSearchChange}
                            ref={namesAutocompleteRef}
                          />
                        </Overridable>
                      )}
                      {showPersonForm && (
                        <>
                          <Overridable
                            id="InvenioRdmRecords.DepositForm.CreatibutorsModal.FullNameField"
                            familyNameFieldPath={familyNameFieldPath}
                            givenNameFieldPath={givenNameFieldPath}
                            isCreator={isCreator()}
                          >
                            <Form.Group widths="equal">
                              <TextField
                                label={i18next.t("Family name")}
                                placeholder={i18next.t("Family name")}
                                fieldPath={familyNameFieldPath}
                                required={isCreator()}
                              />
                              <TextField
                                label={i18next.t("Given names")}
                                placeholder={i18next.t("Given names")}
                                fieldPath={givenNameFieldPath}
                              />
                            </Form.Group>
                          </Overridable>
                          <Overridable
                            id="InvenioRdmRecords.DepositForm.CreatibutorsModal.PersonIdentifiersField"
                            ref={identifiersRef}
                            fieldPath={identifiersFieldPath}
                            values={values}
                          >
                            <CreatibutorsIdentifiers
                              initialOptions={_map(
                                _get(values, identifiersFieldPath, []),
                                (identifier) => ({
                                  text: identifier,
                                  value: identifier,
                                  key: identifier,
                                })
                              )}
                              fieldPath={identifiersFieldPath}
                              ref={identifiersRef}
                            />
                          </Overridable>
                          <Overridable
                            id="InvenioRdmRecords.DepositForm.CreatibutorsModal.PersonAffiliationsField"
                            ref={affiliationsRef}
                            fieldPath={affiliationsFieldPath}
                          >
                            <AffiliationsField
                              fieldPath={affiliationsFieldPath}
                              selectRef={affiliationsRef}
                            />
                          </Overridable>
                        </>
                      )}
                    </>
                  ) : (
                    <>
                      {autocompleteNames !== NamesAutocompleteOptions.OFF && (
                        <Overridable
                          id="InvenioRdmRecords.DepositForm.CreatibutorsModal.OrganizationRemoteSelectField"
                          initialCreatibutor={initialCreatibutor}
                          serializeSuggestions={
                            serializeSuggestions || serializeSuggestions
                          }
                          onValueChange={onOrganizationSearchChange}
                        >
                          <RemoteSelectField
                            selectOnBlur={false}
                            selectOnNavigation={false}
                            searchInput={{
                              autoFocus: _isEmpty(initialCreatibutor),
                            }}
                            fieldPath="creators"
                            clearable
                            multiple={false}
                            allowAdditions={false}
                            placeholder={i18next.t(
                              "Search for an organization by name, identifier, or affiliation..."
                            )}
                            noQueryMessage={i18next.t(
                              "Search for organization by name, identifier, or affiliation..."
                            )}
                            required={false}
                            // Disable UI-side filtering of search results
                            search={(options) => options}
                            suggestionAPIUrl="/api/affiliations"
                            serializeSuggestions={
                              serializeSuggestions || serializeSuggestions
                            }
                            onValueChange={onOrganizationSearchChange}
                          />
                        </Overridable>
                      )}
                      <Overridable
                        id="InvenioRdmRecords.DepositForm.CreatibutorsModal.OrganizationNameField"
                        fieldPath={organizationNameFieldPath}
                        ref={inputRef}
                        isCreator={isCreator()}
                      >
                        <TextField
                          label={i18next.t("Name")}
                          placeholder={i18next.t("Organization name")}
                          fieldPath={organizationNameFieldPath}
                          required={isCreator()}
                          // forward ref to Input component because Form.Input
                          // doesn't handle it
                          input={{ ref: inputRef }}
                        />
                      </Overridable>
                      <Overridable
                        id="InvenioRdmRecords.DepositForm.CreatibutorsModal.OrganizationIdentifiersField"
                        ref={identifiersRef}
                        values={values}
                        fieldPath={identifiersFieldPath}
                      >
                        <CreatibutorsIdentifiers
                          initialOptions={_map(
                            _get(values, identifiersFieldPath, []),
                            (identifier) => ({
                              text: identifier,
                              value: identifier,
                              key: identifier,
                            })
                          )}
                          fieldPath={identifiersFieldPath}
                          ref={identifiersRef}
                          placeholder={i18next.t("e.g. ROR, ISNI or GND.")}
                        />
                      </Overridable>
                      <Overridable
                        id="InvenioRdmRecords.DepositForm.CreatibutorsModal.OrganizationAffiliationsField"
                        fieldPath={affiliationsFieldPath}
                        ref={affiliationsRef}
                      >
                        <AffiliationsField
                          fieldPath={affiliationsFieldPath}
                          selectRef={affiliationsRef}
                        />
                      </Overridable>
                    </>
                  )}
                  {(_get(values, typeFieldPath) === CREATIBUTOR_TYPE.ORGANIZATION ||
                    (showPersonForm &&
                      _get(values, typeFieldPath) === CREATIBUTOR_TYPE.PERSON)) && (
                    <Overridable
                      id="InvenioRdmRecords.DepositForm.CreatibutorsModal.RoleSelectField"
                      fieldPath={roleFieldPath}
                      roleOptions={roleOptions}
                      isCreator={isCreator()}
                    >
                      <SelectField
                        fieldPath={roleFieldPath}
                        label={i18next.t("Role")}
                        options={roleOptions}
                        placeholder={i18next.t("Select role")}
                        {...(isCreator() && { clearable: true })}
                        required={!isCreator()}
                        optimized
                        scrolling
                      />
                    </Overridable>
                  )}
                </Form>
              </Modal.Content>
              <Modal.Actions>
                <Button
                  name="cancel"
                  onClick={() => {
                    resetForm();
                    closeModal();
                  }}
                  icon="remove"
                  content={i18next.t("Cancel")}
                  floated="left"
                />
                {action === ModalActions.ADD && (
                  <Button
                    name="submit"
                    onClick={() => {
                      this.setState(
                        {
                          action: "saveAndContinue",
                          showPersonForm:
                            autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY,
                        },
                        () => {
                          handleSubmit();
                        }
                      );
                    }}
                    primary
                    icon="checkmark"
                    content={saveAndContinueLabel}
                  />
                )}
                <Button
                  name="submit"
                  onClick={() => {
                    this.setState(
                      {
                        action: "saveAndClose",
                        showPersonForm:
                          autocompleteNames !== NamesAutocompleteOptions.SEARCH_ONLY,
                      },
                      () => handleSubmit()
                    );
                  }}
                  primary
                  icon="checkmark"
                  content={i18next.t("Save")}
                />
              </Modal.Actions>
            </Modal>
          );
        }}
      </Formik>
    );
}

CreatibutorsModal.propTypes = {
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  action: PropTypes.oneOf(["add", "edit"]).isRequired,
  addLabel: PropTypes.string.isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  editLabel: PropTypes.string.isRequired,
  initialCreatibutor: PropTypes.shape({
    id: PropTypes.string,
    person_or_org: PropTypes.shape({
      family_name: PropTypes.string,
      given_name: PropTypes.string,
      name: PropTypes.string,
      type: PropTypes.string,
      identifiers: PropTypes.arrayOf(
        PropTypes.shape({
          scheme: PropTypes.string,
          identifier: PropTypes.string,
        })
      ),
    }),
    affiliations: PropTypes.array,
    role: PropTypes.string,
  }),
  trigger: PropTypes.object.isRequired,
  onCreatibutorChange: PropTypes.func.isRequired,
  roleOptions: PropTypes.array,
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
};

