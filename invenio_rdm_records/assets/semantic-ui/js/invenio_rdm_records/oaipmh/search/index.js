// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { initDefaultSearchComponents, Edit, Delete, DeleteModalTrigger } from "@js/invenio_administration";
import { createSearchAppInit } from "@js/invenio_search_ui";
import { SearchResultItem } from "./SearchResultItem";
import { parametrize, overrideStore } from "react-overridable";
import _get from "lodash/get";
import { NotificationController } from "@js/invenio_administration";
import { DeleteModal } from "./DeleteModal";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Popup, Button, Icon } from "semantic-ui-react";

const domContainer = document.getElementById("invenio-search-config");

const appName = "InvenioRdmRecords.AdministrationOaipmhListView";

const sortColumns = (columns) =>
  Object.entries(columns).sort((a, b) => a[1].order - b[1].order);
const title = JSON.parse(domContainer.dataset.title);
const resourceName = JSON.parse(domContainer.dataset.resourceName);
const columns = JSON.parse(domContainer.dataset.fields);
const sortedColumns = sortColumns(columns);
const displayEdit = JSON.parse(domContainer.dataset.displayEdit);
const displayDelete = JSON.parse(domContainer.dataset.displayDelete);
const displayRead = JSON.parse(domContainer.dataset.displayRead);
const actions = JSON.parse(domContainer.dataset.actions);
const apiEndpoint = _get(domContainer.dataset, "apiEndpoint");
const idKeyPath = JSON.parse(_get(domContainer.dataset, "pidPath", "pid"));
const listUIEndpoint = domContainer.dataset.listEndpoint;
const resourceSchema = JSON.parse(domContainer.dataset.resourceSchema);

const defaultComponents = initDefaultSearchComponents(domContainer, appName);
const SearchResultItemWithConfig = parametrize(SearchResultItem, {
  title: title,
  resourceName: resourceName,
  columns: sortedColumns,
  displayRead: displayRead,
  displayEdit: displayEdit,
  displayDelete: displayDelete,
  actions: actions,
  apiEndpoint: apiEndpoint,
  idKeyPath: idKeyPath,
  listUIEndpoint: listUIEndpoint,
  resourceSchema: resourceSchema,
  appName: appName,
});

const createdBySystem = (data) => data?.system_created;


// const EditSet = parametrize(
//   Edit,
//   {
//     disable: createdBySystem,
//     disabledMessage: i18next.t(
//       "This set is not editable as it was created by the system."
//     ),
//     // appName: appName,
//   }
// );

const EditSet = (props) => {
  const { display, editUrl, disabled, resource, appName } = props;
  const disabledMessage = i18next.t(
    "This set is not editable as it was created by the system."
  )
  return (
    <Popup
      content={disabledMessage}
      disabled={!createdBySystem(resource)}
      trigger={
        <span className="mr-5">
          <Button
            as="a"
            disabled={createdBySystem(resource)}
            href={editUrl}
            icon
            labelPosition="left"
          >
            <Icon name="pencil" />
            {i18next.t("Edit")}
          </Button>
        </span>
      }
    />
  )
}

// const DeleteSet = parametrize(
//   Delete,
//   {
//     disable: createdBySystem,
//     disabledMessage: i18next.t(
//       "This set is not deletable as it was created by the system."
//     ),
//     appName: appName,
//   }
// );

const DeleteSet = (props) => {
  const {
    disable,
    title,
    resourceName,
    successCallback,
    idKeyPath,
    resource,
    appName
  } = props
  const disabledMessage = i18next.t(
    "This set is not deletable as it was created by the system."
  )
  return (
    <Popup
      content={disabledMessage}
      disabled={!disable}
      trigger={
        <span>
          <DeleteModalTrigger
            title={title}
            resourceName={resourceName}
            resource={resource}
            successCallback={successCallback}
            idKeyPath={idKeyPath}
            disabled={createdBySystem(resource)}
            apiEndpoint={_get(resource, "links.self")}
            disabledDeleteMessage={disabledMessage}
            appName={appName}
          />
        </span>
      }
    />
  )

}


const overriddenDefaultComponents = {
  ...defaultComponents,
  [`${appName}.ResultsList.item`]: SearchResultItemWithConfig,
  [`${appName}.EditAction.layout`]: EditSet,
  [`${appName}.DeleteAction.layout`]: DeleteSet,
  [`${appName}.DeleteModal.layout`]: DeleteModal,
};

const overriddenComponents = overrideStore.getAll();

createSearchAppInit(
  { ...overriddenDefaultComponents, ...overriddenComponents },
  true,
  "invenio-search-config",
  true,
  NotificationController
);
