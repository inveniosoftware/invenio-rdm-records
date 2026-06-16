/*
 * SPDX-FileCopyrightText: 2021 CERN.
 * SPDX-License-Identifier: MIT
 */

import { useState, useRef } from "react";
import PropTypes from "prop-types";
import { Button, Popup } from "semantic-ui-react";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { i18next } from "@translations/invenio_rdm_records/i18next";

const INITIAL_STATE = {
  confirmationPopupIsOpen: false,
  confirmationPopupMsg: null,
  hoverPopupIsOpen: false,
};

function SimpleCopyButton({ text, onCopy, hoverState = null }) {
  return (
    <CopyToClipboard
      text={text}
      onCopy={() => {
        onCopy(text);
      }}
    >
      <Button
        floated="right"
        basic
        icon="copy"
        aria-label={i18next.t("Copy to clipboard")}
        onMouseEnter={hoverState}
        onMouseLeave={hoverState}
      />
    </CopyToClipboard>
  );
}

SimpleCopyButton.propTypes = {
  text: PropTypes.string.isRequired,
  onCopy: PropTypes.func.isRequired,
  hoverState: PropTypes.func,
};

export default function CopyButton({ text = "", popUpPosition = "right center" }) {
  const [confirmationPopupIsOpen, setConfirmationPopupIsOpen] = useState(false);
  const [confirmationPopupMsg, setConfirmationPopupMsg] = useState(null);
  const [hoverPopupIsOpen, setHoverPopupIsOpen] = useState(false);
  const stateResetRef = useRef(null);

  const delayClosePopup = () => {
    if (stateResetRef.current) {
      clearTimeout(stateResetRef.current);
    }
    stateResetRef.current = setTimeout(() => {
      setConfirmationPopupIsOpen(false);
      setConfirmationPopupMsg(null);
      setHoverPopupIsOpen(false);
    }, 1500);
  };

  const onCopy = () => {
    setConfirmationPopupIsOpen(true);
    setConfirmationPopupMsg(i18next.t("Copied!"));
    delayClosePopup();
  };

  const hoverStateHandler = (event) => {
    if (event.type === "mouseenter") setHoverPopupIsOpen(true);
    if (event.type === "mouseleave") setHoverPopupIsOpen(false);
  };

  return (
    text && (
      <Popup
        role="alert"
        open={hoverPopupIsOpen || confirmationPopupIsOpen}
        content={confirmationPopupMsg || i18next.t("Copy to clipboard")}
        inverted={!!confirmationPopupMsg}
        position={popUpPosition}
        size="mini"
        trigger={
          <SimpleCopyButton
            text={text}
            onCopy={onCopy}
            hoverState={hoverStateHandler}
          />
        }
      />
    )
  );
}

CopyButton.propTypes = {
  popUpPosition: PropTypes.string,
  text: PropTypes.string,
};
