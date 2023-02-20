/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Table } from "semantic-ui-react";
import isEmpty from "lodash/isEmpty";
import { withState } from "react-searchkit";
import { Actions } from "@js/invenio_administration";
import { AdminUIRoutes } from "@js/invenio_administration";
import Formatter from "@js/invenio_administration/src/components/Formatter";


class SearchResultItemComponent extends Component {
  refreshAfterAction = () => {
    const { updateQueryState, currentQueryState } = this.props;
    updateQueryState(currentQueryState);
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
      appName
    } = this.props;

    const resourceHasActions =
      displayEdit || displayDelete || !isEmpty(actions);


    return (
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
              actions={actions}
              editUrl={AdminUIRoutes.editView(
                listUIEndpoint,
                result,
                idKeyPath
              )}
              displayEdit={displayEdit}
              displayDelete={displayDelete}
              resource={result}
              idKeyPath={idKeyPath}
              successCallback={this.refreshAfterAction}
              listUIEndpoint={listUIEndpoint}
              appName={appName}
            />
          </Table.Cell>
        )}
      </Table.Row>
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
  appName: PropTypes.string,
};

SearchResultItemComponent.defaultProps = {
  displayDelete: true,
  displayEdit: true,
  apiEndpoint: undefined,
  actions: {},
  appName: "",
};

export const SearchResultItem = withState(SearchResultItemComponent);
