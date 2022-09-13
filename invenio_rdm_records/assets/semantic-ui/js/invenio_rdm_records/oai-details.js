// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import ReactDOM from "react-dom";
import _get from "lodash/get";
import LinksTable from "./LinksTable";
import AdminDetailsView from "@js/invenio_administration/details/AdminDetailsView.js";

const mainDomContainer = document.getElementById("invenio-details-config");
const fields = JSON.parse(mainDomContainer.dataset.fields);
const apiEndpoint = _get(mainDomContainer.dataset, "apiEndpoint");
const pidValue = JSON.parse(mainDomContainer.dataset.pid);
const title = mainDomContainer.dataset.title;
const actions = JSON.parse(mainDomContainer.dataset.actions);
const displayEdit = JSON.parse(mainDomContainer.dataset.displayEdit);
const displayDelete = JSON.parse(mainDomContainer.dataset.displayDelete);


mainDomContainer &&
  ReactDOM.render(
      <AdminDetailsView
        title={title}
        actions={actions}
        apiEndpoint={apiEndpoint}
        columns={fields}
        displayDelete={displayDelete}
        displayEdit={displayEdit}
        pid={pidValue}
      >
        <LinksTable />
      </AdminDetailsView>
    ,mainDomContainer
  );


