// This file is part of Invenio-RDM-Records
// Copyright (C) 2026 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useEffect, useRef } from "react";
import PropTypes from "prop-types";
import { List } from "semantic-ui-react";
import { HTML5Backend } from "react-dnd-html5-backend";
import { DndProvider } from "react-dnd";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import _get from "lodash/get";
import { CreatibutorsFieldItem } from "../CreatibutorsFieldItem";
import { CREATIBUTOR_TYPE } from "../type";

export const getCreatibutorDisplayName = (value) => {
  const type = _get(value, "person_or_org.type", CREATIBUTOR_TYPE.PERSON);
  const familyName = _get(value, "person_or_org.family_name", "");
  const givenName = _get(value, "person_or_org.given_name", "");
  const name = _get(value, "person_or_org.name", "");
  const affiliations = (value?.affiliations ?? [])
    .map((a) => a.text || a.name)
    .filter(Boolean);
  const suffix = affiliations.length ? ` (${affiliations.join(", ")})` : "";

  if (type === CREATIBUTOR_TYPE.PERSON) {
    const givenNameSuffix = givenName ? `, ${givenName}` : "";
    return `${familyName}${givenNameSuffix}${suffix}`;
  }
  return `${name}${suffix}`;
};

/**
 * Renders a drag-and-drop creatibutor list using CreatibutorsFieldItem.
 * Optionally batches mounting rows to keep large lists responsive.
 */
export function CreatibutorsList({
  entries,
  keyPrefix,
  batchSize,
  wrapWithDndProvider,
  enableDrag,
  creatibutorErrors,
  roleOptions,
  schema,
  autocompleteNames,
  addLabel,
  editLabel,
  serializeSuggestions,
  serializeCreatibutor,
  deserializeCreatibutor,
  removeCreatibutor,
  replaceCreatibutor,
  moveCreatibutor,
  highlightedIndices,
  onHighlightEnd,
}) {
  const useBatchRender = entries.length > batchSize;
  const [renderLimit, setRenderLimit] = useState(batchSize);
  const batchScheduled = useRef(false);
  const prevEntriesLenRef = useRef(entries.length);

  useEffect(() => {
    setRenderLimit(batchSize);
  }, [keyPrefix, batchSize]);

  // Extend the batch window when rows are appended so new items at the end mount.
  useEffect(() => {
    if (!useBatchRender) return;
    if (entries.length > prevEntriesLenRef.current) {
      setRenderLimit((prev) => Math.max(prev, entries.length));
    }
    prevEntriesLenRef.current = entries.length;
  }, [entries.length, useBatchRender]);

  // Mount additional rows one batch per animation frame so the UI stays responsive.
  useEffect(() => {
    if (!useBatchRender || renderLimit >= entries.length) return;

    if (batchScheduled.current) return;
    batchScheduled.current = true;

    const frameId = requestAnimationFrame(() => {
      batchScheduled.current = false;
      setRenderLimit((prev) => Math.min(prev + batchSize, entries.length));
    });

    return () => {
      cancelAnimationFrame(frameId);
      // Reset the guard so a future render can schedule the next batch.
      batchScheduled.current = false;
    };
  }, [useBatchRender, renderLimit, entries.length, batchSize]);

  const visibleEntries = useBatchRender ? entries.slice(0, renderLimit) : entries;

  const list = (
    <List>
      {visibleEntries.map(({ item, idx }) => {
        const key = `${keyPrefix}.${idx}`;
        return (
          <CreatibutorsFieldItem
            key={key}
            index={idx}
            displayName={getCreatibutorDisplayName(item)}
            compKey={key}
            initialCreatibutor={item}
            roleOptions={roleOptions}
            schema={schema}
            autocompleteNames={autocompleteNames}
            addLabel={addLabel}
            editLabel={editLabel}
            serializeSuggestions={serializeSuggestions}
            serializeCreatibutor={serializeCreatibutor}
            deserializeCreatibutor={deserializeCreatibutor}
            removeCreatibutor={removeCreatibutor}
            replaceCreatibutor={replaceCreatibutor}
            moveCreatibutor={moveCreatibutor}
            enableDrag={enableDrag}
            highlighted={highlightedIndices?.has(idx)}
            onHighlightEnd={onHighlightEnd}
            creatibutorError={creatibutorErrors?.[idx]}
          />
        );
      })}
    </List>
  );

  return (
    <>
      {wrapWithDndProvider ? (
        <DndProvider backend={HTML5Backend}>{list}</DndProvider>
      ) : (
        list
      )}
      {useBatchRender && renderLimit < entries.length && (
        <div className="creatibutors-count-bar mt-15">
          <span className="text-muted">{i18next.t("Loading more...")}</span>
        </div>
      )}
    </>
  );
}

CreatibutorsList.propTypes = {
  entries: PropTypes.arrayOf(
    PropTypes.shape({
      item: PropTypes.object.isRequired,
      idx: PropTypes.number.isRequired,
    })
  ).isRequired,
  keyPrefix: PropTypes.string.isRequired,
  batchSize: PropTypes.number,
  wrapWithDndProvider: PropTypes.bool,
  enableDrag: PropTypes.bool,
  creatibutorErrors: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  roleOptions: PropTypes.array.isRequired,
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  addLabel: PropTypes.node,
  editLabel: PropTypes.node,
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
  removeCreatibutor: PropTypes.func.isRequired,
  replaceCreatibutor: PropTypes.func.isRequired,
  moveCreatibutor: PropTypes.func.isRequired,
  highlightedIndices: PropTypes.instanceOf(Set),
  onHighlightEnd: PropTypes.func,
};

CreatibutorsList.defaultProps = {
  batchSize: 20,
  wrapWithDndProvider: true,
  enableDrag: true,
  creatibutorErrors: undefined,
  autocompleteNames: undefined,
  addLabel: undefined,
  editLabel: undefined,
  serializeSuggestions: undefined,
  serializeCreatibutor: undefined,
  deserializeCreatibutor: undefined,
  highlightedIndices: undefined,
  onHighlightEnd: undefined,
};
