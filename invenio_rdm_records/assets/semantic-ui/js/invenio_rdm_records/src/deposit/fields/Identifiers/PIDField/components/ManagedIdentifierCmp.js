/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import PropTypes from "prop-types";
import { useContext } from "react";
import { Form } from "semantic-ui-react";
import { connect } from "react-redux";
import { UnreservePIDBtn } from "./UnreservePIDBtn";
import { ReservePIDBtn } from "./ReservePIDBtn";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "../../../../api/DepositFormSubmitContext";
import { DISCARD_PID_STARTED, RESERVE_PID_STARTED } from "../../../../state/types";
import { getFieldErrors } from "./helpers";

/**
 * Render identifier field and reserve/unreserve
 * button components for managed PID.
 */
function ManagedIdentifierComponent({
  pidType,
  actionState = "",
  actionStateExtra = {},
  btnLabelDiscardPID,
  btnLabelGetPID,
  disabled = false,
  helpText = null,
  identifier,
  pidPlaceholder,
  form,
  fieldPath,
}) {
  const { setSubmitContext } = useContext(DepositFormSubmitContext);

  const handleReservePID = (event, formik) => {
    setSubmitContext(DepositFormSubmitActions.RESERVE_PID, {
      pidType: pidType,
    });
    formik.handleSubmit(event);
  };

  const handleDiscardPID = (event, formik) => {
    setSubmitContext(DepositFormSubmitActions.DISCARD_PID, {
      pidType: pidType,
    });
    formik.handleSubmit(event);
  };

  const hasIdentifier = identifier !== "";

  const ReserveBtn = (
    <ReservePIDBtn
      disabled={disabled || hasIdentifier}
      label={btnLabelGetPID}
      loading={
        actionState === RESERVE_PID_STARTED && actionStateExtra.pidType === pidType
      }
      handleReservePID={handleReservePID}
      fieldError={getFieldErrors(form, fieldPath)}
    />
  );

  const UnreserveBtn = (
    <UnreservePIDBtn
      disabled={disabled}
      label={btnLabelDiscardPID}
      handleDiscardPID={handleDiscardPID}
      loading={
        actionState === DISCARD_PID_STARTED && actionStateExtra.pidType === pidType
      }
      pidType={pidType}
    />
  );

  return (
    <>
      <Form.Group inline>
        {hasIdentifier ? (
          <Form.Field>
            <label>{identifier}</label>
          </Form.Field>
        ) : (
          <Form.Field width={4}>
            <Form.Input disabled value="" placeholder={pidPlaceholder} width={16} />
          </Form.Field>
        )}

        <Form.Field>{identifier ? UnreserveBtn : ReserveBtn}</Form.Field>
      </Form.Group>
      {helpText && <label className="helptext">{helpText}</label>}
    </>
  );
}

ManagedIdentifierComponent.propTypes = {
  btnLabelGetPID: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  helpText: PropTypes.string,
  identifier: PropTypes.string.isRequired,
  btnLabelDiscardPID: PropTypes.string.isRequired,
  pidPlaceholder: PropTypes.string.isRequired,
  pidType: PropTypes.string.isRequired,
  form: PropTypes.object.isRequired,
  fieldPath: PropTypes.string.isRequired,
  /* from Redux */
  actionState: PropTypes.string,
  actionStateExtra: PropTypes.object,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  actionStateExtra: state.deposit.actionStateExtra,
});

export const ManagedIdentifierCmp = connect(
  mapStateToProps,
  null
)(ManagedIdentifierComponent);
