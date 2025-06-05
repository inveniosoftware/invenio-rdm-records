// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import _isEmpty from "lodash/isEmpty";
import React, { Component } from "react";
import { Label } from "semantic-ui-react";
import PropTypes from "prop-types";

export class FormFeedbackSummary extends Component {
  constructor(props) {
    super(props);
    this.sections = {
      ...props.sectionsConfig,
    };
    this.state = {
      domReady: false,
    };
  }

  componentDidMount() {
    // XXX: This is a workaround to ensure that the component is mounted before we try
    // to access the DOM elements. DO NOT use this pattern in new components, this will
    // be properly fixed in https://github.com/inveniosoftware/invenio-rdm-records/issues/2072
    setTimeout(() => {
      this.setState({ domReady: true });
    }, 0);
  }

  getAllErrPaths = (obj, prev = "") => {
    const result = [];

    for (let k in obj) {
      let path = prev + (prev ? "." : "") + k;

      // find leaf path of errors
      if (typeof obj[k] == "string" || obj[k].severity !== undefined) {
        result.push(path);
      } else if (typeof obj[k] == "object") {
        result.push(...this.getAllErrPaths(obj[k], path));
      }
    }

    return result;
  };

  getErrorSections(errors) {
    const errorSections = new Map();

    // Iterate over each error path in the errors object
    const paths = this.getAllErrPaths(errors);

    paths.forEach((path) => {
      let sectionElement = undefined;
      // Try to match error to a section based on field paths
      for (const [section, fields] of Object.entries(this.sections)) {
        if (fields.some((field) => path.startsWith(field))) {
          const sectionElement = document.getElementById(section);
          const label = sectionElement?.getAttribute("label") || "Unknown section";
          errorSections.set(section, {
            label,
            count: (errorSections.get(section)?.count || 0) + 1,
          });
          return;
        }
      }

      // If not matched in predefined sections, check dynamically in accordions
      // this part is used for custom widgets
      // and ensures backwards compatibility for the sections with no config provided
      const sectionElements = document.querySelectorAll(".invenio-accordion-field");

      // select section which contains the field
      // name in the field is always present, it is a must in forms
      sectionElement = Array.from(sectionElements).find((section) =>
        section.querySelector(`[name="${path}"]`)
      );

      if (sectionElement) {
        const sectionId = sectionElement.id;
        const label = sectionElement.getAttribute("label") || "Unknown section";
        errorSections.set(sectionId, {
          label,
          count: (errorSections.get(sectionId)?.count || 0) + 1,
        });
      }
    });

    // Order sections based on their DOM appearance and return error links
    const accordions = Array.from(document.querySelectorAll(".accordion")).map(
      (accordion) => accordion.id
    );

    const orderedSections = [
      ...accordions.filter((id) => errorSections.has(id)), // Keep sections that exist in order
      ...[...errorSections.keys()].filter((id) => !accordions.includes(id)), // Append missing sections
    ];
    return { orderedSections: orderedSections, errorSections: errorSections };
  }

  render() {
    const { errors } = this.props;
    const { domReady } = this.state;
    const { orderedSections, errorSections } = domReady
      ? this.getErrorSections(errors)
      : [];
    if (_isEmpty(orderedSections)) {
      return null;
    }

    return orderedSections.map((section, i) => {
      const { label, count } = errorSections.get(section);
      return (
        <a key={section} className="pl-5 comma-separated" href={`#${section}`}>
          {label}{" "}
          <Label circular size="tiny">
            {count}
          </Label>
        </a>
      );
    });
  }
}

FormFeedbackSummary.propTypes = {
  sectionsConfig: PropTypes.object.isRequired,
  errors: PropTypes.object.isRequired,
};
