// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2025 CERN.
// Copyright (C)      2025 CESNET.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.
//
// This file is an adaptation of:
// https://raw.githubusercontent.com/transloadit/uppy/refs/tags/%40uppy/locales%403.5.4/packages/%40uppy/locales/src/en_US.ts
// to integrate Uppy localization with Invenio"s i18next system.

import * as React from "react";
import { i18next } from "@translations/invenio_rdm_records/i18next";

function normalizeLanguageCode(code) {
  const langMapping = {
    ar: "ar_SA",
    bg: "bg_BG",
    ca: "ca_ES",
    cs: "cs_CZ",
    da: "da_DK",
    de: "de_DE",
    el: "el_GR",
    en: "en_US",
    // You can decide to map "es" to either "es_ES" or "es_MX"
    es: "es_ES",
    fa: "fa_IR",
    fi: "fi_FI",
    fr: "fr_FR",
    gl: "gl_ES",
    he: "he_IL",
    hi: "hi_IN",
    hr: "hr_HR",
    hu: "hu_HU",
    id: "id_ID",
    is: "is_IS",
    it: "it_IT",
    ja: "ja_JP",
    ko: "ko_KR",
    nb: "nb_NO",
    nl: "nl_NL",
    pl: "pl_PL",
    // You can decide to map "pt" to either "pt_BR" or "pt_PT"
    pt: "pt_BR",
    ro: "ro_RO",
    ru: "ru_RU",
    sk: "sk_SK",
    // You can decide to map "sr" to either "sr_RS_Latin" or "sr_RS_Cyrillic"
    sr: "sr_RS_Latin",
    sv: "sv_SE",
    th: "th_TH",
    tr: "tr_TR",
    uk: "uk_UA",
    uz: "uz_UZ",
    vi: "vi_VN",
    // You can decide to map "zh" to either "zh_CN" or "zh_TW"
    zh: "zh_CN",
    // Add more mappings as necessary and contribute to uppy:
    // https://uppy.io/docs/locales/#contributing-a-new-language
  };

  return code.length === 2 ? langMapping[code] : code.replace("-", "_");
}

const importLangPack = async (code) => {
  try {
    return await import(`@uppy/locales/lib/${code}.js`);
  } catch (e) {
    console.warn(`No Uppy locale found for ${code}, falling back to en_US`);
    return await import("@uppy/locales/lib/en_US.js");
  }
};

export function useUppyLocale() {
  const [locale, setLocale] = React.useState(null);
  const detectedLocale = i18next.language;

  React.useEffect(() => {
    const normalizedLangCode = normalizeLanguageCode(detectedLocale);

    importLangPack(normalizedLangCode).then((module) => {
      const localeData = module.default ?? module;
      setLocale(localeData);
    });
  }, [detectedLocale]);

  return locale;
}

export default useUppyLocale;
