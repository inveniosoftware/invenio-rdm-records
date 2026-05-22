/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import React from "react";
import { connect as reduxConnect } from "react-redux";

export function connect(Component) {
  // eslint-disable-next-line no-unused-vars,react/prop-types
  const WrappedComponent = ({ dispatch, ...props }) => {
    return <Component {...props} />;
  };
  const mapStateToProps = (state) => ({
    deposit: state.deposit,
  });

  return reduxConnect(mapStateToProps, null)(WrappedComponent);
}
