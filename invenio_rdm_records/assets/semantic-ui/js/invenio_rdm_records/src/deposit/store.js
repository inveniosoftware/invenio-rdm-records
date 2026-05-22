/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import _cloneDeep from "lodash/cloneDeep";
import _get from "lodash/get";
import { applyMiddleware, compose, createStore } from "redux";
import thunk from "redux-thunk";
import rootReducer from "./state/reducers";
import { computeDepositState } from "./state/reducers/deposit";
import { UploadState } from "./state/reducers/files";
import { DRAFT_LOADED_WITH_VALIDATION_ERRORS } from "./state/types";

const preloadFiles = (files) => {
  const _files = _cloneDeep(files);
  return {
    links: files.links || {},
    entries: _get(_files, "entries", [])
      .map((file) => {
        const fileState = {
          file_id: file.file_id,
          name: file.key,
          size: file.size || 0,
          checksum: file.checksum || "",
          links: file.links || {},
          mimetype: file.mimetype || "application/octet-stream",
          status: UploadState[file.status],
        };

        return {
          progressPercentage: fileState.status === UploadState.completed ? 100 : 0,
          ...fileState,
        };
      })
      .reduce((acc, current) => {
        acc[current.name] = { ...current };
        return acc;
      }, {}),
  };
};

export function configureStore(appConfig) {
  const { record, errors, preselectedCommunity, files, config, permissions, ...extra } =
    appConfig;

  // when not passed, make sure that the value is `undefined` and not `null`
  const _preselectedCommunity = preselectedCommunity || undefined;
  const initialDepositState = {
    record,
    errors: errors || {},
    editorState: computeDepositState(record, _preselectedCommunity),
    config,
    permissions,
    actionState: errors ? DRAFT_LOADED_WITH_VALIDATION_ERRORS : null,
    actionStateExtra: {},
  };

  const preloadedState = {
    deposit: initialDepositState,
    files: preloadFiles(files || {}),
  };

  const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;
  return createStore(
    rootReducer,
    preloadedState,
    composeEnhancers(applyMiddleware(thunk.withExtraArgument({ config, ...extra })))
  );
}
