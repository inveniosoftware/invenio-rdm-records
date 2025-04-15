// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
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
import { Icon } from "semantic-ui-react";

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

// TODO: this is a WIP to provide users with possibility
// to manually pick which individual files do they want to import from a record.
export class InvenioFilesProvider extends UIPlugin {
  static VERSION = "0.0.1";

  constructor(uppy, opts) {
    super(uppy, opts);
    this.type = "acquirer";
    this.id = this.opts.id || "InvenioFilesProvider";
    this.files = this.opts.files || [];
    this.icon = () => <Icon name="history" />;

    this.provider = new InvenioClientProvider(uppy, {
      provider: this.id,
      pluginId: this.id,
      files: this.files,
    });

    // merge default options with the ones set by user
    this.opts = { ...defaultOptions, ...opts };

    this.i18nInit();
    this.title = i18next.t("Previous version");
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

    const { target } = this.opts;
    if (target) {
      this.mount(target, this);
    }
  }

  uninstall() {
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
