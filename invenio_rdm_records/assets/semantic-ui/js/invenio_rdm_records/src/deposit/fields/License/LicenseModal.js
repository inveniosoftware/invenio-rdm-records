// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { TextAreaField, TextField } from "react-invenio-forms";
import { OverridableContext } from "react-overridable";
import {
  EmptyResults,
  Error,
  InvenioSearchApi,
  ReactSearchKit,
  ResultsLoader,
  Toggle,
} from "react-searchkit";
import { Button, Form, Grid, Menu, Modal } from "semantic-ui-react";
import * as Yup from "yup";
import { LicenseFilter } from "./LicenseFilter";
import { LicenseResults } from "./LicenseResults";
import { LicenseSearchBar } from "./LicenseSearchBar";

const overriddenComponents = {
  "SearchFilters.Toggle": LicenseFilter,
};

const ModalTypes = {
  STANDARD: "standard",
  CUSTOM: "custom",
};

const ModalActions = {
  ADD: "add",
  EDIT: "edit",
};

const LicenseSchema = Yup.object().shape({
  selectedLicense: Yup.object().shape({
    title: Yup.string().required(i18next.t("Title is a required field.")),
    link: Yup.string().url(i18next.t("Link must be a valid URL")),
  }),
});

export class LicenseModal extends Component {
  state = {
    open: false,
  };

  openModal = () => {
    this.setState({ open: true });
  };

  closeModal = () => {
    this.setState({ open: false });
  };

  onSubmit = (values, formikBag) => {
    // We have to close the modal first because onLicenseChange and passing
    // license as an object makes React get rid of this component. Otherwise
    // we get a memory leak warning.
    const { onLicenseChange } = this.props;
    this.closeModal();
    onLicenseChange(values.selectedLicense);
    formikBag.resetForm();
  };

  render() {
    const {
      mode,
      trigger,
      action,
      searchConfig,
      serializeLicenses,
      initialLicense: initialLicenseProp,
    } = this.props;
    const { open } = this.state;

    const initialLicense = initialLicenseProp || {
      title: "",
      description: "",
      id: null,
      link: "",
    };

    const searchApi = new InvenioSearchApi(searchConfig.searchApi);
    return (
      <Formik
        initialValues={{
          selectedLicense: initialLicense,
        }}
        onSubmit={this.onSubmit}
        validationSchema={LicenseSchema}
        validateOnChange={false}
        validateOnBlur={false}
      >
        {({ handleSubmit, resetForm }) => (
          <Modal
            onOpen={() => this.openModal()}
            open={open}
            trigger={trigger}
            onClose={() => {
              this.closeModal();
              resetForm();
            }}
            closeIcon
            closeOnDimmerClick={false}
          >
            <Modal.Header as="h2" className="pt-10 pb-10">
              {action === ModalActions.ADD
                ? i18next.t(`Add {{mode}} license`, {
                    mode: mode,
                  })
                : i18next.t(`Change {{mode}} license`, {
                    mode: mode,
                  })}
            </Modal.Header>
            <Modal.Content scrolling>
              {mode === ModalTypes.STANDARD && (
                <OverridableContext.Provider value={overriddenComponents}>
                  <ReactSearchKit
                    searchApi={searchApi}
                    appName="licenses"
                    urlHandlerApi={{ enabled: false }}
                    initialQueryState={searchConfig.initialQueryState}
                  >
                    <Grid>
                      <Grid.Row>
                        <Grid.Column width={8} floated="left" verticalAlign="middle">
                          <LicenseSearchBar
                            placeholder={i18next.t("Search")}
                            autofocus
                            actionProps={{
                              icon: "search",
                              content: null,
                              className: "search",
                            }}
                          />
                        </Grid.Column>
                        <Grid.Column width={8} textAlign="right" floated="right">
                          <Menu compact>
                            <Toggle
                              title={i18next.t("Recommended")}
                              label="recommended"
                              filterValue={["tags", "recommended"]}
                            />
                            <Toggle
                              title={i18next.t("All")}
                              label="all"
                              filterValue={["tags", "all"]}
                            />
                            <Toggle
                              title={i18next.t("Data")}
                              label="data"
                              filterValue={["tags", "data"]}
                            />
                            <Toggle
                              title={i18next.t("Software")}
                              label="software"
                              filterValue={["tags", "software"]}
                            />
                          </Menu>
                        </Grid.Column>
                      </Grid.Row>
                      <Grid.Row verticalAlign="middle">
                        <Grid.Column>
                          <ResultsLoader>
                            <EmptyResults />
                            <Error />
                            <LicenseResults
                              {...(serializeLicenses && {
                                serializeLicenses,
                              })}
                            />
                          </ResultsLoader>
                        </Grid.Column>
                      </Grid.Row>
                    </Grid>
                  </ReactSearchKit>
                </OverridableContext.Provider>
              )}
              {mode === ModalTypes.CUSTOM && (
                <Form>
                  <TextField
                    label={i18next.t("Title")}
                    placeholder={i18next.t("License title")}
                    fieldPath="selectedLicense.title"
                    required
                    // eslint-disable-next-line
                    autoFocus
                  />
                  <TextAreaField
                    fieldPath="selectedLicense.description"
                    label={i18next.t("Description")}
                  />
                  <TextField
                    label={i18next.t("Link")}
                    placeholder={i18next.t("License link")}
                    fieldPath="selectedLicense.link"
                  />
                </Form>
              )}
            </Modal.Content>
            <Modal.Actions>
              <Button
                name="cancel"
                onClick={() => {
                  resetForm();
                  this.closeModal();
                }}
                icon="remove"
                labelPosition="left"
                content={i18next.t("Cancel")}
                floated="left"
              />
              <Button
                name="submit"
                onClick={(event) => handleSubmit(event)}
                primary
                icon="checkmark"
                labelPosition="left"
                content={
                  action === ModalActions.ADD
                    ? i18next.t("Add license")
                    : i18next.t("Change license")
                }
              />
            </Modal.Actions>
          </Modal>
        )}
      </Formik>
    );
  }
}

LicenseModal.propTypes = {
  mode: PropTypes.oneOf(["standard", "custom"]).isRequired,
  action: PropTypes.oneOf(["add", "edit"]).isRequired,
  initialLicense: PropTypes.shape({
    id: PropTypes.string,
    title: PropTypes.string,
    description: PropTypes.string,
  }),
  trigger: PropTypes.object.isRequired,
  onLicenseChange: PropTypes.func.isRequired,
  searchConfig: PropTypes.shape({
    searchApi: PropTypes.shape({
      axios: PropTypes.shape({
        headers: PropTypes.object,
      }),
    }).isRequired,
    initialQueryState: PropTypes.shape({
      filters: PropTypes.arrayOf(PropTypes.array),
    }).isRequired,
  }).isRequired,
  serializeLicenses: PropTypes.func,
};

LicenseModal.defaultProps = {
  initialLicense: undefined,
  serializeLicenses: undefined,
};
