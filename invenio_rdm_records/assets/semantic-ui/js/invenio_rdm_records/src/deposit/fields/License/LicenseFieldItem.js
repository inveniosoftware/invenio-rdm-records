// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, List, Ref } from "semantic-ui-react";
import _truncate from "lodash/truncate";
import { LicenseModal } from "./LicenseModal";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import PropTypes from "prop-types";

export const LicenseFieldItem = ({
  license,
  moveLicense,
  replaceLicense,
  removeLicense,
  searchConfig,
  serializeLicenses,
}) => {
  const dropRef = React.useRef(null);

  const [, drag, preview] = useDrag({
    item: { index: license.index, type: "license" },
  });
  const [{ hidden }, drop] = useDrop({
    accept: "license",
    hover(item, monitor) {
      if (!dropRef.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = license.index;

      // Don't replace items with themselves
      if (dragIndex === hoverIndex) {
        return;
      }

      if (monitor.isOver({ shallow: true })) {
        moveLicense(dragIndex, hoverIndex);
        item.index = hoverIndex;
      }
    },
    collect: (monitor) => ({
      hidden: monitor.isOver({ shallow: true }),
    }),
  });

  // Initialize the ref explicitely
  drop(dropRef);
  return (
    <Ref innerRef={dropRef} key={license.key}>
      <List.Item
        key={license.key}
        className={hidden ? "deposit-drag-listitem hidden" : "deposit-drag-listitem"}
      >
        <List.Content floated="right">
          <LicenseModal
            searchConfig={searchConfig}
            onLicenseChange={(selectedLicense) => {
              replaceLicense(license.index, selectedLicense);
            }}
            mode={license.type}
            initialLicense={license.initial}
            action="edit"
            trigger={
              <Button size="mini" primary type="button">
                {i18next.t("Edit")}
              </Button>
            }
            serializeLicenses={serializeLicenses}
          />
          <Button
            size="mini"
            type="button"
            onClick={() => {
              removeLicense(license.index);
            }}
          >
            {i18next.t("Remove")}
          </Button>
        </List.Content>
        <Ref innerRef={drag}>
          <List.Icon name="bars" className="drag-anchor" />
        </Ref>
        <Ref innerRef={preview}>
          <List.Content>
            <List.Header>{license.title}</List.Header>
            {license.description && (
              <List.Description>
                {_truncate(license.description, { length: 300 })}
              </List.Description>
            )}
            {license.link && (
              <span>
                <a href={license.link} target="_blank" rel="noopener noreferrer">
                  {license.description && <span>&nbsp;</span>}
                  {i18next.t("Read more")}
                </a>
              </span>
            )}
          </List.Content>
        </Ref>
      </List.Item>
    </Ref>
  );
};

LicenseFieldItem.propTypes = {
  license: PropTypes.object.isRequired,
  moveLicense: PropTypes.func.isRequired,
  replaceLicense: PropTypes.func.isRequired,
  removeLicense: PropTypes.func.isRequired,
  searchConfig: PropTypes.object.isRequired,
  serializeLicenses: PropTypes.func,
};

LicenseFieldItem.defaultProps = {
  serializeLicenses: undefined,
};
