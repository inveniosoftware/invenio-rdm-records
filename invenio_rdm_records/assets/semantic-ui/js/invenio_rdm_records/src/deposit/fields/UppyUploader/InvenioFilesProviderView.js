// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import * as React from "react";
import ProviderView from "@uppy/provider-views/lib/ProviderView";
import Browser from "@uppy/provider-views/lib/Browser";
import CloseWrapper from "@uppy/provider-views/lib/CloseWrapper";

const defaultOptions = {
  viewType: "list",
  showTitles: true,
  showFilter: true,
  showBreadcrumbs: false,
  loadAllFiles: false,
};

export class InvenioFilesProviderView extends ProviderView {
  static VERSION = "0.0.2";

  /**
   * @param {object} plugin instance of the plugin
   * @param {object} opts
   */
  constructor(plugin, opts) {
    super(plugin, { ...defaultOptions, ...opts });

    this.render = this.render.bind(this);
  }

  render(state, viewOptions = {}) {
    const { didFirstRender } = this.plugin.getPluginState();
    const { i18n } = this.plugin;

    if (!didFirstRender) {
      this.preFirstRender();
    }

    const targetViewOptions = { ...this.opts, ...viewOptions };
    const { files, loading, currentSelection } = this.plugin.getPluginState();
    const { isChecked, toggleCheckbox, recordShiftKeyPress } = this;

    const browserProps = {
      isChecked,
      toggleCheckbox,
      recordShiftKeyPress,
      currentSelection,
      files: files,
      folders: [],
      done: this.donePicking,
      cancel: this.cancelPicking,

      headerComponent: "blah",
      noResultsLabel: i18n("noSearchResults"),
      title: this.plugin.title,
      viewType: targetViewOptions.viewType,
      showTitles: targetViewOptions.showTitles,
      showFilter: targetViewOptions.showFilter,
      isLoading: loading,
      showBreadcrumbs: targetViewOptions.showBreadcrumbs,
      pluginIcon: this.plugin.icon,
      i18n,
      uppyFiles: this.plugin.uppy.getFiles(),
      validateRestrictions: (...args) => this.plugin.uppy.validateRestrictions(...args),
      loadAllFiles: this.opts.loadAllFiles,
    };

    return (
      <CloseWrapper onUnmount={this.resetPluginState}>
        {/* eslint-disable-next-line react/jsx-props-no-spreading */}
        <Browser {...browserProps} />
      </CloseWrapper>
    );
  }
}

export default InvenioFilesProviderView;
