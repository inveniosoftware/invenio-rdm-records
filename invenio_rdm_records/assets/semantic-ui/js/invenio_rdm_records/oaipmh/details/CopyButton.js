/*
 * SPDX-FileCopyrightText: 2021 CERN.
 * SPDX-License-Identifier: MIT
 */

import { Component } from "react";
import PropTypes from "prop-types";
import { Button, Popup } from "semantic-ui-react";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { i18next } from "@translations/invenio_rdm_records/i18next";

function SimpleCopyButton({text, onCopy, hoverState = null}) {
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

export default function CopyButton({text = "", popUpPosition = "right center"}) {
  const onCopy = () => {
    this.setState(() => ({
      confirmationPopupIsOpen: true,
      confirmationPopupMsg: i18next.t("Copied!"),
    }));

    delayClosePopup();
  };

  const delayClosePopup = () => {
    let stateReset = setTimeout(() => {
      this.setState(INITIAL_STATE);
    }, 1500);

    this.setState({ stateReset });
  };

  const hoverStateHandler = (event) => {
    event.persist();
    if (event.type === "mouseenter") this.setState({ hoverPopupIsOpen: true });
    if (event.type === "mouseleave") this.setState({ hoverPopupIsOpen: false });
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

