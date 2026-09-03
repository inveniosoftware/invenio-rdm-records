/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React from "react";
import { connect } from "react-redux";
import { connect as connectFormik } from "formik";
import { Button, Modal } from "semantic-ui-react";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "../../api/DepositFormSubmitContext";
import { DRAFT_DELETE_STARTED } from "../../state/types";
import _omit from "lodash/omit";
import _capitalize from "lodash/capitalize";
import PropTypes from "prop-types";

// action
const DISCARD_CHANGES_LBL = i18next.t("discard changes");
const DISCARD_VERSION_LBL = i18next.t("discard version");
const DELETE_LBL = i18next.t("delete");

// action messages
const DISCARD_CHANGES_DLG = i18next.t(
  "Are you sure you want to discard the changes to this draft?"
);

const DISCARD_VERSION_DLG = i18next.t(
  "Are you sure you want to delete this new version?"
);
const DISCARD_DELETE_DLG = i18next.t("Are you sure you want to delete this draft?");

const DialogText = ({ actionLbl }) => {
  let text = "";
  switch (actionLbl) {
    case DISCARD_CHANGES_LBL:
      text = DISCARD_CHANGES_DLG;
      break;
    case DISCARD_VERSION_LBL:
      text = DISCARD_VERSION_DLG;
      break;
    case DELETE_LBL:
      text = DISCARD_DELETE_DLG;
      break;
    default:
      break;
  }
  return text;
};

export function DeleteButtonComponent({
  isPublished = false,
  isVersion = false,
  formik,
  draftExists = false,
  actionState = undefined,
  ...ui
}) {
  const { setSubmitContext } = React.useContext(DepositFormSubmitContext);
  const [modalOpen, setModalOpen] = React.useState(false);

  const openConfirmModal = () => setModalOpen(true);

  const closeConfirmModal = () => setModalOpen(false);

  const handleDelete = (event) => {
    const { handleSubmit } = formik;

    setSubmitContext(DepositFormSubmitActions.DELETE, {
      isDiscardingVersion: isPublished || isVersion,
    });
    handleSubmit(event);
    closeConfirmModal();
  };

  const { isSubmitting } = formik;

  const uiProps = _omit(ui, ["dispatch"]);

  let actionLbl = "";
  if (!isPublished) {
    actionLbl = isVersion ? DISCARD_VERSION_LBL : DELETE_LBL;
  } else {
    actionLbl = DISCARD_CHANGES_LBL;
  }
  const color = isPublished ? "warning" : "negative";
  const icon = isPublished ? "close" : "trash alternate outline";
  const capitalizedActionLbl = _capitalize(actionLbl);

  return (
    <>
      <Button
        disabled={!draftExists || isSubmitting}
        onClick={openConfirmModal}
        className={color}
        icon={icon}
        loading={isSubmitting && actionState === DRAFT_DELETE_STARTED}
        labelPosition="left"
        {...uiProps}
        content={capitalizedActionLbl}
      />

      <Modal open={modalOpen} onClose={closeConfirmModal} size="tiny">
        <Modal.Content>
          <DialogText actionLbl={actionLbl} />
        </Modal.Content>
        <Modal.Actions>
          <Button onClick={closeConfirmModal} floated="left">
            {i18next.t("Cancel")}
          </Button>
          <Button
            className={color}
            onClick={handleDelete}
            loading={isSubmitting && actionState === DRAFT_DELETE_STARTED}
            icon="trash alternate outline"
            content={capitalizedActionLbl}
          />
        </Modal.Actions>
      </Modal>
    </>
  );
}

DeleteButtonComponent.propTypes = {
  draftExists: PropTypes.bool,
  isPublished: PropTypes.bool,
  isVersion: PropTypes.bool,
  actionState: PropTypes.string,
  formik: PropTypes.object.isRequired,
};

const mapStateToProps = (state) => ({
  draftExists: Boolean(state.deposit.record.id),
  isPublished: state.deposit.record.is_published,
  isVersion: state.deposit.record.versions?.index > 1,
  actionState: state.deposit.actionState,
});

export const DeleteButton = connect(
  mapStateToProps,
  null
)(connectFormik(DeleteButtonComponent));
