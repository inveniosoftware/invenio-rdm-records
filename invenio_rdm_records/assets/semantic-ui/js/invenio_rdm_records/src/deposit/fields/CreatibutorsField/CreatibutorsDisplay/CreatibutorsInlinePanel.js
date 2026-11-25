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

export const CreatibutorsInlinePanel = React.memo(function CreatibutorsInlinePanel({
  type,
  list,
  keyPrefix,
  creatibutorErrors,
  removeCreatibutor,
  replaceCreatibutor,
  moveCreatibutor,
  scrollThreshold,
  batchSize,
}) {
  const [searchQuery, setSearchQuery] = useState("");
  const [scrollToIndex, setScrollToIndex] = useState(null);

  const scrollRef = useRef(null);
  const wrapperRef = useRef(null);
  const prevLengthRef = useRef(list.length);
  // Holds the latest sync function so it can be called when content height changes without re-registering the scroll listener.
  const syncScrollEdgesRef = useRef(null);

  // Compute display names once per list change rather than on every search keystroke.
  const query = normalizeSearch(searchQuery.trim());
  const entriesWithDisplayNames = useMemo(
    () =>
      list.map((item, idx) => {
        const displayName = getCreatibutorDisplayName(item);
        return {
          item,
          idx,
          displayName,
          searchName: normalizeSearch(displayName),
        };
      }),
    [list]
  );

  const filteredEntries = useMemo(() => {
    if (!query) return entriesWithDisplayNames;
    return entriesWithDisplayNames.filter(({ searchName }) =>
      searchName.includes(query)
    );
  }, [entriesWithDisplayNames, query]);

  const isScrollable = list.length > scrollThreshold;

  // When creatibutors are added: clear search and scroll to bottom.
  useEffect(() => {
    if (list.length <= prevLengthRef.current) {
      prevLengthRef.current = list.length;
      return;
    }

    prevLengthRef.current = list.length;

    setSearchQuery((q) => (q ? "" : q));
    setScrollToIndex(list.length - 1);
  }, [list.length]);

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

  // Scroll the container once the new row is in the DOM.
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
            placeholder={i18next.t(`Filter ${type}...`)}
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
            batchSize={batchSize}
            totalCount={list.length}
            wrapWithDndProvider={false}
            creatibutorErrors={creatibutorErrors}
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
  type: PropTypes.string.isRequired,
  creatibutorErrors: PropTypes.oneOfType([PropTypes.object, PropTypes.array]),
  removeCreatibutor: PropTypes.func.isRequired,
  replaceCreatibutor: PropTypes.func.isRequired,
  moveCreatibutor: PropTypes.func.isRequired,
  scrollThreshold: PropTypes.number,
  batchSize: PropTypes.number,
};

CreatibutorsInlinePanel.defaultProps = {
  scrollThreshold: 10,
  batchSize: 30,
  creatibutorErrors: undefined,
};
