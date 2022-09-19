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
import { Actions } from "@js/invenio_administration/src/actions/Actions.js";
import { AdminUIRoutes } from "@js/invenio_administration/src/routes.js";
import { OverridableContext } from "react-overridable";
import { DeleteModal } from "./DeleteModal";

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
              <Table.Cell key={`${text}-${order}`} data-label={text}>
                {index === 0 ? (
                  <a
                    href={AdminUIRoutes.detailsView(
                      listUIEndpoint,
                      result,
                      idKeyPath
                    )}
                  >
                    {_get(result, property)}
                  </a>
                ) : (
                  _get(result, property)
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
                displayEdit={displayEdit}
                disableEdit={this.createdBySystem()}
                displayDelete={displayDelete}
                disableDelete={this.createdBySystem()}
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
};

SearchResultItemComponent.defaultProps = {
  displayDelete: true,
  displayEdit: true,
  apiEndpoint: undefined,
  actions: {},
};

export const SearchResultItem = withState(SearchResultItemComponent);
