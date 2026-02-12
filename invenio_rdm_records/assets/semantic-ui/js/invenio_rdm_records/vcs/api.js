// This file is part of InvenioRdmRecords
// Copyright (C) 2026 CERN.
//
// InvenioRDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
import $ from "jquery";

function addResultMessage(element, color, icon, message) {
  element.classList.remove("hidden");
  element.classList.add(color);
  element.querySelector(`.icon`).className = `${icon} small icon`;
  element.querySelector(".content").textContent = message;
}

// function from https://www.w3schools.com/js/js_cookies.asp
// We're keeping this old method of accessing cookies for now since the modern async
// CookieStore is not Baseline Widely Available (as of 2026-02, see https://developer.mozilla.org/en-US/docs/Web/API/CookieStore)
function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(";");
  for (let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) === " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) === 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

const REQUEST_HEADERS = {
  "Content-Type": "application/json",
  "X-CSRFToken": getCookie("csrftoken"),
};

export function sendEnableDisableRequest(checked, repo, communityId) {
  const input = repo.querySelector("input[data-repo-id]");
  const repoId = input.dataset["repoId"];
  const provider = input.dataset["provider"];
  const switchMessage = repo.querySelector(".repo-switch-message");

  let url;
  if (checked === true) {
    url = `/api/user/vcs/${provider}/repositories/${repoId}/enable`;
    if (communityId) {
      url += `?community_id=${communityId}`;
    }
  } else if (checked === false) {
    url = `/api/user/vcs/${provider}/repositories/${repoId}/disable`;
  }

  const request = new Request(url, {
    method: "POST",
    headers: REQUEST_HEADERS,
  });

  sendRequest(request);

  async function sendRequest(request) {
    try {
      const response = await fetch(request);
      if (response.ok) {
        addResultMessage(
          switchMessage,
          "positive",
          "checkmark",
          "Repository synced successfully. Please reload the page."
        );
        setTimeout(function () {
          switchMessage.classList.add("hidden");
        }, 10000);
      } else {
        addResultMessage(
          switchMessage,
          "negative",
          "cancel",
          `Request failed with status code: ${response.status}`
        );
        setTimeout(function () {
          switchMessage.classList.add("hidden");
        }, 5000);
      }
    } catch (error) {
      addResultMessage(
        switchMessage,
        "negative",
        "cancel",
        `There has been a problem: ${error}`
      );
      setTimeout(function () {
        switchMessage.classList.add("hidden");
      }, 7000);
    }
  }
}

// ON OFF toggle a11y
const $onOffToggle = $(".toggle.on-off-with-communities");

$onOffToggle &&
  $onOffToggle.on("change", (event) => {
    const target = $(event.target);
    const $onOffToggleCheckedAriaLabel = target.data("checked-aria-label");
    const $onOffToggleUnCheckedAriaLabel = target.data("unchecked-aria-label");
    if (event.target.checked) {
      target.attr("aria-label", $onOffToggleCheckedAriaLabel);
    } else {
      target.attr("aria-label", $onOffToggleUnCheckedAriaLabel);
    }
  });
