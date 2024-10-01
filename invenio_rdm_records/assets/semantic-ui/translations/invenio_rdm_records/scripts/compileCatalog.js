// This file is part of InvenioRdmRecords
// Copyright (C) 2022 CERN.
// Copyright (C) 2024 KTH Royal Institute of Technology.
//
// Invenio RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

const { readFileSync, writeFileSync, existsSync } = require("fs");
const { gettextToI18next } = require("i18next-conv");

const PACKAGE_JSON_BASE_PATH = "./";
const { languages } = require(`../package`).config;

// it accepts the same options as the cli.
// https://github.com/i18next/i18next-gettext-converter#options
const options = {
  /* your options here */
};

function save(target) {
  return (result) => {
    writeFileSync(target, result);
  };
}

if ("lang" === process.argv[2]) {
  const lang = process.argv[3];
  const inputFilePath = `${PACKAGE_JSON_BASE_PATH}messages/${lang}/messages.po`;
  const outputFilePath = `${PACKAGE_JSON_BASE_PATH}messages/${lang}/translations.json`;

  if (existsSync(inputFilePath)) {
    gettextToI18next(lang, readFileSync(inputFilePath), options)
      .then(save(outputFilePath))
      .catch((err) => {
        console.error(`Error converting ${inputFilePath}:`, err);
      });
  } else {
    console.error(`File not found: ${inputFilePath} for language ${lang}`);
  }
} else {
  for (const lang of languages) {
    const inputFilePath = `${PACKAGE_JSON_BASE_PATH}messages/${lang}/messages.po`;
    const outputFilePath = `${PACKAGE_JSON_BASE_PATH}messages/${lang}/translations.json`;

    if (existsSync(inputFilePath)) {
      gettextToI18next(lang, readFileSync(inputFilePath), options)
        .then(save(outputFilePath))
        .catch((err) => {
          console.error(`Error converting ${inputFilePath}:`, err);
        });
    } else {
      console.error(`File not found: ${inputFilePath} for language ${lang}`);
    }
  }
}
