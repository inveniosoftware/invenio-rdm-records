import PropTypes from "prop-types";
import React from "react";
import Overridable from "react-overridable";

export const fieldCommonProps = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  hidden: PropTypes.bool,
  disabled: PropTypes.bool,
  required: PropTypes.bool,
};

export const createFieldComponent = (id, Child) => {
  const Component = ({ hidden, ...props }) => {
    if (hidden) return null;
    return <Child {...props} />;
  };

  Component.propTypes = {
    ...fieldCommonProps,
  };

  return Overridable.component(id, Component);
};
