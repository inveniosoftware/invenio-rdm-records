// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

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
