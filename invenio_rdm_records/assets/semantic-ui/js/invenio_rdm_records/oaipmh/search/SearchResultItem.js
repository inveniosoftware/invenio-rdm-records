/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import PropTypes from "prop-types";
import React, { Component } from "react";
import _get from "lodash/get";
import { Table } from "semantic-ui-react";
import isEmpty from "lodash/isEmpty";
import { withState } from "react-searchkit";
import { Actions } from "@js/invenio_administration";
import { AdminUIRoutes } from "@js/invenio_administration";
import { OverridableContext } from "react-overridable";
import { DeleteModal } from "./DeleteModal";
import Formatter from "@js/invenio_administration/src/components/Formatter";
import { i18next } from "@translations/invenio_app_rdm/i18next";

const overridenComponents = {
  "DeleteModal.layout": DeleteModal,
};

class SearchResultItemComponent extends Component {
  refreshAfterAction = () => {
    const { updateQueryState, currentQueryState } = this.props;
    updateQueryState(currentQueryState);
  };

  createdBySystem = () => {
    const { result } = this.props;
    return result.system_created;
  };

  displayAsPre = (result, property) => {
    const { resourceSchema } = this.props;
    if (property === "spec") {
      return (
        <pre>
          <Formatter
            result={result}
            resourceSchema={resourceSchema}
            property={property}
          />
        </pre>
      );
    } else {
      return (
        <Formatter
          result={result}
          resourceSchema={resourceSchema}
          property={property}
        />
      );
    }
  };

  render() {
    const {
      title,
      resourceName,
      result,
      columns,
      displayEdit,
      displayDelete,
      actions,
      apiEndpoint,
      idKeyPath,
      listUIEndpoint,
    } = this.props;

    const resourceHasActions =
      displayEdit || displayDelete || !isEmpty(actions);
    return (
      <OverridableContext.Provider value={overridenComponents}>
        <Table.Row>
          {columns.map(([property, { text, order }], index) => {
            return (
              <Table.Cell
                key={`${text}-${order}`}
                data-label={text}
                className="word-break-all"
              >
                {index === 0 ? (
                  <a
                    href={AdminUIRoutes.detailsView(
                      listUIEndpoint,
                      result,
                      idKeyPath
                    )}
                  >
                    {this.displayAsPre(result, property)}
                  </a>
                ) : (
                  this.displayAsPre(result, property)
                )}
              </Table.Cell>
            );
          })}
          {resourceHasActions && (
            <Table.Cell>
              <Actions
                title={title}
                resourceName={resourceName}
                apiEndpoint={apiEndpoint}
                editAction={{
                  display: displayEdit,
                  disabled: this.createdBySystem(),
                  disabledMessage: i18next.t(
                    "This set is not editable as it was created by the system."
                  ),
                }}
                deleteAction={{
                  display: displayDelete,
                  disabled: this.createdBySystem(),
                  disabledMessage: i18next.t(
                    "This set is not deletable as it was created by the system."
                  ),
                }}
                actions={actions}
                resource={result}
                idKeyPath={idKeyPath}
                successCallback={this.refreshAfterAction}
                listUIEndpoint={listUIEndpoint}
              />
            </Table.Cell>
          )}
        </Table.Row>
      </OverridableContext.Provider>
    );
  }
}

SearchResultItemComponent.propTypes = {
  title: PropTypes.string.isRequired,
  resourceName: PropTypes.string.isRequired,
  result: PropTypes.object.isRequired,
  columns: PropTypes.array.isRequired,
  displayDelete: PropTypes.bool,
  displayEdit: PropTypes.bool,
  actions: PropTypes.object,
  apiEndpoint: PropTypes.string,
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  idKeyPath: PropTypes.string.isRequired,
  listUIEndpoint: PropTypes.string.isRequired,
  resourceSchema: PropTypes.object.isRequired,
};

SearchResultItemComponent.defaultProps = {
  displayDelete: true,
  displayEdit: true,
  apiEndpoint: undefined,
  actions: {},
};

export const SearchResultItem = withState(SearchResultItemComponent);
