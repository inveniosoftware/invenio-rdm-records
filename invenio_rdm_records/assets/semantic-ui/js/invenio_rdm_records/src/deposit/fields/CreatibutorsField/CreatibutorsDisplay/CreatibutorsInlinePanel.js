/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import React, { useEffect, useMemo, useRef, useState } from "react";
import PropTypes from "prop-types";
import { Button, Input } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { CreatibutorsList, getCreatibutorDisplayName } from "./CreatibutorsList";

// Normalise a string for diacritic insensitive search: decompose into base chars +
// combining marks, strip the marks, then lower-case while still matching the literal character.
const normalizeSearch = (str) =>
  str
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase();

const getCreatibutorSchemaLabel = (schema) =>
  schema === "contributors" ? i18next.t("contributors") : i18next.t("authors");

export const CreatibutorsInlinePanel = React.memo(function CreatibutorsInlinePanel({
  list,
  keyPrefix,
  schema,
  highlightOnAdd,
  highlightDuration,
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
  const [scrollToIndex, setScrollToIndex] = useState(null);

  const scrollRef = useRef(null);
  const wrapperRef = useRef(null);
  const prevLengthRef = useRef(list.length);
  const highlightTimerRef = useRef(null);
  // Holds the latest sync function so it can be called when content height changes
  // without re-registering the scroll listener.
  const syncScrollEdgesRef = useRef(null);

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
  // normalizeSearch strips diacritics so "u" matches "ü", etc.
  const query = normalizeSearch(searchQuery.trim());
  const filteredEntries = useMemo(() => {
    if (!query) return entriesWithDisplayNames;
    return entriesWithDisplayNames.filter(({ displayName }) =>
      normalizeSearch(displayName).includes(query)
    );
  }, [entriesWithDisplayNames, query]);

  const isScrollable = list.length > scrollThreshold;

  // When creatibutors are added: clear search, scroll to bottom, highlight new rows.
  // A single timer clears all highlights after the animation completes — no need to
  // track each index individually via a callback chain.
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

    if (highlightTimerRef.current) clearTimeout(highlightTimerRef.current);
    highlightTimerRef.current = setTimeout(() => {
      setHighlightedIndices(new Set());
      highlightTimerRef.current = null;
    }, highlightDuration);

    setScrollToIndex(list.length - 1);
  }, [highlightOnAdd, list.length, highlightDuration]);

  // Clean up the highlight timer on unmount.
  useEffect(
    () => () => {
      if (highlightTimerRef.current) clearTimeout(highlightTimerRef.current);
    },
    []
  );

  // Toggle .can-scroll-up / .can-scroll-down directly
  // no state handling, so scroll events never trigger re-renders
  useEffect(() => {
    const el = scrollRef.current;
    const wrapper = wrapperRef.current;
    if (!el || !wrapper || !isScrollable) {
      wrapper?.classList.remove("can-scroll-up", "can-scroll-down");
      syncScrollEdgesRef.current = null;
      return;
    }

    const sync = () => {
      wrapper.classList.toggle("can-scroll-up", el.scrollTop > 0);
      wrapper.classList.toggle(
        "can-scroll-down",
        el.scrollTop < el.scrollHeight - el.clientHeight - 1
      );
    };
    syncScrollEdgesRef.current = sync;

    sync();
    el.addEventListener("scroll", sync, { passive: true });
    return () => {
      el.removeEventListener("scroll", sync);
      syncScrollEdgesRef.current = null;
    };
  }, [isScrollable]);

  // Resync scroll edges when filtered results change the scroll container's content height.
  useEffect(() => {
    syncScrollEdgesRef.current?.();
  }, [filteredEntries]);

  // Scroll the container once the new row is in the DOM (double rAF ensures layout is ready).
  useEffect(() => {
    if (scrollToIndex == null || !isScrollable) {
      setScrollToIndex(null);
      return;
    }

    const el = scrollRef.current;
    if (!el) return;

    const frameId = requestAnimationFrame(() => {
      el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
    });

    const timeoutId = setTimeout(() => setScrollToIndex(null), 500);
    return () => {
      cancelAnimationFrame(frameId);
      clearTimeout(timeoutId);
    };
  }, [scrollToIndex, isScrollable]);

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

      <div className="creatibutors-scroll-wrapper" ref={wrapperRef}>
        {/* Scroll-to-top shortcut: always shown when list is scrollable. Clicking when
            already at the top is a harmless no-op and avoids JS scroll-edge detection. */}
        {isScrollable && (
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

        <div className={scrollContainerClassName} ref={scrollRef}>
          <CreatibutorsList
            entries={filteredEntries}
            keyPrefix={keyPrefix}
            filterQuery={query}
            batchSize={batchSize}
            wrapWithDndProvider={false}
            highlightedIndices={highlightedIndices}
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

        {/* Scroll-to-bottom shortcut: same rationale as scroll-to-top above. */}
        {isScrollable && (
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
  highlightDuration: PropTypes.number,
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
  batchSize: 30,
  highlightDuration: 2000, // 2 seconds
  highlightOnAdd: true,
  creatibutorErrors: undefined,
  addLabel: undefined,
  editLabel: undefined,
  autocompleteNames: undefined,
  serializeSuggestions: undefined,
  serializeCreatibutor: undefined,
  deserializeCreatibutor: undefined,
};
