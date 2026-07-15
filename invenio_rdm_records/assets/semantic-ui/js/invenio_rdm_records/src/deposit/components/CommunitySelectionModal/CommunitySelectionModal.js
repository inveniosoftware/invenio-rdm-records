/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import { cloneElement, Component } from "react";
import { connect } from "react-redux";
import { Header, Modal, Button } from "semantic-ui-react";
import { CommunityContext } from "./CommunityContext";
import { CommunitySelectionSearch } from "./CommunitySelectionSearch";
import _isEmpty from "lodash/isEmpty";

export function CommunitySelectionModalComponent({chosenCommunity = undefined, userCommunitiesMemberships, displaySelected = false, onCommunityChange, trigger = undefined, modalOpen = false, onModalChange = undefined, extraContentComponents = undefined, modalHeader = i18next.t("Select a community"), apiConfigs = undefined, handleClose, record = null, isInitialSubmission = true, overriddenComponents = undefined}) {
  const [localChosenCommunity, setLocalChosenCommunity] = React.useState(chosenCommunity);

  const getChosenCommunity = () => {
    const { localChosenCommunity } = this.state;
    return localChosenCommunity;
  };

  const setCommunity = (community) => {
    const { onCommunityChange } = this.props;
    onCommunityChange(community);
    setLocalChosenCommunity(community);
  };

  const modalTrigger = () => {
    const { trigger, modalOpen } = this.props;
    if (!_isEmpty(trigger)) {
      return cloneElement(trigger, {
        "aria-haspopup": "dialog",
        "aria-expanded": modalOpen,
      });
    }
  };

  const handleModalOpen = () => {
    const { chosenCommunity, onModalChange } = this.props;
    setLocalChosenCommunity(chosenCommunity);
    onModalChange && onModalChange(true);
  };

  return (
      <CommunityContext.Provider value={contextValue}>
        <Modal
          role="dialog"
          aria-labelledby="community-modal-header"
          id="community-selection-modal"
          className="m-0"
          closeIcon
          closeOnDimmerClick={false}
          open={modalOpen}
          onClose={() => {
            onModalChange && onModalChange(false);
          }}
          onOpen={handleModalOpen}
          trigger={modalTrigger()}
        >
          <Modal.Header>
            <Header as="h2" size="small" id="community-modal-header" className="mt-5">
              {modalHeader}
            </Header>
          </Modal.Header>

          <CommunitySelectionSearch
            apiConfigs={apiConfigs}
            record={record}
            isInitialSubmission={isInitialSubmission}
            overriddenComponents={overriddenComponents}
          />

          {extraContentComponents && (
            <Modal.Content>{extraContentComponents}</Modal.Content>
          )}

          <Modal.Actions>
            <Button onClick={handleClose}>{i18next.t("Close")}</Button>
          </Modal.Actions>
        </Modal>
      </CommunityContext.Provider>
    );
}

CommunitySelectionModalComponent.propTypes = {
  chosenCommunity: PropTypes.object,
  onCommunityChange: PropTypes.func.isRequired,
  trigger: PropTypes.object,
  userCommunitiesMemberships: PropTypes.object,
  extraContentComponents: PropTypes.node,
  modalHeader: PropTypes.string,
  onModalChange: PropTypes.func,
  displaySelected: PropTypes.bool,
  modalOpen: PropTypes.bool,
  apiConfigs: PropTypes.object,
  handleClose: PropTypes.func.isRequired,
  record: PropTypes.object,
  isInitialSubmission: PropTypes.bool,
  overriddenComponents: PropTypes.object,
};

const mapStateToProps = (state) => ({
  userCommunitiesMemberships: state.deposit.config.user_communities_memberships,
});

export const CommunitySelectionModal = connect(
  mapStateToProps,
  null
)(CommunitySelectionModalComponent);
