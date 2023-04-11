// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Container, Divider, Segment } from "semantic-ui-react";
import { Trans } from "react-i18next";

export const CommunitySelectionFooter = () => {
  return (
    <>
      <Divider hidden />
      <Container>
        <Segment textAlign="center">
          <p>
            <Trans>
              Did not find a community that fits you? Upload without a community or{" "}
              <a href="/communities/new">create your own.</a>
            </Trans>
          </p>
        </Segment>
      </Container>
    </>
  );
};
