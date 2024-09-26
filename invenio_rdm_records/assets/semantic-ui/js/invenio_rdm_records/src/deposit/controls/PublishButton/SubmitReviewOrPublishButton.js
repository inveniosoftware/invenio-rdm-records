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
            publishWithoutCommunity
            {...ui}
          />
        </>
      );
    } else {
      result = <PublishButton {...ui} />;
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
});

export const SubmitReviewOrPublishButton = connect(
  mapStateToProps,
  mapDispatchToProps
)(SubmitReviewOrPublishComponent);
