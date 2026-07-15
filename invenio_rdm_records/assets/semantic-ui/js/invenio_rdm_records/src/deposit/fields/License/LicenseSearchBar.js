/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-License-Identifier: MIT
 */

import { useState, Component } from "react";
import PropTypes from "prop-types";
import { withState } from "react-searchkit";
import { Input } from "semantic-ui-react";

export const LicenseSearchBarComponent = ({
  updateQueryState = null,
  currentQueryState = null,
  autofocus = false,
  actionProps = null,
  placeholder = "",
}) => {
  const [currentValue, setCurrentValue] = useState("");

  const onInputChange = (queryString) => {
    setCurrentValue(queryString);
  };

  const executeSearch = () => {
    currentQueryState["filters"][0] = ["tags", "all"];
    currentQueryState["queryString"] = currentValue;
    updateQueryState(currentQueryState);
  };

  const onKeyPress = (event) => {
    if (event.key === "Enter") {
      executeSearch();
    }
  };

  return (
    <Element
      actionProps={actionProps}
      autofocus={autofocus}
      executeSearch={executeSearch}
      onBtnSearchClick={executeSearch}
      onInputChange={onInputChange}
      onKeyPress={onKeyPress}
      placeholder={placeholder}
      queryString={currentValue}
    />
  );
};

LicenseSearchBarComponent.propTypes = {
  actionProps: PropTypes.object,
  autofocus: PropTypes.bool,
  currentQueryState: PropTypes.object,
  updateQueryState: PropTypes.func,
  placeholder: PropTypes.string,
};

function Element({autofocus = false, actionProps = null, onBtnSearchClick = null, onInputChange = null, onKeyPress = null, placeholder = "", queryString = ""}) {
  React.useEffect(() => {
    if (autofocus && focusInput) {
      focusInput.focus();
    }
  }, []);

  return (
      <Input
        action={{
          content: "Search",
          onClick: onBtnSearchClick,
          ...actionProps,
        }}
        fluid
        placeholder={placeholder || "Type something"}
        onChange={(_, { value }) => {
          onInputChange(value);
        }}
        value={queryString}
        onKeyPress={onKeyPress}
        ref={(input) => {
          focusInput = input;
        }}
      />
    );
}

Element.propTypes = {
  actionProps: PropTypes.object,
  autofocus: PropTypes.bool,
  onBtnSearchClick: PropTypes.func,
  onInputChange: PropTypes.func,
  onKeyPress: PropTypes.func,
  placeholder: PropTypes.string,
  queryString: PropTypes.string,
};

export const LicenseSearchBar = withState(LicenseSearchBarComponent);
