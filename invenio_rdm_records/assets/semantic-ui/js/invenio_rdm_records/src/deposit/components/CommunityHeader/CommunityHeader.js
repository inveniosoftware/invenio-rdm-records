/*
 * SPDX-FileCopyrightText: 2020-2024 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021-2022 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import { Component } from "react";
import { Image } from "react-invenio-forms";
import { connect } from "react-redux";
import { Button, Container } from "semantic-ui-react";
import { changeSelectedCommunity } from "../../state/actions";
import { CommunitySelectionModal } from "../CommunitySelectionModal";
import Overridable from "react-overridable";

function CommunityHeaderComponent({changeSelectedCommunity, community = undefined, imagePlaceholderLink, showCommunitySelectionButton, disableCommunitySelectionButton, userCanManageRecord, record, showCommunityHeader, apiConfigs = undefined, overriddenComponents = undefined}) {
  const [modalOpen, setModalOpen] = React.useState(false);

  // record is coming from the Jinja template and it is refreshed on page reload
    const isNewUpload = !record.id;
    // Check if the user can manage the record only if it is not a new upload
    const isCommunitySelectionDisabled =
      (!isNewUpload && !userCanManageRecord) || disableCommunitySelectionButton;

    return (
      showCommunityHeader && (
        <Container
          className="page-subheader-outer compact ml-0-mobile mr-0-mobile"
          fluid
        >
          <Container className="page-subheader">
            {community ? (
              <>
                <div className="page-subheader-element">
                  <Image
                    rounded
                    className="community-header-logo"
                    src={community.links?.logo || imagePlaceholderLink} // logo is undefined when new draft and no selection
                    fallbackSrc={imagePlaceholderLink}
                  />
                </div>
                <div className="page-subheader-element flex align-items-center">
                  {community.metadata.title}
                </div>
              </>
            ) : (
              <div className="page-subheader-element">
                {i18next.t(
                  "Select the community where you want to submit your record."
                )}
              </div>
            )}
            <div className="community-header-element flex align-items-center rel-ml-1">
              {showCommunitySelectionButton && (
                <Overridable id="InvenioRdmRecords.CommunityHeader.CommunityHeaderElement.Container">
                  <>
                    <CommunitySelectionModal
                      onCommunityChange={(community) => {
                        changeSelectedCommunity(community);
                        setModalOpen(false);
                      }}
                      onModalChange={(value) => setModalOpen(value)}
                      handleClose={() => setModalOpen(false)}
                      modalOpen={modalOpen}
                      chosenCommunity={community}
                      displaySelected
                      record={record}
                      apiConfigs={apiConfigs}
                      overriddenComponents={overriddenComponents}
                      trigger={
                        <Overridable id="InvenioRdmRecords.CommunityHeader.CommunitySelectionButton.Container">
                          <Button
                            className="community-header-button"
                            disabled={isCommunitySelectionDisabled}
                            onClick={() => setModalOpen(true)}
                            primary
                            size="mini"
                            name="setting"
                            type="button"
                            content={
                              community
                                ? i18next.t("Change")
                                : i18next.t("Select a community")
                            }
                          />
                        </Overridable>
                      }
                    />
                    <Overridable
                      id="InvenioRdmRecords.CommunityHeader.RemoveCommunityButton.Container"
                      community={community}
                    >
                      {community && (
                        <Button
                          basic
                          size="mini"
                          labelPosition="left"
                          className="community-header-button ml-5"
                          onClick={() => changeSelectedCommunity(null)}
                          content={i18next.t("Remove")}
                          icon="close"
                          disabled={isCommunitySelectionDisabled}
                        />
                      )}
                    </Overridable>
                  </>
                </Overridable>
              )}
            </div>
          </Container>
        </Container>
      )
    );
}

CommunityHeaderComponent.propTypes = {
  imagePlaceholderLink: PropTypes.string.isRequired,
  community: PropTypes.object,
  disableCommunitySelectionButton: PropTypes.bool.isRequired,
  showCommunitySelectionButton: PropTypes.bool.isRequired,
  showCommunityHeader: PropTypes.bool.isRequired,
  changeSelectedCommunity: PropTypes.func.isRequired,
  record: PropTypes.object.isRequired,
  userCanManageRecord: PropTypes.bool.isRequired,
  apiConfigs: PropTypes.object,
  overriddenComponents: PropTypes.object,
};

const mapStateToProps = (state) => ({
  community: state.deposit.editorState.selectedCommunity,
  disableCommunitySelectionButton:
    state.deposit.editorState.ui.disableCommunitySelectionButton,
  showCommunitySelectionButton:
    state.deposit.editorState.ui.showCommunitySelectionButton,
  showCommunityHeader: state.deposit.editorState.ui.showCommunityHeader,
  userCanManageRecord: state.deposit.permissions.can_manage,
});

const mapDispatchToProps = (dispatch) => ({
  changeSelectedCommunity: (community) => dispatch(changeSelectedCommunity(community)),
});

export const CommunityHeader = connect(
  mapStateToProps,
  mapDispatchToProps
)(CommunityHeaderComponent);
