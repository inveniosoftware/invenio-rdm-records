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
  wrapWithDndProvider,
  enableDrag,
  creatibutorErrors,
  removeCreatibutor,
  replaceCreatibutor,
  moveCreatibutor,
}) {
  const useBatchRender = entries.length > batchSize;
  const [renderLimit, setRenderLimit] = useState(batchSize);
  const batchScheduled = useRef(false);
  const prevEntriesLenRef = useRef(entries.length);

  // Reset the batch window when switching to a different field array.
  useEffect(() => {
    setRenderLimit(batchSize);
  }, [keyPrefix, batchSize]);

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

  // Extend on append so new rows at the end can be mounted.
  if (entries.length > prevEntriesLenRef.current) {
    const newLimit = Math.max(renderLimit, entries.length);
    if (newLimit !== renderLimit) {
      setRenderLimit(newLimit);
    }
  }
  prevEntriesLenRef.current = entries.length;
  const visibleEntries = useBatchRender ? entries.slice(0, renderLimit) : entries;

  const list = (
    <List>
      {visibleEntries.map(({ item, idx, displayName, highlighted = false }) => {
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
            enableDrag={enableDrag}
            creatibutorError={creatibutorErrors?.[idx]}
            highlighted={highlighted}
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
      highlighted: PropTypes.bool,
    })
  ).isRequired,
  keyPrefix: PropTypes.string.isRequired,
  batchSize: PropTypes.number.isRequired,
  wrapWithDndProvider: PropTypes.bool,
  enableDrag: PropTypes.bool,
  creatibutorErrors: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  removeCreatibutor: PropTypes.func.isRequired,
  replaceCreatibutor: PropTypes.func.isRequired,
  moveCreatibutor: PropTypes.func.isRequired,
};

CreatibutorsList.defaultProps = {
  wrapWithDndProvider: true,
  enableDrag: true,
  creatibutorErrors: undefined,
};
