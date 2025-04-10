// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import * as React from "react";
import { UIPlugin } from "@uppy/core";
// import { ProviderViews } from "@uppy/provider-views";
// import { SearchProviderViews } from "@uppy/provider-views";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { InvenioFilesProviderView } from "./InvenioFilesProviderView";
import { h } from "preact";

const defaultOptions = {};

class InvenioClientProvider {
  constructor(uppy, opts) {
    this.provider = opts.provider;
    this.id = this.provider;
    this.username = undefined;
    this.files = opts.files || [];
    this.opts = opts;
  }

  list(directory, options) {
    return { username: this.username, nextPagePath: undefined, items: this.files };
  }
}

export class InvenioFilesProvider extends UIPlugin {
  static VERSION = "0.0.1";

  constructor(uppy, opts) {
    super(uppy, opts);
    this.type = "acquirer";
    this.id = this.opts.id || "InvenioFilesProvider";
    this.files = this.opts.files || [];
    this.icon = () => {
      return (
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 384 512"
          aria-hidden="true"
          height="2em"
        >
          <path d="M64 0C28.7 0 0 28.7 0 64V448c0 35.3 28.7 64 64 64H320c35.3 0 64-28.7 64-64V160H256c-17.7 0-32-14.3-32-32V0H64zM256 0V128H384L256 0zM216 232V334.1l31-31c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9l-72 72c-9.4 9.4-24.6 9.4-33.9 0l-72-72c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l31 31V232c0-13.3 10.7-24 24-24s24 10.7 24 24z" />
        </svg>
      );
    };

    this.provider = new InvenioClientProvider(uppy, {
      provider: this.id,
      pluginId: this.id,
      files: this.files,
    });

    // merge default options with the ones set by user
    this.opts = { ...defaultOptions, ...opts };

    this.i18nInit();
    this.title = i18next.t("Manage uploaded files");
    this.onFileRemoved = this.#deleteFile.bind(this);
  }

  #deleteFile(file, reason) {
    if (reason === "removed-by-user") {
      this.opts.deleteFile(file);
    }
  }

  install() {
    // this.view = new ProviderViews(this, {
    //   viewType: "list",
    //   showTitles: true,
    //   loadAllFiles: true,
    //   showBreadcrumbs: false,
    //   provider: this.provider,
    // });

    this.view = new InvenioFilesProviderView(this, {
      provider: this.provider,
      viewType: "list",
      showFilter: true,
    });

    this.uppy.on("file-removed", this.onFileRemoved);

    const { target } = this.opts;
    if (target) {
      this.mount(target, this);
    }
  }

  uninstall() {
    this.uppy.off("file-removed", this.onFileRemoved);
    this.view.tearDown();
    this.unmount();
  }

  onFirstRender() {
    return this.view.getFolder();
  }

  render(state) {
    return this.view.render(state);
  }
}

export default InvenioFilesProvider;
