/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import { useState } from "react";
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

export function DepositFormApp({
  recordSerializer: recordSerializerProp = undefined,
  config,
  apiClient: apiClientProp = undefined,
  fileApiClient: fileApiClientProp = undefined,
  draftsService: draftsServiceProp = undefined,
  filesService: filesServiceProp = undefined,
  record,
  preselectedCommunity = undefined,
  files = undefined,
  permissions = undefined,
  errors = undefined,
  children = undefined,
}) {
  const [store] = useState(() => {
    const recordSerializer =
      recordSerializerProp ||
      new RDMDepositRecordSerializer(
        config.default_locale,
        config.custom_fields.vocabularies
      );

    const additionalApiConfig = { headers: config.apiHeaders || null };

    const apiClient =
      apiClientProp ||
      new RDMDepositApiClient(additionalApiConfig, config.createUrl, recordSerializer);

    const fileApiClient =
      fileApiClientProp ||
      new RDMDepositFileApiClient(
        additionalApiConfig,
        config.default_transfer_type,
        config.enabled_transfer_types
      );

    const draftsService = draftsServiceProp || new RDMDepositDraftsService(apiClient);

    const filesService =
      filesServiceProp ||
      new RDMDepositFilesService(fileApiClient, config.fileUploadConcurrency);

    const service = new DepositService(draftsService, filesService);

    const appConfig = {
      config: config,
      record: recordSerializer.deserialize(record),
      preselectedCommunity: preselectedCommunity,
      files: files,
      apiClient: apiClient,
      fileApiClient: fileApiClient,
      service: service,
      permissions: permissions,
      recordSerializer: recordSerializer,
    };

    if (errors && errors.length > 0) {
      appConfig.errors = recordSerializer.deserializeErrors(errors);
    }

    const depositStore = configureStore(appConfig);

    filesService.setProgressNotifier(
      new RDMUploadProgressNotifier(depositStore.dispatch)
    );

    return depositStore;
  });

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
