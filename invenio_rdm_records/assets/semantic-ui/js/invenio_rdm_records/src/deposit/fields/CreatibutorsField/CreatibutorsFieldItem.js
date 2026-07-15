/*
 * SPDX-FileCopyrightText: 2020-2025 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 New York University.
 * SPDX-FileCopyrightText: 2024 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import _get from "lodash/get";
import { memo, useRef, useState, useEffect, useMemo } from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, Label, List } from "semantic-ui-react";
import { FeedbackLabel } from "react-invenio-forms";
import { CreatibutorsModal } from "./CreatibutorsModal";
import { CREATIBUTOR_TYPE } from "./type";
import PropTypes from "prop-types";

export const getCreatibutorDisplayName = (value) => {
  const creatibutorType = _get(value, "person_or_org.type", CREATIBUTOR_TYPE.PERSON);
  const isPerson = creatibutorType === CREATIBUTOR_TYPE.PERSON;

  const familyName = _get(value, "person_or_org.family_name", "");
  const givenName = _get(value, "person_or_org.given_name", "");
  const affiliations = value?.affiliations.map(
    (affiliation) => affiliation.text || affiliation.name
  );
  const name = _get(value, `person_or_org.name`);

  const affiliation = affiliations.length ? ` (${affiliations.join(", ")})` : "";

  if (isPerson) {
    const givenNameSuffix = givenName ? `, ${givenName}` : "";
    return `${familyName}${givenNameSuffix}${affiliation}`;
  }

  return `${name}${affiliation}`;
};

export const CreatibutorsFieldItem = memo(function CreatibutorsFieldItem({
  compKey,
  creatibutorError = undefined,
  index,
  replaceCreatibutor,
  removeCreatibutor,
  moveCreatibutor,
  addLabel = undefined,
  editLabel = undefined,
  initialCreatibutor,
  displayName = undefined,
  roleOptions,
  schema,
  autocompleteNames = undefined,
  serializeSuggestions = undefined,
  serializeCreatibutor = undefined,
  deserializeCreatibutor = undefined,
}) {
  const dropRef = useRef(null);
  const modalRef = useRef(null);
  const [mountModal, setMountModal] = useState(false);

  // Only recompute the display string when this author's data actually changes.
  const creatibutorDisplayName = useMemo(
    () => getCreatibutorDisplayName(initialCreatibutor),
    [initialCreatibutor]
  );

  // eslint-disable-next-line no-unused-vars
  const [_, drag, preview] = useDrag({
    item: { index, type: "creatibutor" },
  });
  const [{ hidden }, drop] = useDrop({
    accept: "creatibutor",
    hover(item, monitor) {
      if (!dropRef.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = index;

      // Don't replace items with themselves
      if (dragIndex === hoverIndex) {
        return;
      }

      if (monitor.isOver({ shallow: true })) {
        moveCreatibutor(dragIndex, hoverIndex);
        item.index = hoverIndex;
      }
    },
    collect: (monitor) => ({
      hidden: monitor.isOver({ shallow: true }),
    }),
  });

  useEffect(() => {
    if (mountModal && modalRef.current) {
      modalRef.current.openModal();
    }
  }, [mountModal]);

  const handleEditClick = () => {
    if (mountModal && modalRef.current) {
      // Already mounted from a previous edit – open directly.
      modalRef.current.openModal();
    } else {
      // First edit: mount the modal; the effect above will open it.
      setMountModal(true);
    }
  };

  const renderRole = (role, roleOptions) => {
    if (role) {
      const friendlyRole =
        roleOptions.find(({ value }) => value === role)?.text ?? role;

      return <Label size="tiny">{friendlyRole}</Label>;
    }
  };

  // Initialize the ref explicitly
  drop(dropRef);
  return (
    <List.Item
      ref={dropRef}
      key={compKey}
      className={hidden ? "deposit-drag-listitem hidden" : "deposit-drag-listitem"}
    >
      <List.Content floated="right">
        <Button size="mini" type="button" onClick={() => removeCreatibutor(index)}>
          {i18next.t("Remove")}
        </Button>
        <Button size="mini" primary type="button" onClick={handleEditClick}>
          {i18next.t("Edit")}
        </Button>
        {mountModal && (
          <CreatibutorsModal
            ref={modalRef}
            addLabel={addLabel}
            editLabel={editLabel}
            onCreatibutorChange={(selectedCreatibutor) => {
              replaceCreatibutor(index, selectedCreatibutor);
            }}
            initialCreatibutor={initialCreatibutor}
            roleOptions={roleOptions}
            schema={schema}
            autocompleteNames={autocompleteNames}
            action="edit"
            serializeSuggestions={serializeSuggestions}
            serializeCreatibutor={serializeCreatibutor}
            deserializeCreatibutor={deserializeCreatibutor}
          />
        )}
      </List.Content>
      <List.Icon ref={drag} name="bars" className="drag-anchor" />
      <List.Content ref={preview}>
        <List.Description>
          <span className="creatibutor">
            {_get(initialCreatibutor, "person_or_org.identifiers", []).some(
              (identifier) => identifier.scheme === "orcid"
            ) && (
              <img
                alt={i18next.t("ORCID logo")}
                className="inline-id-icon mr-5"
                src="/static/images/orcid.svg"
                width="16"
                height="16"
              />
            )}
            {_get(initialCreatibutor, "person_or_org.identifiers", []).some(
              (identifier) => identifier.scheme === "ror"
            ) && (
              <img
                alt={i18next.t("ROR logo")}
                className="inline-id-icon mr-5"
                src="/static/images/ror-icon.svg"
                width="16"
                height="16"
              />
            )}
            {_get(initialCreatibutor, "person_or_org.identifiers", []).some(
              (identifier) => identifier.scheme === "gnd"
            ) && (
              <img
                alt={i18next.t("GND logo")}
                className="inline-id-icon mr-5"
                src="/static/images/gnd-icon.svg"
                width="16"
                height="16"
              />
            )}
            {displayName || creatibutorDisplayName}
            {renderRole(initialCreatibutor?.role, roleOptions)}
          </span>
        </List.Description>
        {creatibutorError && <FeedbackLabel fieldPath={`${compKey}`} hasSubfields />}
      </List.Content>
    </List.Item>
  );
});

CreatibutorsFieldItem.propTypes = {
  compKey: PropTypes.string.isRequired,
  creatibutorError: PropTypes.array,
  index: PropTypes.number.isRequired,
  replaceCreatibutor: PropTypes.func.isRequired,
  removeCreatibutor: PropTypes.func.isRequired,
  moveCreatibutor: PropTypes.func.isRequired,
  addLabel: PropTypes.node,
  editLabel: PropTypes.node,
  initialCreatibutor: PropTypes.object.isRequired,
  displayName: PropTypes.string,
  roleOptions: PropTypes.array.isRequired,
  schema: PropTypes.string.isRequired,
  autocompleteNames: PropTypes.oneOfType([PropTypes.bool, PropTypes.string]),
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
};
