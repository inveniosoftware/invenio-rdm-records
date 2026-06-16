/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import PropTypes from "prop-types";
import { Button, Input } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { CreatibutorsList, getCreatibutorDisplayName } from "./CreatibutorsList";

const getCreatibutorSchemaLabel = (schema) =>
  schema === "contributors" ? i18next.t("contributors") : i18next.t("authors");

const getScrollEdges = (el) => {
  const { scrollTop, scrollHeight, clientHeight } = el;
  return {
    canScrollUp: scrollTop > 0,
    canScrollDown: Math.ceil(scrollTop + clientHeight) < scrollHeight,
  };
};

export const CreatibutorsInlinePanel = React.memo(function CreatibutorsInlinePanel({
  list,
  keyPrefix,
  schema,
  highlightOnAdd,
  creatibutorErrors,
  removeCreatibutor,
  replaceCreatibutor,
  moveCreatibutor,
  roleOptions,
  autocompleteNames,
  addLabel,
  editLabel,
  serializeSuggestions,
  serializeCreatibutor,
  deserializeCreatibutor,
  scrollThreshold,
  batchSize,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [highlightedIndices, setHighlightedIndices] = useState(() => new Set());
  const [canScrollUp, setCanScrollUp] = useState(false);
  const [canScrollDown, setCanScrollDown] = useState(false);
  const [scrollToIndex, setScrollToIndex] = useState(null);

  const scrollRef = useRef(null);
  const prevLengthRef = useRef(list.length);

  const type = getCreatibutorSchemaLabel(schema);

  // Compute display names once per list change rather than on every search keystroke.
  const entriesWithDisplayNames = useMemo(
    () =>
      list.map((item, idx) => ({
        item,
        idx,
        displayName: getCreatibutorDisplayName(item),
      })),
    [list]
  );

  // Filter using the pre-computed display names (cheap string comparison per keystroke).
  const query = searchQuery.toLowerCase().trim();
  const filteredEntries = useMemo(() => {
    if (!query) return entriesWithDisplayNames;
    return entriesWithDisplayNames.filter(({ displayName }) =>
      displayName.toLowerCase().includes(query)
    );
  }, [entriesWithDisplayNames, query]);

  const isScrollable = list.length > scrollThreshold;

  const updateScrollState = useCallback(() => {
    const el = scrollRef.current;
    if (!el) return;
    const { canScrollUp, canScrollDown } = getScrollEdges(el);
    setCanScrollUp(canScrollUp);
    setCanScrollDown(canScrollDown);
  }, []);

  const clearHighlight = useCallback((index) => {
    setHighlightedIndices((prev) => {
      if (!prev.has(index)) return prev;
      const next = new Set(prev);
      next.delete(index);
      return next;
    });
  }, []);

  // When creatibutors are added: clear search, scroll to bottom, highlight new indices.
  useEffect(() => {
    if (!highlightOnAdd || list.length <= prevLengthRef.current) {
      prevLengthRef.current = list.length;
      return;
    }

    const prevLen = prevLengthRef.current;
    prevLengthRef.current = list.length;

    setSearchQuery((query) => (query ? "" : query));
    setHighlightedIndices((prev) => {
      const next = new Set(prev);
      for (let i = prevLen; i < list.length; i++) {
        next.add(i);
      }
      return next;
    });

    setScrollToIndex(list.length - 1);
  }, [highlightOnAdd, list.length]);

  // Scroll the list container once the new row is in the DOM.
  useEffect(() => {
    if (scrollToIndex == null) return;

    if (!isScrollable) {
      setScrollToIndex(null);
      return;
    }

    const el = scrollRef.current;
    if (!el) return;

    const scrollToBottom = () => {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
      updateScrollState();
    };

    const frameId = requestAnimationFrame(() => {
      requestAnimationFrame(scrollToBottom);
    });

    const timeoutId = setTimeout(() => setScrollToIndex(null), 500);
    return () => {
      cancelAnimationFrame(frameId);
      clearTimeout(timeoutId);
    };
  }, [scrollToIndex, isScrollable, updateScrollState]);

  useEffect(() => {
    updateScrollState();
  }, [list.length, filteredEntries.length, updateScrollState]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el || !isScrollable) return;
    const observer = new ResizeObserver(() => updateScrollState());
    observer.observe(el);
    return () => observer.disconnect();
  }, [isScrollable, updateScrollState]);

  const scrollContainerClassName =
    "creatibutors-scroll-container " + (isScrollable ? "scrollable" : "");

  return (
    <div className="creatibutors-inline-panel">
      {isScrollable && (
        <div className="mb-10 flex">
          <Input
            className="creatibutors-filter-input"
            icon="search"
            iconPosition="left"
            placeholder={i18next.t("Filter {{type}}...", { type })}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <span className="creatibutors-count-bar text-muted ml-10">
            {i18next.t("{{shown}} / {{total}}", {
              shown: query ? filteredEntries.length : list.length,
              total: list.length,
            })}
          </span>
        </div>
      )}

      <div className="creatibutors-scroll-wrapper">
        {isScrollable && canScrollUp && (
          <div className="creatibutors-scroll-fade start">
            <Button
              type="button"
              icon="angle double up"
              basic
              className="creatibutors-scroll-btn"
              onClick={() =>
                scrollRef.current?.scrollTo({ top: 0, behavior: "smooth" })
              }
              title={i18next.t("Scroll to top")}
              aria-label={i18next.t("Scroll to top")}
            />
          </div>
        )}

        <div
          className={scrollContainerClassName}
          ref={scrollRef}
          onScroll={updateScrollState}
        >
          <CreatibutorsList
            entries={filteredEntries}
            keyPrefix={keyPrefix}
            filterQuery={query}
            batchSize={batchSize}
            wrapWithDndProvider={false}
            highlightedIndices={highlightedIndices}
            onHighlightEnd={clearHighlight}
            creatibutorErrors={creatibutorErrors}
            roleOptions={roleOptions}
            schema={schema}
            addLabel={addLabel}
            editLabel={editLabel}
            autocompleteNames={autocompleteNames}
            serializeSuggestions={serializeSuggestions}
            serializeCreatibutor={serializeCreatibutor}
            deserializeCreatibutor={deserializeCreatibutor}
            removeCreatibutor={removeCreatibutor}
            replaceCreatibutor={replaceCreatibutor}
            moveCreatibutor={moveCreatibutor}
          />
        </div>

        {isScrollable && canScrollDown && (
          <div className="creatibutors-scroll-fade end">
            <Button
              type="button"
              basic
              icon="angle double down"
              className="creatibutors-scroll-btn"
              onClick={() =>
                scrollRef.current?.scrollTo({
                  top: scrollRef.current.scrollHeight,
                  behavior: "smooth",
                })
              }
              title={i18next.t("Scroll to bottom")}
              aria-label={i18next.t("Scroll to bottom")}
            />
          </div>
        )}
      </div>
    </div>
  );
});

CreatibutorsInlinePanel.propTypes = {
  list: PropTypes.array.isRequired,
  keyPrefix: PropTypes.string.isRequired,
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  highlightOnAdd: PropTypes.bool,
  creatibutorErrors: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  addLabel: PropTypes.node,
  editLabel: PropTypes.node,
  removeCreatibutor: PropTypes.func.isRequired,
  replaceCreatibutor: PropTypes.func.isRequired,
  moveCreatibutor: PropTypes.func.isRequired,
  roleOptions: PropTypes.array.isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
  scrollThreshold: PropTypes.number,
  batchSize: PropTypes.number,
};

CreatibutorsInlinePanel.defaultProps = {
  scrollThreshold: 10,
  batchSize: 20,
  highlightOnAdd: true,
  creatibutorErrors: undefined,
  addLabel: undefined,
  editLabel: undefined,
  autocompleteNames: undefined,
  serializeSuggestions: undefined,
  serializeCreatibutor: undefined,
  deserializeCreatibutor: undefined,
};
