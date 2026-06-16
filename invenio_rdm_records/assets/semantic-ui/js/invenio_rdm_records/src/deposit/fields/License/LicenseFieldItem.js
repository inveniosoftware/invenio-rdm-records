/*
 * SPDX-FileCopyrightText: 2020-2023 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 Graz University of Technology.
 * SPDX-License-Identifier: MIT
 */

import { useRef } from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, List } from "semantic-ui-react";
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
  const dropRef = useRef(null);

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
    <List.Item
      ref={dropRef}
      key={license.key}
      className={hidden ? "deposit-drag-listitem hidden" : "deposit-drag-listitem"}
    >
      <List.Content floated="right">
        <Button
          size="mini"
          type="button"
          onClick={() => {
            removeLicense(license.index);
          }}
        >
          {i18next.t("Remove")}
        </Button>
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
      </List.Content>
      <List.Icon ref={drag} name="bars" className="drag-anchor" />
      <List.Content ref={preview}>
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
    </List.Item>
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
