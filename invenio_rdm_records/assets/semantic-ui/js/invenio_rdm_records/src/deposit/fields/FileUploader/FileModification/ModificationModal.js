/*
 * SPDX-FileCopyrightText: 2025-2026 CERN
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Formik } from "formik";
import PropTypes from "prop-types";
import { useMemo, useState } from "react";
import Overridable from "react-overridable";
import { save, hasValidationErrorsWithSeverityError } from "../../../state/actions";
import { connect } from "react-redux";

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

const initState = {
  loading: false,
  error: undefined,
  checklistState: [undefined],
  checkboxState: [false],
  messages: [],
};

function ModificationModalComponent({
  draft,
  record,
  open,
  handleClose,
  saveAction,
  fileModification = {},
}) {
  const [loading, setLoading] = useState(initState.loading);
  const [error, setError] = useState(initState.error);
  const [checklistState, setChecklistState] = useState(initState.checklistState);
  const [checkboxState, setCheckboxState] = useState(initState.checkboxState);
  const [messages, setMessages] = useState(initState.messages);

  const checklist = useMemo(
    () => [
      {
        label: i18next.t("I want to update the files with a new version"),
        message: i18next.t("Instead, you can make a new version"),
      },
    ],
    []
  );

  const onClose = () => {
    setLoading(initState.loading);
    setError(initState.error);
    setChecklistState(initState.checklistState);
    setCheckboxState(initState.checkboxState);
    setMessages(initState.messages);
    handleClose();
  };

  const handleRadioUpdate = (index, value) => {
    const nextChecklistState = checklistState.map((c, i) => {
      if (i === index) {
        return value;
      } else {
        return c;
      }
    });
    const filteredChecklist = checklist.filter((_, index) => {
      return nextChecklistState[index];
    });
    const newMessages = filteredChecklist.map((x) => x["message"]);
    setChecklistState(nextChecklistState);
    setMessages(newMessages);
  };

  const handleCheckboxUpdate = (index) => {
    const nextCheckboxState = checkboxState.map((c, i) => {
      if (i === index) {
        return !checkboxState[i];
      } else {
        return c;
      }
    });
    setCheckboxState(nextCheckboxState);
  };

  const onSubmit = async (values) => {
    setLoading(true);
    const payload = {
      reason: values.reason,
      comment: values.comment,
    };
    if (!("file_modification" in record.links)) {
      setError("Could not submit file modification request");
      setLoading(false);
      return;
    }

    // save draft before reloading the page
    try {
      await saveAction(draft, {});
    } catch (saveError) {
      // warnings don't block reload, but errors do
      if (hasValidationErrorsWithSeverityError(saveError?.errors)) {
        setLoading(false);
        setError(
          i18next.t(
            "Your record has validation errors that must be fixed before enabling file editing."
          )
        );
        return;
      }
    }

    try {
      const cancellableAction = withCancel(
        http.post(record.links.file_modification, payload)
      );
      const response = await cancellableAction.promise;
      const data = response.data;

      if (response.status === 200) {
        window.location.reload();
      } else if (response.status === 201) {
        window.location.href = data.links.self_html;
      }
    } catch (submitError) {
      setError(submitError);
      console.error(submitError);
    } finally {
      setLoading(false);
    }
  };

  // The submit button is enabled when:
  //  all the checkboxes are true and all the checklist boxes are false
  // by boolean logic: !(A && !B) === !A || B
  // note: radio buttons have three states including undefined
  const formDisabled =
    checkboxState.some((v) => v === false) ||
    checklistState.some((x) => x === true || x === undefined);

  if (!fileModification.fileModification?.allowed) {
    return (
      <Modal
        open={open}
        closeIcon
        onClose={onClose}
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
          <Button onClick={onClose} content={i18next.t("Close")} />
        </ModalActions>
      </Modal>
    );
  }

  return (
    <Modal
      open={open}
      closeIcon
      onClose={onClose}
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
        onSubmit={onSubmit}
        initialValues={{ reason: "", comment: "" }}
        validateOnChange={false}
        validateOnBlur={false}
      >
        {({ handleSubmit }) => (
          <Form>
            <ModalContent>
              <p>
                {fileModification.fileModification?.policy?.description}{" "}
                {i18next.t(
                  "Once unlocked you will have {{ daysUntil }} days to publish your changes.",
                  { daysUntil: fileModification.context.days_until }
                )}
              </p>
              {checklist.length > 0 && (
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
                      {checklist.map((row, index) => (
                        <RadioGroup
                          index={index}
                          row={row}
                          key={index}
                          state={checklistState}
                          onStateChange={handleRadioUpdate}
                        />
                      ))}
                    </TableBody>
                  </Table>
                  {messages.length > 0 && (
                    <Message info>
                      <p>{messages.join(" ")}</p>
                    </Message>
                  )}
                </>
              )}
              <Checkbox
                label={i18next.t(
                  "I will not modify files that supplement findings/results of an already published work."
                )}
                className="mt-5 mb-5"
                onChange={() => handleCheckboxUpdate(0)}
              />
              {error && (
                <ErrorMessage
                  header={i18next.t("Unable to unlock files")}
                  content={i18next.t(error)}
                  icon="exclamation"
                  className="text-align-left"
                  negative
                />
              )}
            </ModalContent>
            <ModalActions>
              <Button onClick={onClose} content={i18next.t("Close")} floated="left" />
              <Button
                content={i18next.t("Enable file editing")}
                className="primary"
                icon="lock open"
                type="submit"
                onClick={() => handleSubmit()}
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

ModificationModalComponent.propTypes = {
  draft: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
  open: PropTypes.bool.isRequired,
  handleClose: PropTypes.func.isRequired,
  fileModification: PropTypes.object,
  saveAction: PropTypes.func.isRequired,
};

const mapDispatchToProps = (dispatch) => ({
  saveAction: (values) => dispatch(save(values)),
});

export const ModificationModal = connect(
  null,
  mapDispatchToProps
)(ModificationModalComponent);
