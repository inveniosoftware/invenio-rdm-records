/*
 * SPDX-FileCopyrightText: 2025 CERN.
 * SPDX-FileCopyrightText: 2026 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";
import { useState } from "react";
import { Button, Icon, Popup } from "semantic-ui-react";
import { ModificationModal } from "./ModificationModal";

export const FileModification = ({
  disabled,
  draft,
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
          // Extra span needed since disabled buttons do not trigger hover events
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
        draft={draft}
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
  draft: PropTypes.object.isRequired,
  record: PropTypes.object.isRequired,
  permissions: PropTypes.object.isRequired,
  fileModification: PropTypes.object,
};

FileModification.defaultProps = {
  disabled: false,
  fileModification: {},
};
