// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, Component } from "react";
import PropTypes from "prop-types";
import { withState } from "react-searchkit";
import { Input } from "semantic-ui-react";

export const LicenseSearchBarComponent = ({
  updateQueryState,
  currentQueryState,
  autofocus,
  actionProps,
  placeholder,
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

LicenseSearchBarComponent.defaultProps = {
  actionProps: null,
  autofocus: false,
  placeholder: "",
  currentQueryState: null,
  updateQueryState: null,
};

class Element extends Component {
  componentDidMount() {
    const { autofocus } = this.props;
    if (autofocus && this.focusInput) {
      this.focusInput.focus();
    }
  }

  render() {
    const {
      actionProps,
      onBtnSearchClick,
      onInputChange,
      onKeyPress,
      placeholder,
      queryString,
    } = this.props;

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
          this.focusInput = input;
        }}
      />
    );
  }
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

Element.defaultProps = {
  actionProps: null,
  autofocus: false,
  onBtnSearchClick: null,
  onInputChange: null,
  onKeyPress: null,
  placeholder: "",
  queryString: "",
};

export const LicenseSearchBar = withState(LicenseSearchBarComponent);
