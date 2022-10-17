// This file is part of InvenioAdministration
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import PropTypes from "prop-types";
import { Button, Icon, Message, Checkbox } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { Modal } from "semantic-ui-react";
import { Trans } from "react-i18next";
import isEmpty from "lodash/isEmpty";
import { ErrorMessage } from "@js/invenio_administration";

export class DeleteModal extends Component {
  constructor(props) {
    super(props);
    this.state = { loading: false, error: undefined, checked: false };
  }

  render() {
    const { loading, error, checked } = this.state;
    const {
      resetErrorState,
      cleanError,
      handleOnButtonClick,
      modalOpen,
      toggleModal,
      title,
    } = this.props;
    return (
      <Modal role="dialog" open={modalOpen}>
        <Modal.Header as="h2">
          <Trans defaults="Delete {{title}}" values={{ title: title }} />
        </Modal.Header>
        <Modal.Content>
          <Modal.Description>
            <Message
              warning
              icon="warning sign"
              header={
                <Trans
                  defaults="This will delete the set '{{title}}'."
                  values={{ title: title }}
                />
              }
              content={i18next.t(
                "Before deleting, make sure to alert all harvesters that this set will no longer be available."
              )}
            />
            <Checkbox
              className="ml-5"
              value={true}
              checked={checked}
              onChange={(event, data) => {
                this.setState({ checked: data.checked });
              }}
              label={i18next.t(
                "I have alerted all harvesters that this set will no longer be available."
              )}
            />
            {!isEmpty(error) && (
              <ErrorMessage {...error} removeNotification={resetErrorState} />
            )}
          </Modal.Description>
        </Modal.Content>
        <Modal.Actions>
          <Button
            icon="cancel"
            onClick={() => {
              cleanError();
              toggleModal(false);
            }}
            loading={loading}
            content={i18next.t("Cancel")}
            floated="left"
            size="medium"
          />
          <Button
            disabled={!checked}
            negative
            onClick={handleOnButtonClick}
            loading={loading}
          >
            <Icon name="trash alternate" />
            {i18next.t("Delete")}
          </Button>
        </Modal.Actions>
      </Modal>
    );
  }
}

DeleteModal.propTypes = {
  title: PropTypes.string.isRequired,
  apiEndpoint: PropTypes.string.isRequired,
  resource: PropTypes.object.isRequired,
  successCallback: PropTypes.func.isRequired,
  idKeyPath: PropTypes.string.isRequired,
  toggleModal: PropTypes.func.isRequired,
  modalOpen: PropTypes.bool.isRequired,
  children: PropTypes.node,
  handleOnButtonClick: PropTypes.func.isRequired,
  cleanError: PropTypes.func.isRequired,
  resetErrorState: PropTypes.func.isRequired,
};

DeleteModal.defaultProps = {
  children: null,
};
