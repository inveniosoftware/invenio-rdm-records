// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2022 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { Component } from "react";
import { connect } from "react-redux";
import { connect as connectFormik } from "formik";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "../../api/DepositFormSubmitContext";
import { DRAFT_PREVIEW_STARTED } from "../../state/types";
import { Button } from "semantic-ui-react";
import _omit from "lodash/omit";
import PropTypes from "prop-types";

export class PreviewButtonComponent extends Component {
  static contextType = DepositFormSubmitContext;

  handlePreview = (event, handleSubmit) => {
    const { setSubmitContext } = this.context;

    setSubmitContext(DepositFormSubmitActions.PREVIEW);
    handleSubmit(event);
  };

  render() {
    const { actionState, formik, ...ui } = this.props;
    const { handleSubmit, isSubmitting } = formik;

    const uiProps = _omit(ui, ["dispatch"]);

    return (
      <Button
        name="preview"
        disabled={isSubmitting}
        onClick={(e) => this.handlePreview(e, handleSubmit)}
        loading={isSubmitting && actionState === DRAFT_PREVIEW_STARTED}
        icon="eye"
        labelPosition="left"
        content={i18next.t("Preview")}
        {...uiProps}
      />
    );
  }
}

PreviewButtonComponent.propTypes = {
  actionState: PropTypes.string,
  formik: PropTypes.object.isRequired,
};

PreviewButtonComponent.defaultProps = {
  actionState: undefined,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  record: state.deposit.record,
});

export const PreviewButton = connect(
  mapStateToProps,
  null
)(connectFormik(PreviewButtonComponent));
