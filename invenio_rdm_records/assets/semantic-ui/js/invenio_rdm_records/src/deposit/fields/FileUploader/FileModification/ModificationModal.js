// This file is part of InvenioRDM
// Copyright (C) 2025 CERN
//
// Invenio-rdm-records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Formik } from "formik";
import PropTypes from "prop-types";
import React, { Component } from "react";
import Overridable from "react-overridable";

import { ErrorMessage, http, withCancel } from "react-invenio-forms";
import {
  Button,
  Checkbox,
  Form,
  Message,
  Modal,
  ModalActions,
  ModalContent,
  ModalHeader,
  Table,
  TableBody,
  TableHeader,
  TableHeaderCell,
  TableRow,
} from "semantic-ui-react";
import RadioGroup from "./RadioGroup";

export class ModificationModal extends Component {
  constructor(props) {
    super(props);
    this.initState = {
      loading: false,
      error: undefined,
      checklistState: [undefined],
      checkboxState: [false],
      messages: [],
    };
    this.state = { ...this.initState };
    this.checklist = [
      {
        label: i18next.t("I want to update the files with a new version"),
        message: i18next.t("Instead, you can make a new version"),
      },
    ];
  }

  handleClose = () => {
    this.setState({
      ...this.initState,
    });
    const { handleClose } = this.props;
    handleClose();
  };

  handleRadioUpdate = (index, value) => {
    const { checklistState } = this.state;
    const nextChecklistState = checklistState.map((c, i) => {
      if (i === index) {
        return value;
      } else {
        return c;
      }
    });
    const filteredChecklist = this.checklist.filter((_, index) => {
      return nextChecklistState[index];
    });
    const newMessages = filteredChecklist.map((x) => x["message"]);
    this.setState({ checklistState: nextChecklistState, messages: newMessages });
  };

  handleCheckboxUpdate = (index) => {
    const { checkboxState } = this.state;
    const nextCheckboxState = checkboxState.map((c, i) => {
      if (i === index) {
        return !checkboxState[i];
      } else {
        return c;
      }
    });
    this.setState({ checkboxState: nextCheckboxState });
  };

  handleSubmit = async (values) => {
    this.setState({ loading: true });
    const { record } = this.props;
    const payload = {
      reason: values.reason,
      comment: values.comment,
    };
    if ("file_modification" in record.links) {
      this.cancellableAction = withCancel(
        http.post(record.links.file_modification, payload)
      );
      try {
        const response = await this.cancellableAction.promise;
        const data = response.data;

        if (response.status === 200) {
          window.location.reload();
        } else if (response.status === 201) {
          window.location.href = data.links.self_html;
        }
      } catch (error) {
        this.setState({ error: error });
        console.error(error);
      } finally {
        this.setState({ loading: false });
      }
    } else {
      this.setState({
        error: "Could not submit file modification request",
        loading: false,
      });
    }
  };

  render() {
    const { open, fileModification } = this.props;
    const { loading, error, messages, checklistState, checkboxState } = this.state;

    const formDisabled =
      checkboxState.some((v) => v === false) ||
      checklistState.some((x) => x === true || x === undefined);

    if (!fileModification.fileModification?.allowed) {
      return (
        <Modal
          open={open}
          closeIcon
          onClose={this.handleClose}
          role="dialog"
          aria-modal="true"
          tab-index="-1"
          size="tiny"
          closeOnDimmerClick={false}
          onClick={(e) => e.stopPropagation()} // prevent interaction with dropdown
          onKeyDown={(e) => e.stopPropagation()} // prevent interaction with dropdown
        >
          <ModalHeader>{i18next.t("Edit files")}</ModalHeader>
          <Overridable id="InvenioAppRdm.Deposit.ModificationModal.message">
            <ModalContent>
              <p>
                {i18next.t(
                  "Please contact us to request file modification, including the" +
                    " record URL and a detailed justification in your message."
                )}
              </p>
            </ModalContent>
          </Overridable>
          <ModalActions className="text-align-left">
            <Button onClick={this.handleClose} content={i18next.t("Close")} />
          </ModalActions>
        </Modal>
      );
    }

    return (
      <Modal
        open={open}
        closeIcon
        onClose={this.handleClose}
        role="dialog"
        aria-modal="true"
        tab-index="-1"
        size="tiny"
        closeOnDimmerClick={false}
        onClick={(e) => e.stopPropagation()} // prevent interaction with dropdown
        onKeyDown={(e) => e.stopPropagation()} // prevent interaction with dropdown
      >
        <ModalHeader>{i18next.t("Edit files")}</ModalHeader>
        <Formik
          onSubmit={this.handleSubmit}
          initialValues={{ reason: "", comment: "" }}
          validateOnChange={false}
          validateOnBlur={false}
        >
          {({ handleSubmit }) => (
            <Form>
              <ModalContent>
                <p>{fileModification.fileModification?.policy?.description}</p>
                {this.checklist.length > 0 && (
                  <>
                    <strong>{i18next.t("File modification checklist:")}</strong>
                    <Table basic="very" unstackable className="mt-0">
                      <TableHeader>
                        <TableRow>
                          <TableHeaderCell />
                          <TableHeaderCell>{i18next.t("Yes")}</TableHeaderCell>
                          <TableHeaderCell>{i18next.t("No")}</TableHeaderCell>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {this.checklist.map((row, index) => (
                          <RadioGroup
                            index={index}
                            row={row}
                            key={index}
                            state={checklistState}
                            onStateChange={this.handleRadioUpdate}
                          />
                        ))}
                      </TableBody>
                    </Table>
                    {messages.length > 0 && (
                      <Message info>
                        {messages.length === 1 ? (
                          <p dangerouslySetInnerHTML={{ __html: messages[0] }} />
                        ) : (
                          <Message.List>
                            {messages.map((message) => (
                              <Message.Item key={message}>
                                <p dangerouslySetInnerHTML={{ __html: message }} />
                              </Message.Item>
                            ))}
                          </Message.List>
                        )}
                      </Message>
                    )}
                  </>
                )}
                <Checkbox
                  label={
                    /* eslint-disable-next-line jsx-a11y/label-has-associated-control */
                    <label>
                      {i18next.t(
                        "I will not modify files that supplement findings/results of an already published work."
                      )}
                    </label>
                  }
                  className="mt-5 mb-5"
                  onChange={() => this.handleCheckboxUpdate(0)}
                />
                {error && (
                  <ErrorMessage
                    header={i18next.t("Unable to unlock files.")}
                    content={i18next.t(error)}
                    icon="exclamation"
                    className="text-align-left"
                    negative
                  />
                )}
              </ModalContent>
              <ModalActions>
                <Button
                  onClick={this.handleClose}
                  content={i18next.t("Close")}
                  floated="left"
                />
                <Button
                  content={i18next.t("Enable file editing")}
                  className="primary"
                  icon="lock open"
                  type="submit"
                  onClick={(event) => handleSubmit(event)}
                  loading={loading}
                  disabled={formDisabled || loading}
                />
              </ModalActions>
            </Form>
          )}
        </Formik>
      </Modal>
    );
  }
}

ModificationModal.propTypes = {
  record: PropTypes.object.isRequired,
  open: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  fileModification: PropTypes.object,
};

ModificationModal.defaultProps = {
  fileModification: {},
};
