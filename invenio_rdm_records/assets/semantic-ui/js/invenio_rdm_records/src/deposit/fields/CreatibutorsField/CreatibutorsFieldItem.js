/*
 * SPDX-FileCopyrightText: 2020-2026 CERN.
 * SPDX-FileCopyrightText: 2020-2022 Northwestern University.
 * SPDX-FileCopyrightText: 2021 New York University.
 * SPDX-FileCopyrightText: 2024 KTH Royal Institute of Technology.
 * SPDX-License-Identifier: MIT
 */

import { i18next } from "@translations/invenio_rdm_records/i18next";
import _get from "lodash/get";
import React, { useRef, useState, useEffect, useContext, createContext } from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, Label, List, Ref } from "semantic-ui-react";
import { FeedbackLabel } from "react-invenio-forms";
import { CreatibutorsModal } from "./CreatibutorsModal";
import PropTypes from "prop-types";

// Item-level config context provided to all rows by parent components.
export const CreatibutorsItemContext = createContext(null);

// until: 0 keeps Date.now() >= until true until an add sets a future expiry.
const NO_HIGHLIGHT = { from: 0, until: 0, shown: new Set() };

const renderRole = (role, roleOptions) => {
  if (!role) return null;
  const friendlyRole = roleOptions.find(({ value }) => value === role)?.text ?? role;
  return <Label size="tiny">{friendlyRole}</Label>;
};

export const CreatibutorsFieldItem = React.memo(function CreatibutorsFieldItem({
  compKey,
  creatibutorError,
  index,
  replaceCreatibutor,
  removeCreatibutor,
  moveCreatibutor,
  initialCreatibutor,
  displayName,
}) {
  const {
    roleOptions,
    schema,
    autocompleteNames,
    addLabel,
    editLabel,
    serializeSuggestions,
    serializeCreatibutor,
    deserializeCreatibutor,
    highlight = NO_HIGHLIGHT,
  } = useContext(CreatibutorsItemContext) ?? {};

  const [isHighlighted, setIsHighlighted] = useState(() => {
    if (
      index < highlight.from ||
      Date.now() >= highlight.until ||
      highlight.shown.has(index)
    )
      return false;
    highlight.shown.add(index);
    return true;
  });

  useEffect(() => {
    if (!isHighlighted) return;
    const t = setTimeout(
      () => setIsHighlighted(false),
      Math.max(0, highlight.until - Date.now())
    );
    return () => clearTimeout(t);
  }, [isHighlighted, highlight]);

  const dropRef = useRef(null);
  const modalRef = useRef(null);
  const [mountModal, setMountModal] = useState(false);

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

  // After the modal mounts for the first time, open it immediately.
  useEffect(() => {
    if (mountModal && modalRef.current) {
      modalRef.current.openModal();
    }
  }, [mountModal]);

  const handleEditClick = () => {
    if (mountModal && modalRef.current) {
      // Already mounted from a previous edit - open directly.
      modalRef.current.openModal();
    } else {
      // First edit: mount the modal; the effect above will open it.
      setTimeout(() => setMountModal(true), 0);
    }
  };

  // Initialize the ref explicitely
  drop(dropRef);
  return (
    <Ref innerRef={dropRef} key={compKey}>
      <List.Item
        key={compKey}
        className={[
          "deposit-drag-listitem",
          hidden && "drag-ghost",
          isHighlighted && "highlighted",
        ]
          .filter(Boolean)
          .join(" ")}
      >
        <List.Content floated="right">
          <Button size="mini" type="button" onClick={() => removeCreatibutor(index)}>
            {i18next.t("Remove")}
          </Button>
          {/* Edit button mounts the modal lazily on first click. */}
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
              trigger={null}
              serializeSuggestions={serializeSuggestions}
              serializeCreatibutor={serializeCreatibutor}
              deserializeCreatibutor={deserializeCreatibutor}
            />
          )}
        </List.Content>
        <Ref innerRef={drag}>
          <List.Icon name="bars" className="drag-anchor" />
        </Ref>
        <Ref innerRef={preview}>
          <List.Content>
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
                {displayName} {renderRole(initialCreatibutor?.role, roleOptions)}
              </span>
            </List.Description>
            {creatibutorError && (
              <FeedbackLabel fieldPath={`${compKey}`} hasSubfields />
            )}
          </List.Content>
        </Ref>
      </List.Item>
    </Ref>
  );
});

CreatibutorsFieldItem.propTypes = {
  compKey: PropTypes.string.isRequired,
  creatibutorError: PropTypes.array,
  index: PropTypes.number.isRequired,
  replaceCreatibutor: PropTypes.func.isRequired,
  removeCreatibutor: PropTypes.func.isRequired,
  moveCreatibutor: PropTypes.func.isRequired,
  initialCreatibutor: PropTypes.object.isRequired,
  displayName: PropTypes.string,
};

CreatibutorsFieldItem.defaultProps = {
  creatibutorError: undefined,
  displayName: undefined,
};
