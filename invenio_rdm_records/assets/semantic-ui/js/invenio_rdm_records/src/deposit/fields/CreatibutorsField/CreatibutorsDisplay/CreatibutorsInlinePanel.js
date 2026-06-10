// This file is part of Invenio-RDM-Records
// Copyright (C) 2026 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useCallback, useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { Button, Input } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { CreatibutorsList, getCreatibutorDisplayName } from "./CreatibutorsList";

const getCreatibutorSchemaLabel = (schema) =>
  schema === "contributors" ? i18next.t("contributors") : i18next.t("authors");

const filterCreatibutorsByQuery = (list, searchQuery) => {
  const query = searchQuery.toLowerCase().trim();
  return list.reduce((acc, item, idx) => {
    if (!query || getCreatibutorDisplayName(item).toLowerCase().includes(query)) {
      acc.push({ item, idx });
    }
    return acc;
  }, []);
};

const getScrollEdges = (el) => {
  const { scrollTop, scrollHeight, clientHeight } = el;
  return {
    canScrollUp: scrollTop > 0,
    canScrollDown: Math.ceil(scrollTop + clientHeight) < scrollHeight,
  };
};

export function CreatibutorsInlinePanel({
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
  const query = searchQuery.toLowerCase().trim();
  const filteredEntries = filterCreatibutorsByQuery(list, searchQuery);
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
        <div className="mb-10">
          <Input
            fluid
            icon="search"
            iconPosition="left"
            placeholder={i18next.t(
              "Search {{type}} by name, identifier or affiliation...",
              { type }
            )}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className="creatibutors-count-bar mt-5">
            <span className="text-muted">
              {query
                ? i18next.t("{{shown}} / {{total}}", {
                    shown: filteredEntries.length,
                    total: list.length,
                  })
                : i18next.t("{{count}} total", { count: list.length })}
            </span>
          </div>
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
            keyPrefix={`${keyPrefix}.${query}`}
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
}

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
