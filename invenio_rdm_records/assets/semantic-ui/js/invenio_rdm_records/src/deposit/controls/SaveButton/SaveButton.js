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

export class SaveButtonComponent extends Component {
  static contextType = DepositFormSubmitContext;

  handleSave = (event) => {
    const { formik } = this.props;
    const { setSubmitContext } = this.context;
    const { handleSubmit } = formik;

    setSubmitContext(DepositFormSubmitActions.SAVE);
    handleSubmit(event);
    scrollTop();
  };

  render() {
    const { actionState, formik, ...ui } = this.props;
    const { isSubmitting } = formik;

    const uiProps = _omit(ui, ["dispatch"]);

    return (
      <Button
        name="save"
        disabled={isSubmitting}
        onClick={(event) => this.handleSave(event)}
        icon="save"
        loading={isSubmitting && actionState === DRAFT_SAVE_STARTED}
        labelPosition="left"
        content={i18next.t("Save draft")}
        {...uiProps}
      />
    );
  }
}

SaveButtonComponent.propTypes = {
  formik: PropTypes.object.isRequired,
  actionState: PropTypes.string,
};

SaveButtonComponent.defaultProps = {
  actionState: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
});

export const SaveButton = connect(
  mapStateToProps,
  null
)(connectFormik(SaveButtonComponent));
