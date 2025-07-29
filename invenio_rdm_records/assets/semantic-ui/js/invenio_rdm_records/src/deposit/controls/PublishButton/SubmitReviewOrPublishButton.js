// This file is part of Invenio-RDM-Records
// Copyright (C) 2022-2023 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { connect } from "react-redux";
import { Button } from "semantic-ui-react";
import { changeSelectedCommunity } from "../../state/actions";
import { CommunitySelectionModal } from "../../components/CommunitySelectionModal";
import { PublishButton } from "./PublishButton";
import { SubmitReviewButton } from "./SubmitReviewButton";

class SubmitReviewOrPublishComponent extends Component {
  constructor(props) {
    super(props);
    this.state = {
      modalOpen: false,
    };
  }

  doiReservationCheck = (
    isDOIRequired,
    noINeedDOI,
    formik,
    errorMessage,
    errorType
  ) => {
    // Check for explicit DOI reservation via the "GET DOI button" only when DOI is
    // optional in the instance's settings. If it is required, backend will automatically
    // mint one even if it was not explicitly reserved
    const shouldCheckForExplicitDOIReservation =
      isDOIRequired !== undefined && // isDOIRequired is undefined when no value was provided from Invenio-app-rdm
      !isDOIRequired &&
      noINeedDOI &&
      Object.keys(formik?.values?.pids).length === 0;
    if (shouldCheckForExplicitDOIReservation) {
      const errors = {
        pids: {
          doi: i18next.t(errorMessage),
        },
      };
      formik.setErrors(errors);
      const { raiseDOINeededButNotReserved } = this.props;
      raiseDOINeededButNotReserved(formik?.values, errors, errorType);
    }
    return shouldCheckForExplicitDOIReservation;
  };

  render() {
    const {
      community,
      changeSelectedCommunityFn,
      showChangeCommunityButton,
      showDirectPublishButton,
      showSubmitForReviewButton,
      record,
      ...ui
    } = this.props;
    const { modalOpen } = this.state;
    let result;

    if (showSubmitForReviewButton) {
      result = (
        <SubmitReviewButton
          directPublish={showDirectPublishButton}
          {...ui}
          fluid
          className="mb-10"
          record={record}
          doiReservationCheck={this.doiReservationCheck}
        />
      );
    } else if (showChangeCommunityButton) {
      result = (
        <>
          <CommunitySelectionModal
            onCommunityChange={(community) => {
              changeSelectedCommunityFn(community);
            }}
            onModalChange={(value) => this.setState({ modalOpen: value })}
            modalOpen={modalOpen}
            displaySelected
            record={record}
            chosenCommunity={community}
            trigger={
              <Button content={i18next.t("Change community")} fluid className="mb-10" />
            }
          />
          <PublishButton
            buttonLabel={i18next.t("Publish without community")}
            doiReservationCheck={this.doiReservationCheck}
            publishWithoutCommunity
            {...ui}
          />
        </>
      );
    } else {
      result = <PublishButton doiReservationCheck={this.doiReservationCheck} {...ui} />;
    }
    return result;
  }
}

SubmitReviewOrPublishComponent.propTypes = {
  community: PropTypes.object,
  changeSelectedCommunityFn: PropTypes.func.isRequired,
  showChangeCommunityButton: PropTypes.bool.isRequired,
  showDirectPublishButton: PropTypes.bool.isRequired,
  showSubmitForReviewButton: PropTypes.bool.isRequired,
  record: PropTypes.object.isRequired,
  raiseDOINeededButNotReserved: PropTypes.func.isRequired,
};

SubmitReviewOrPublishComponent.defaultProps = {
  community: undefined,
};

const mapStateToProps = (state) => ({
  community: state.deposit.editorState.selectedCommunity,
  showDirectPublishButton: state.deposit.editorState.ui.showDirectPublishButton,
  showChangeCommunityButton: state.deposit.editorState.ui.showChangeCommunityButton,
  showSubmitForReviewButton: state.deposit.editorState.ui.showSubmitForReviewButton,
});

const mapDispatchToProps = (dispatch) => ({
  changeSelectedCommunityFn: (community) =>
    dispatch(changeSelectedCommunity(community)),
  raiseDOINeededButNotReserved: (data, errors, errorType) =>
    dispatch({
      type: errorType,
      payload: { data: data, errors: errors },
    }),
});

export const SubmitReviewOrPublishButton = connect(
  mapStateToProps,
  mapDispatchToProps
)(SubmitReviewOrPublishComponent);
