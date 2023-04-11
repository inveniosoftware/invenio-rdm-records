// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import { Button, Menu } from "semantic-ui-react";

export const LicenseFilter = ({
  updateQueryFilters,
  userSelectionFilters,
  filterValue,
  label,
  title,
}) => {
  const _isChecked = (userSelectionFilters) => {
    const isFilterActive =
      userSelectionFilters.filter((filter) => filter[1] === filterValue[1]).length > 0;
    return isFilterActive;
  };

  const onToggleClicked = () => {
    updateQueryFilters(userSelectionFilters.concat([filterValue]));
  };

  const isChecked = _isChecked(userSelectionFilters);
  return isChecked ? (
    <Menu.Item name={label} active as={Button} primary onClick={onToggleClicked}>
      {title}
    </Menu.Item>
  ) : (
    <Menu.Item name={label} onClick={onToggleClicked}>
      {title}
    </Menu.Item>
  );
};

LicenseFilter.propTypes = {
  updateQueryFilters: PropTypes.func.isRequired,
  userSelectionFilters: PropTypes.array.isRequired,
  filterValue: PropTypes.array.isRequired,
  label: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
};
