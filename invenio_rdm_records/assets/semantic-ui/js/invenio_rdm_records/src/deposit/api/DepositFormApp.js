/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import { Component } from "react";
import { I18nextProvider } from "react-i18next";
import { Provider } from "react-redux";
import {
  DepositApiClient,
  DepositFileApiClient,
  RDMDepositApiClient,
  RDMDepositFileApiClient,
} from "./DepositApiClient";
import { DepositBootstrap } from "./DepositBootstrap";
import { DepositDraftsService, RDMDepositDraftsService } from "./DepositDraftsService";
import { DepositFilesService, RDMDepositFilesService } from "./DepositFilesService";
import {
  DepositRecordSerializer,
  RDMDepositRecordSerializer,
} from "./DepositRecordSerializer";
import { DepositService } from "./DepositService";
import { configureStore } from "../store";
import { RDMUploadProgressNotifier } from "../components/UploadProgressNotifier";

export function DepositFormApp({recordSerializer = undefined, config, apiClient = undefined, fileApiClient = undefined, draftsService = undefined, filesService = undefined, record, preselectedCommunity = undefined, files = undefined, permissions = undefined, errors = undefined, children = undefined}) {
  return (
      <Provider store={store}>
        <I18nextProvider i18n={i18next}>
          <DepositBootstrap>{children}</DepositBootstrap>
        </I18nextProvider>
      </Provider>
    );
}

DepositFormApp.propTypes = {
  config: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
  errors: PropTypes.arrayOf(
    PropTypes.shape({
      field: PropTypes.string.isRequired,
      messages: PropTypes.arrayOf(PropTypes.string).isRequired,
      description: PropTypes.string,
      severity: PropTypes.string,
    })
  ),
  preselectedCommunity: PropTypes.object,
  files: PropTypes.object,
  permissions: PropTypes.object,
  apiClient: PropTypes.instanceOf(DepositApiClient),
  fileApiClient: PropTypes.instanceOf(DepositFileApiClient),
  draftsService: PropTypes.instanceOf(DepositDraftsService),
  filesService: PropTypes.instanceOf(DepositFilesService),
  recordSerializer: PropTypes.instanceOf(DepositRecordSerializer),
  children: PropTypes.node,
};

