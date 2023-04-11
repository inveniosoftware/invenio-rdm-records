// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Item, Header, Radio } from "semantic-ui-react";
import { withState } from "react-searchkit";
import _get from "lodash/get";
import { FastField } from "formik";

export const LicenseResults = withState(
  ({ currentResultsState: results, serializeLicenses }) => {
    const serializeLicenseResult = serializeLicenses
      ? serializeLicenses
      : (result) => ({
          title: result.title_l10n,
          description: result.description_l10n,
          id: result.id,
        });
    return (
      <FastField name="selectedLicense">
        {({ form: { values, setFieldValue } }) => (
          <Item.Group>
            {results.data.hits.map((result) => {
              const title = result["title_l10n"];
              const description = result["description_l10n"];
              return (
                <Item
                  key={title}
                  onClick={() =>
                    setFieldValue("selectedLicense", serializeLicenseResult(result))
                  }
                  className="license-item mb-15"
                >
                  <Radio
                    checked={_get(values, "selectedLicense.title") === title}
                    onChange={() =>
                      setFieldValue("selectedLicense", serializeLicenseResult(result))
                    }
                    {...(!description && { className: "mt-0" })}
                  />
                  <Item.Content className="license-item-content">
                    <Header size="small" className="mt-0">
                      {title}
                    </Header>
                    {description && (
                      <Item.Description className="license-item-description">
                        {description}
                      </Item.Description>
                    )}
                  </Item.Content>
                </Item>
              );
            })}
          </Item.Group>
        )}
      </FastField>
    );
  }
);
