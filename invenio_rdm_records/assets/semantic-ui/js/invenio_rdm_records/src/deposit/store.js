// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _cloneDeep from "lodash/cloneDeep";
import _get from "lodash/get";
import { applyMiddleware, compose, createStore } from "redux";
import thunk from "redux-thunk";
import rootReducer from "./state/reducers";
import { computeDepositState } from "./state/reducers/deposit";
import { UploadState } from "./state/reducers/files";

const preloadFiles = (files) => {
  const _files = _cloneDeep(files);
  return {
    links: files.links || {},
    entries: _get(_files, "entries", [])
      .map((file) => {
        let hasSize = file.size >= 0;
        const fileState = {
          name: file.key,
          size: file.size || 0,
          checksum: file.checksum || "",
          links: file.links || {},
        };
        // TODO: fix this as the lack of size is not always an error e.g upload ongoing in another tab
        return hasSize
          ? {
              status: UploadState.finished,
              progressPercentage: 100,
              ...fileState,
            }
          : { status: UploadState.pending, ...fileState };
      })
      .reduce((acc, current) => {
        acc[current.name] = { ...current };
        return acc;
      }, {}),
  };
};

export function configureStore(appConfig) {
  const { record, preselectedCommunity, files, config, permissions, ...extra } =
    appConfig;

  // when not passed, make sure that the value is `undefined` and not `null`
  const _preselectedCommunity = preselectedCommunity || undefined;

  const initialDepositState = {
    record,
    editorState: computeDepositState(record, _preselectedCommunity),
    config,
    permissions,
    actionState: null,
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
