/*
 * SPDX-FileCopyrightText: 2020-2024 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Component } from "react";
import Overridable, { OverridableContext, parametrize } from "react-overridable";
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
import { Grid, Menu, Modal } from "semantic-ui-react";
import { CommunityListItem } from "./CommunityListItem";
import PropTypes from "prop-types";

const communitySelectionSearchDefaultPropApiConfigs = {
    allCommunities: {
      initialQueryState: { size: 5, page: 1, sortBy: "bestmatch" },
      searchApi: {
        axios: {
          url: "/api/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.AllCommunities",
      toggleText: i18next.t("Search in all communities"),
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
      toggleText: i18next.t("Search in my communities"),
    },
  };
export function CommunitySelectionSearch({apiConfigs = communitySelectionSearchDefaultPropApiConfigs, myCommunities, record = null, isInitialSubmission = true, CommunityListItem = CommunityListItem, pagination = true, myCommunitiesEnabled = true, autofocus = true, overriddenComponents = undefined}) {
  const [selectedConfig, setSelectedConfig] = React.useState(allCommunities);
  const [searchApi, setSearchApi] = React.useState(null);
  const [appId, setAppId] = React.useState(null);
  const [initialQueryState, setInitialQueryState] = React.useState(null);

  const searchApi = new InvenioSearchApi(selectedSearchApi);
    const overriddenComponents = {
      [`${selectedAppId}.ResultsList.item`]: parametrize(CommunityListItem, {
        record,
        isInitialSubmission,
      }),
      ...extraOverriddenComponents,
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
              <Overridable
                id="InvenioRdmRecords.CommunityHeader.CommunitySelectionSearch.TabMenu.Container"
                allCommunities={allCommunities}
                myCommunities={myCommunities}
                selectedAppId={selectedAppId}
                onSelectConfig={(config) => setSelectedConfig(config)}
                myCommunitiesEnabled={myCommunitiesEnabled}
              >
                {myCommunitiesEnabled && (
                  <Grid.Column
                    mobile={16}
                    tablet={8}
                    computer={8}
                    textAlign="left"
                    floated="left"
                    className="pt-0 pl-0"
                  >
                    <Menu role="tablist" className="theme-primary-menu" compact>
                      <Menu.Item
                        as="button"
                        role="tab"
                        id="all-communities-tab"
                        aria-selected={selectedAppId === allCommunities.appId}
                        aria-controls={allCommunities.appId}
                        name="All"
                        active={selectedAppId === allCommunities.appId}
                        onClick={() =>
                          setSelectedConfig(allCommunities)
                        }
                      >
                        {i18next.t("All")}
                      </Menu.Item>
                      <Menu.Item
                        as="button"
                        role="tab"
                        id="my-communities-tab"
                        aria-selected={selectedAppId === myCommunities.appId}
                        aria-controls={myCommunities.appId}
                        name="My communities"
                        active={selectedAppId === myCommunities.appId}
                        onClick={() =>
                          setSelectedConfig(myCommunities)
                        }
                      >
                        {i18next.t("My communities")}
                      </Menu.Item>
                    </Menu>
                  </Grid.Column>
                )}
              </Overridable>
              <Grid.Column
                mobile={16}
                tablet={8}
                computer={8}
                floated={myCommunitiesEnabled ? "right" : "null"}
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
  record: PropTypes.object,
  isInitialSubmission: PropTypes.bool,
  CommunityListItem: PropTypes.elementType,
  pagination: PropTypes.bool,
  myCommunitiesEnabled: PropTypes.bool,
  autofocus: PropTypes.bool,
  overriddenComponents: PropTypes.object,
};

