/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Component } from "react";
import { connect } from "react-redux";
import { Button } from "semantic-ui-react";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "../../api/DepositFormSubmitContext";
import { DRAFT_SAVE_STARTED } from "../../state/types";
import { scrollTop } from "../../utils";
import _omit from "lodash/omit";
import { connect as connectFormik } from "formik";
import PropTypes from "prop-types";

export function SaveButtonComponent({formik, actionState = undefined, ...ui}) {
  const contextValue = React.useContext(DepositFormSubmitContext);

  const handleSave = (event) => {
    const { formik } = this.props;
    const { setSubmitContext } = this.context;
    const { handleSubmit } = formik;

    setSubmitContext(DepositFormSubmitActions.SAVE);
    handleSubmit(event);
    scrollTop();
  };

  const { isSubmitting } = formik;

    const uiProps = _omit(ui, ["dispatch"]);

    return (
      <Button
        name="save"
        disabled={isSubmitting}
        onClick={(event) => handleSave(event)}
        icon="save"
        loading={isSubmitting && actionState === DRAFT_SAVE_STARTED}
        labelPosition="left"
        content={i18next.t("Save draft")}
        {...uiProps}
      />
    );
}

SaveButtonComponent.propTypes = {
  formik: PropTypes.object.isRequired,
  actionState: PropTypes.string,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
});

export const SaveButton = connect(
  mapStateToProps,
  null
)(connectFormik(SaveButtonComponent));
