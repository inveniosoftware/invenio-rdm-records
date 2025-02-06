// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
// Copyright (C) 2024 KTH Royal Institute of Technology.
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
  Pagination,
  ReactSearchKit,
  ResultsLoader,
  Toggle,
} from "react-searchkit";
import { Button, Container, Form, Grid, Menu, Modal } from "semantic-ui-react";
import * as Yup from "yup";
import { LicenseFilter } from "./LicenseFilter";
import { LicenseResults } from "./LicenseResults";
import { LicenseSearchBar } from "./LicenseSearchBar";
import { NoLicenseResults } from "./NoLicenseResults";

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
    mode: ModalTypes.STANDARD,
  };

  openModal = () => {
    this.setState({ open: true });
  };

  closeModal = () => {
    this.setState({ open: false });
  };

  setMode = (mode) => {
    this.setState({ mode: mode });
  };

  onSubmit = (values, formikBag) => {
    // We have to close the modal first because onLicenseChange and passing
    // license as an object makes React get rid of this component. Otherwise
    // we get a memory leak warning.
    const { onLicenseChange } = this.props;
    this.closeModal();
    this.setMode(this.mode);
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
    const modeState = this.state.mode;

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
            role="dialog"
            centered={false}
            onOpen={() => {
              this.openModal();
              this.setMode(mode);
            }}
            open={open}
            trigger={React.cloneElement(trigger, {
              "aria-expanded": open,
              "aria-haspopup": "dialog",
            })}
            onClose={() => {
              resetForm();
              this.setMode(ModalTypes.STANDARD);
              this.closeModal();
            }}
            closeIcon
            closeOnDimmerClick={false}
          >
            <Modal.Header as="h2" className="pt-10 pb-10">
              {action === ModalActions.ADD
                ? i18next.t(`Add {{mode}} license`, {
                    mode: modeState,
                  })
                : i18next.t(`Change {{mode}} license`, {
                    mode: modeState,
                  })}
            </Modal.Header>
            <Modal.Content>
              {modeState === ModalTypes.STANDARD && (
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
                            placeholder={i18next.t("Search for licenses")}
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
                              label={i18next.t("recommended")}
                              filterValue={["tags", "recommended"]}
                            />
                            <Toggle
                              title={i18next.t("All")}
                              label={i18next.t("all")}
                              filterValue={["tags", "all"]}
                            />
                            <Toggle
                              title={i18next.t("Data")}
                              label={i18next.t("data")}
                              filterValue={["tags", "data"]}
                            />
                            <Toggle
                              title={i18next.t("Software")}
                              label={i18next.t("software")}
                              filterValue={["tags", "software"]}
                            />
                          </Menu>
                        </Grid.Column>
                      </Grid.Row>
                      <Grid.Row verticalAlign="middle">
                        <Grid.Column width={16} className="pb-0">
                          <ResultsLoader>
                            <EmptyResults />
                            <Error />
                            <LicenseResults
                              {...(serializeLicenses && {
                                serializeLicenses,
                              })}
                            />
                          </ResultsLoader>
                          <Container textAlign="center" className="rel-mb-1">
                            <Pagination />
                          </Container>
                        </Grid.Column>
                        <Grid.Column
                          width={16}
                          textAlign="center"
                          className="pt-0 pb-0"
                        >
                          <NoLicenseResults
                            switchToCustom={() => {
                              resetForm();
                              this.setMode(ModalTypes.CUSTOM);
                            }}
                          />
                        </Grid.Column>
                      </Grid.Row>
                    </Grid>
                  </ReactSearchKit>
                </OverridableContext.Provider>
              )}
              {modeState === ModalTypes.CUSTOM && (
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
                  this.setMode(mode);
                  this.closeModal();
                }}
                icon="remove"
                content={i18next.t("Cancel")}
                floated="left"
              />
              <Button
                name="submit"
                onClick={(event) => handleSubmit(event)}
                primary
                icon="checkmark"
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
