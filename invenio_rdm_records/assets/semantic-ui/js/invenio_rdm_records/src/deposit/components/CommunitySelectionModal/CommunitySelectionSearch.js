// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { Component } from "react";
import { OverridableContext } from "react-overridable";
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
import { Container, Grid, Menu, Modal, Segment } from "semantic-ui-react";
import { CommunityListItem } from "./CommunityListItem";
import PropTypes from "prop-types";

export class CommunitySelectionSearch extends Component {
  constructor(props) {
    super(props);
    const {
      apiConfigs: { allCommunities },
    } = this.props;

    const defaultConfig = allCommunities;

    this.state = {
      selectedConfig: defaultConfig,
    };
  }

  render() {
    const {
      selectedConfig: {
        searchApi: selectedsearchApi,
        appId: selectedAppId,
        initialQueryState: selectedInitialQueryState,
        toggleText,
      },
    } = this.state;
    const {
      apiConfigs: { allCommunities, myCommunities },
    } = this.props;
    const searchApi = new InvenioSearchApi(selectedsearchApi);
    const overriddenComponents = {
      [`${selectedAppId}.ResultsList.item`]: CommunityListItem,
    };
    return (
      <OverridableContext.Provider value={overriddenComponents}>
        <ReactSearchKit
          appName={selectedAppId}
          urlHandlerApi={{ enabled: false }}
          searchApi={searchApi}
          key={selectedAppId}
          initialQueryState={selectedInitialQueryState}
        >
          <Grid>
            <Grid.Row verticalAlign="middle">
              <Grid.Column width={8} textAlign="left" floated="left">
                <Menu compact>
                  <Menu.Item
                    name="All"
                    active={selectedAppId === allCommunities.appId}
                    onClick={() =>
                      this.setState({
                        selectedConfig: allCommunities,
                      })
                    }
                  >
                    {i18next.t("All")}
                  </Menu.Item>
                  <Menu.Item
                    name="My communities"
                    active={selectedAppId === myCommunities.appId}
                    onClick={() =>
                      this.setState({
                        selectedConfig: myCommunities,
                      })
                    }
                  >
                    {i18next.t("My communities")}
                  </Menu.Item>
                </Menu>
              </Grid.Column>
              <Grid.Column width={8} floated="right" verticalAlign="middle">
                <SearchBar
                  placeholder={toggleText}
                  autofocus
                  actionProps={{
                    icon: "search",
                    content: null,
                    className: "search",
                  }}
                />
              </Grid.Column>
            </Grid.Row>

            <Grid.Row verticalAlign="middle">
              <Grid.Column>
                <ResultsLoader>
                  <Segment className="community-list-container p-0">
                    <Modal.Content scrolling className="community-list-results">
                      <EmptyResults />
                      <Error />
                      <ResultsList />
                    </Modal.Content>
                  </Segment>
                  <Container textAlign="center">
                    <Pagination />
                  </Container>
                </ResultsLoader>
              </Grid.Column>
            </Grid.Row>
          </Grid>
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
};

CommunitySelectionSearch.defaultProps = {
  apiConfigs: {
    allCommunities: {
      initialQueryState: { size: 5, page: 1 },
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
      initialQueryState: { size: 5, page: 1 },
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
