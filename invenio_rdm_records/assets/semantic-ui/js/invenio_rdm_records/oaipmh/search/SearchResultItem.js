/*
 * SPDX-FileCopyrightText: 2022 CERN.
 * SPDX-License-Identifier: MIT
 */
import PropTypes from "prop-types";
import { Component } from "react";
import { Table } from "semantic-ui-react";
import isEmpty from "lodash/isEmpty";
import { withState } from "react-searchkit";
import { Actions, Edit, Delete } from "@js/invenio_administration";
import { AdminUIRoutes } from "@js/invenio_administration";
import { OverridableContext, parametrize } from "react-overridable";
import { DeleteModal } from "./DeleteModal";
import Formatter from "@js/invenio_administration/src/components/Formatter";
import { i18next } from "@translations/invenio_rdm_records/i18next";

const overridenComponents = {
  "InvenioAdministration.DeleteModal.layout": DeleteModal,
};

const searchResultItemComponentDefaultPropActions = {};
function SearchResultItemComponent({updateQueryState, currentQueryState, resourceSchema, title, resourceName, result, columns, displayEdit = true, displayDelete = true, actions = searchResultItemComponentDefaultPropActions, apiEndpoint = undefined, idKeyPath, listUIEndpoint}) {
  const refreshAfterAction = () => {
    const { updateQueryState, currentQueryState } = this.props;
    updateQueryState(currentQueryState);
  };

  const displayAsPre = (result, property) => {
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

  const resourceHasActions = displayEdit || displayDelete || !isEmpty(actions);

    overridenComponents["InvenioAdministration.EditAction"] = parametrize(Edit, {
      disable: () => result.system_created,
      disabledMessage: i18next.t(
        "This set is not editable as it was created by the system."
      ),
    });

    overridenComponents["InvenioAdministration.DeleteAction"] = parametrize(Delete, {
      disable: () => result.system_created,
      disabledMessage: i18next.t(
        "This set is not deletable as it was created by the system."
      ),
    });

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
                    href={AdminUIRoutes.detailsView(listUIEndpoint, result, idKeyPath)}
                  >
                    {displayAsPre(result, property)}
                  </a>
                ) : (
                  displayAsPre(result, property)
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
                editUrl={AdminUIRoutes.editView(listUIEndpoint, result, idKeyPath)}
                displayEdit={displayEdit}
                displayDelete={displayDelete}
                resource={result}
                idKeyPath={idKeyPath}
                successCallback={refreshAfterAction}
                listUIEndpoint={listUIEndpoint}
              />
            </Table.Cell>
          )}
        </Table.Row>
      </OverridableContext.Provider>
    );
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

export const SearchResultItem = withState(SearchResultItemComponent);
