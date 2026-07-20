/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

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
export const CreatibutorsList = React.memo(function CreatibutorsList({
  entries,
  keyPrefix,
  batchSize,
  totalCount,
  wrapWithDndProvider,
  creatibutorErrors,
  removeCreatibutor,
  replaceCreatibutor,
  moveCreatibutor,
}) {
  const useBatchRender = entries.length > batchSize;
  const [renderLimit, setRenderLimit] = useState(batchSize);
  const batchScheduled = useRef(false);
  const prevTotalCountRef = useRef(totalCount);

  // Reset the batch window when switching to a different field array.
  useEffect(() => {
    setRenderLimit(batchSize);
  }, [keyPrefix, batchSize]);

  // Extend on append (full list grew), not when filter results widen.
  useEffect(() => {
    if (totalCount > prevTotalCountRef.current) {
      setRenderLimit((prev) => Math.max(prev, entries.length));
    }
    prevTotalCountRef.current = totalCount;
  }, [totalCount, entries.length]);

  // If the list gets shorter (like after filtering), lower the number of rendered items so loading more starts again when needed.
  useEffect(() => {
    setRenderLimit((prev) => Math.min(prev, entries.length));
  }, [entries.length]);

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
      {visibleEntries.map(({ item, idx, displayName }) => {
        const key = `${keyPrefix}.${idx}`;
        return (
          <CreatibutorsFieldItem
            key={key}
            index={idx}
            compKey={key}
            initialCreatibutor={item}
            displayName={displayName}
            removeCreatibutor={removeCreatibutor}
            replaceCreatibutor={replaceCreatibutor}
            moveCreatibutor={moveCreatibutor}
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
});

CreatibutorsList.propTypes = {
  entries: PropTypes.arrayOf(
    PropTypes.shape({
      item: PropTypes.object.isRequired,
      idx: PropTypes.number.isRequired,
      displayName: PropTypes.string,
    })
  ).isRequired,
  keyPrefix: PropTypes.string.isRequired,
  batchSize: PropTypes.number.isRequired,
  totalCount: PropTypes.number.isRequired,
  wrapWithDndProvider: PropTypes.bool,
  creatibutorErrors: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  removeCreatibutor: PropTypes.func.isRequired,
  replaceCreatibutor: PropTypes.func.isRequired,
  moveCreatibutor: PropTypes.func.isRequired,
};

CreatibutorsList.defaultProps = {
  wrapWithDndProvider: true,
  creatibutorErrors: undefined,
};
