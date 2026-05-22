/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { combineReducers } from "redux";
import depositReducer from "./deposit";
import fileReducer from "./files";

export default combineReducers({
  deposit: depositReducer,
  files: fileReducer,
});
