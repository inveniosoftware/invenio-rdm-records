/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { jsonFileFormat } from "./json";
import {
  createCreatibutorFileFormatRegistry,
  DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER,
  getCreatibutorFileFormats,
  registerCreatibutorFileFormat,
  unregisterCreatibutorFileFormat,
} from "./index";

const customFormat = {
  id: "custom",
  label: "Custom",
  extension: "CUSTOM",
  parse: () => [],
};

// Each test uses its own registry, so the suite does not depend on the order
// its tests run in.
const createRegistry = () => {
  const registry = createCreatibutorFileFormatRegistry();
  registry.register(jsonFileFormat);
  return registry;
};

describe("creatibutor file format registry", () => {
  it("registers JSON in the default registry", () => {
    expect(getCreatibutorFileFormats()).toEqual([
      expect.objectContaining({ id: "json", extension: ".json", order: 100 }),
    ]);
  });

  it("normalizes the extension of a registered format", () => {
    const registry = createRegistry();

    expect(registry.register(customFormat).extension).toBe(".custom");
    expect(registry.getFormats()).toContainEqual(
      expect.objectContaining({ id: "custom", extension: ".custom" })
    );
  });

  it("defaults the order of a format that does not set one", () => {
    const registry = createRegistry();

    expect(registry.register(customFormat).order).toBe(
      DEFAULT_CREATIBUTOR_FILE_FORMAT_ORDER
    );
  });

  it("rejects registering a format with an already registered id", () => {
    const registry = createRegistry();
    const registered = registry.register(customFormat);

    expect(() =>
      registry.register({
        ...customFormat,
        label: "Updated custom",
        extension: ".other",
      })
    ).toThrow(
      'Cannot register the creatibutor file format "custom": a format with this id is already registered.'
    );
    expect(registry.getFormats().map(({ id }) => id)).toEqual(["json", "custom"]);
    expect(registry.getFormats()[1]).toBe(registered);
  });

  it("rejects an incomplete format descriptor", () => {
    const registry = createRegistry();

    expect(() =>
      registry.register({ id: "broken", label: "Broken", extension: ".x" })
    ).toThrow(/requires a non-empty id, label, extension and a parse function/);
    expect(registry.getFormats()).toHaveLength(1);
  });

  it("rejects a non-numeric order", () => {
    const registry = createRegistry();

    expect(() => registry.register({ ...customFormat, order: "first" })).toThrow(
      'The order of the creatibutor file format "custom" must be a finite number.'
    );
  });

  it("rejects a second format for an already registered extension", () => {
    const registry = createRegistry();

    expect(() =>
      registry.register({ ...customFormat, id: "json_too", extension: "JSON" })
    ).toThrow(
      'Cannot register the creatibutor file format "json_too": the extension ' +
        '".json" is already used by "json".'
    );
    expect(registry.getFormats().map(({ id }) => id)).toEqual(["json"]);
  });

  it("offers formats by order, then by registration order", () => {
    const registry = createRegistry();
    registry.register({
      ...customFormat,
      id: "before",
      extension: ".before",
      order: 80,
    });
    registry.register({
      ...customFormat,
      id: "after",
      extension: ".after",
      order: 110,
    });
    registry.register({
      ...customFormat,
      id: "also_after",
      extension: ".also",
      order: 110,
    });

    expect(registry.getFormats().map(({ id }) => id)).toEqual([
      "before",
      "json",
      "after",
      "also_after",
    ]);
  });

  it("removes a format and returns it", () => {
    const registry = createRegistry();
    registry.register(customFormat);

    expect(registry.unregister("custom")).toEqual(
      expect.objectContaining({ id: "custom" })
    );
    expect(registry.getFormats().map(({ id }) => id)).toEqual(["json"]);
  });

  it("rejects removing an unknown format", () => {
    const registry = createRegistry();

    expect(() => registry.unregister("unknown")).toThrow(
      'No creatibutor file format is registered with the id "unknown".'
    );
  });

  it("allows registering a format again after removal", () => {
    const registry = createRegistry();
    registry.register(customFormat);
    registry.unregister("custom");

    expect(registry.register(customFormat).id).toBe("custom");
    expect(registry.getFormats()).toHaveLength(2);
  });

  it("returns a copy of the list with frozen formats", () => {
    const registry = createRegistry();
    const format = registry.register(customFormat);

    registry.getFormats().push(customFormat);

    expect(registry.getFormats()).toHaveLength(2);
    expect(Object.isFrozen(format)).toBe(true);
  });

  it("keeps registries independent of each other", () => {
    createRegistry().register(customFormat);

    expect(getCreatibutorFileFormats().map(({ id }) => id)).toEqual(["json"]);
  });

  it("returns an empty list when the default registry has no format", () => {
    unregisterCreatibutorFileFormat("json");
    try {
      expect(getCreatibutorFileFormats()).toEqual([]);
    } finally {
      registerCreatibutorFileFormat(jsonFileFormat);
    }
    expect(getCreatibutorFileFormats()).toHaveLength(1);
  });
});
