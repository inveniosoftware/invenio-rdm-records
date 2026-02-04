// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2024 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { Component } from "react";
import { OverridableContext, parametrize } from "react-overridable";
import {
  EmptyResults,
  Error,
  InvenioSearchApi,
  Pagination,
  ReactSearchKit,
  ResultsList,
  ResultsLoader,
  SearchBar,
} from "react-searchkit";
import { Grid, Modal } from "semantic-ui-react";
import { CommunityListItem } from "./CommunityListItem";
import PropTypes from "prop-types";
import { CommunitiesStatusFilter } from "@js/invenio_communities/community";

export class CommunitySelectionSearch extends Component {
  constructor(props) {
    super(props);
    const {
      apiConfigs: { allCommunities },
    } = this.props;

    this.state = {
      selectedConfig: allCommunities,
    };
  }

  render() {
    const {
      selectedConfig: {
        searchApi: selectedSearchApi,
        appId: selectedAppId,
        initialQueryState: selectedInitialQueryState,
        toggleText,
      },
    } = this.state;

    const {
      apiConfigs: { allCommunities, myCommunities },
      record,
      isInitialSubmission,
      CommunityListItem,
      pagination,
      communitiesStatusFilterEnabled,
      autofocus,
    } = this.props;

    const searchApi = new InvenioSearchApi(selectedSearchApi);
    const overriddenComponents = {
      [`${selectedAppId}.ResultsList.item`]: parametrize(CommunityListItem, {
        record: record,
        isInitialSubmission: isInitialSubmission,
      }),
    };

    return (
      <OverridableContext.Provider value={overriddenComponents}>
        <ReactSearchKit
          appName={selectedAppId}
          urlHandlerApi={{ enabled: false }}
          searchApi={searchApi}
          key={selectedAppId}
          initialQueryState={selectedInitialQueryState}
          defaultSortingOnEmptyQueryString={{ sortBy: "bestmatch" }}
        >
          <>
            <Modal.Content as={Grid} className="m-0 pb-0 centered">
              {communitiesStatusFilterEnabled && (
                <Grid.Column
                  mobile={16}
                  tablet={8}
                  computer={8}
                  textAlign="left"
                  floated="left"
                  className="pt-0 pl-0"
                >
                  <CommunitiesStatusFilter
                    myCommunitiesOnClick={() => {
                      this.setState({
                        selectedConfig: myCommunities,
                      });
                    }}
                    allCommunitiesOnClick={() => {
                      this.setState({
                        selectedConfig: allCommunities,
                      });
                    }}
                    appId={selectedAppId}
                    allCommunitiesSelected={selectedAppId === allCommunities.appId}
                  />
                </Grid.Column>
              )}
              <Grid.Column
                mobile={16}
                tablet={8}
                computer={8}
                floated={communitiesStatusFilterEnabled ? "right" : "null"}
                verticalAlign="middle"
                className="pt-0 pr-0 pl-0"
              >
                <SearchBar
                  placeholder={toggleText}
                  autofocus={autofocus}
                  actionProps={{
                    "icon": "search",
                    "content": null,
                    "className": "search",
                    "aria-label": i18next.t("Search"),
                  }}
                />
              </Grid.Column>
            </Modal.Content>

            <Modal.Content
              role="tabpanel"
              id={selectedAppId}
              scrolling
              className="community-list-results"
            >
              <ResultsLoader>
                <EmptyResults />
                <Error />
                <ResultsList />
              </ResultsLoader>
            </Modal.Content>

            {pagination && (
              <Modal.Content className="text-align-center">
                <Pagination />
              </Modal.Content>
            )}
          </>
        </ReactSearchKit>
      </OverridableContext.Provider>
    );
  }
}

CommunitySelectionSearch.propTypes = {
  apiConfigs: PropTypes.shape({
    allCommunities: PropTypes.shape({
      appId: PropTypes.string.isRequired,
      initialQueryState: PropTypes.object.isRequired,
      searchApi: PropTypes.object.isRequired,
    }),
    myCommunities: PropTypes.shape({
      appId: PropTypes.string.isRequired,
      initialQueryState: PropTypes.object.isRequired,
      searchApi: PropTypes.object.isRequired,
    }),
  }),
  record: PropTypes.object.isRequired,
  isInitialSubmission: PropTypes.bool,
  CommunityListItem: PropTypes.elementType,
  pagination: PropTypes.bool,
  communitiesStatusFilterEnabled: PropTypes.bool,
  autofocus: PropTypes.bool,
};

CommunitySelectionSearch.defaultProps = {
  isInitialSubmission: true,
  pagination: true,
  communitiesStatusFilterEnabled: true,
  autofocus: true,
  CommunityListItem: CommunityListItem,
  apiConfigs: {
    allCommunities: {
      initialQueryState: { size: 5, page: 1, sortBy: "bestmatch" },
      searchApi: {
        axios: {
          url: "/api/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.AllCommunities",
      toggleText: "Search in all communities",
    },
    myCommunities: {
      initialQueryState: { size: 5, page: 1, sortBy: "bestmatch" },
      searchApi: {
        axios: {
          url: "/api/user/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.MyCommunities",
      toggleText: "Search in my communities",
    },
  },
};
