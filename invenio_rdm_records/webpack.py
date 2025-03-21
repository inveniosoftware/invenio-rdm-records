# -*- coding: utf-8 -*-
#
# Copyright (C) 2019-2025 CERN.
# Copyright (C) 2019-2022 Northwestern University.
# Copyright (C)      2022 TU Wien.
# Copyright (C)      2022 Graz University of Technology.
#
# Invenio RDM Records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS Webpack bundles for theme."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "invenio-oai-pmh-details": "./js/invenio_rdm_records/oaipmh/details/index.js",
                "invenio-oai-pmh-search": "./js/invenio_rdm_records/oaipmh/search/index.js",
            },
            dependencies={
                "@babel/runtime": "^7.9.0",
                "@tinymce/tinymce-react": "^4.3.0",
                "formik": "^2.1.0",
                "i18next": "^20.3.0",
                "i18next-browser-languagedetector": "^6.1.0",
                "luxon": "^1.23.0",
                "path": "^0.12.7",
                "prop-types": "^15.7.2",
                "react-copy-to-clipboard": "^5.0.0",
                "react-dnd": "^11.1.0",
                "react-dnd-html5-backend": "^11.1.0",
                "react-dropzone": "^11.0.0",
                "react-i18next": "^11.11.0",
                "react-invenio-forms": "^4.6.0",
                "react-searchkit": "^3.0.0",
                "tinymce": "^6.7.2",
                "yup": "^0.32.0",
                "@semantic-ui-react/css-patch": "^1.0.0",
                "axios": "^1.7.7",
                "react": "^16.13.0",
                "react-dom": "^16.13.0",
                "react-redux": "^7.2.0",
                "redux": "^4.0.0",
                "redux-thunk": "^2.3.0",
                "lodash": "^4.17.0",
                "query-string": "^7.0.0",
                "semantic-ui-css": "^2.4.0",
                "semantic-ui-react": "^2.1.0",
            },
            aliases={
                # Define Semantic-UI theme configuration needed by
                # Invenio-Theme in order to build Semantic UI (in theme.js
                # entry point). theme.config itself is provided by
                # cookiecutter-invenio-rdm.
                "@js/invenio_rdm_records": "js/invenio_rdm_records",
                "@translations/invenio_rdm_records": "translations/invenio_rdm_records",
            },
        ),
    },
)
