// This file is part of InvenioRDM
// Copyright (C) 2025.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import React, { useState } from "react";
import { Button, Icon, Popup } from "semantic-ui-react";
import { ModificationModal } from "./ModificationModal";

export const FileModification = ({
  disabled,
  record,
  permissions,
  fileModification,
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const handleOpen = () => setModalOpen(true);
  const handleClose = () => setModalOpen(false);

  return (
    <>
      <Popup
        content={i18next.t("It is not possible to modify the files of this record.")}
        disabled={!disabled}
        trigger={
          <span>
            <Button
              type="button"
              size="mini"
              icon
              labelPosition="left"
              primary
              disabled={disabled}
              aria-haspopup="dialog"
              onClick={handleOpen}
            >
              <Icon name="lock open" />
              {i18next.t("Edit published files")}
            </Button>
          </span>
        }
      />
      <ModificationModal
        record={record}
        open={modalOpen}
        handleClose={handleClose}
        permissions={permissions}
        fileModification={fileModification}
      />
    </>
  );
};

FileModification.propTypes = {
  disabled: PropTypes.bool,
  record: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
  fileModification: PropTypes.object,
};

FileModification.defaultProps = {
  disabled: false,
  fileModification: {},
};
