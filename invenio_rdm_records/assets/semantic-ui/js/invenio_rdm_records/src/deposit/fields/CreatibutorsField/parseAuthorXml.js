/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 * The format of xml follows https://github.com/inspirehep/author.xml
 */

import { CREATIBUTOR_TYPE } from "./type";

export const AUTHOR_XML_IDENTIFIER_SCHEMES = Object.freeze([
  "orcid",
  "gnd",
  "isni",
  "ror",
]);

const AUTHOR_LIST_ROOT_ELEMENT = "collaborationauthorlist";

const ELEMENT_NODE = 1;

const localName = (element) =>
  (element.localName || element.nodeName || "").toLowerCase();

const textOf = (element) => (element?.textContent ?? "").trim();

const childElements = (node) =>
  Array.from(node?.childNodes ?? []).filter((child) => child.nodeType === ELEMENT_NODE);

const childrenNamed = (node, ...names) => {
  const wanted = names.map((name) => name.toLowerCase());
  return childElements(node).filter((child) => wanted.includes(localName(child)));
};

const firstChildNamed = (node, ...names) => childrenNamed(node, ...names)[0] ?? null;

/**
 * `<cal:authorids>` and `<cal:authorAffiliations>` wrap the entries they hold.
 * Accept the entries nested (what author.xml does) as well as directly under
 * `<foaf:Person>`, as hand-written files tend to flatten them.
 */
const entriesOf = (node, containerName, entryName) => [
  ...childrenNamed(node, entryName),
  ...childrenNamed(firstChildNamed(node, containerName), entryName),
];

const indexElements = (node, index = new Map()) => {
  childElements(node).forEach((child) => {
    const name = localName(child);
    const elements = index.get(name);
    if (elements) {
      elements.push(child);
    } else {
      index.set(name, [child]);
    }
    indexElements(child, index);
  });
  return index;
};

const attributeOf = (element, name) => {
  if (!element) return null;
  const value = element.getAttribute(name);
  if (value !== null) return value;
  const wanted = name.toLowerCase();
  const match = Array.from(element.attributes ?? []).find(
    (attribute) =>
      attribute.name.toLowerCase() === wanted ||
      attribute.localName?.toLowerCase() === wanted
  );
  return match?.value ?? null;
};

const normalized = (value) => (value ?? "").trim();

const toSourceKey = (value) => normalized(value).toUpperCase();

const pick = (...values) => values.find((value) => value) ?? undefined;

// Resolve identifiers URLs if provided instead of bare ids.
const IDENTIFIER_URL_PREFIX =
  /^https?:\/\/(www\.)?(orcid\.org|isni\.org(\/isni)?|d-nb\.info\/gnd|ror\.org)\//i;

const normalizeIdentifier = (value) =>
  normalized(value)
    .replace(IDENTIFIER_URL_PREFIX, "")
    .replace(/^ror:/i, "")
    .replace(/\/+$/, "");

const normalizeRor = (value) => normalizeIdentifier(value) || null;

/**
 * Split a free-text name. From e.g. `<foaf:name>` or `<cal:authorNamePaper>`
 * into a given and family name.
 */
const splitName = (value) => {
  const name = normalized(value);
  if (!name) return {};
  const commaIndex = name.indexOf(",");
  if (commaIndex !== -1) {
    return {
      family_name: name.slice(0, commaIndex).trim() || undefined,
      given_name: name.slice(commaIndex + 1).trim() || undefined,
    };
  }
  const parts = name.split(/\s+/);
  if (parts.length === 1) return { family_name: parts[0] };
  return {
    given_name: parts.slice(0, -1).join(" "),
    family_name: parts[parts.length - 1],
  };
};

/**
 * Map the author's name, which the format distributes over up to five elements:
 * `<foaf:givenName>`/`<foaf:familyName>` (structured, `givenName` optional),
 * `<cal:authorNamePaperGiven>`/`<cal:authorNamePaperFamily>`
 * , `<foaf:name>` (free text, full names) and `<cal:authorNamePaper>` (free text, initials).
 */
const parseName = (personElement) => {
  const givenName = textOf(firstChildNamed(personElement, "givenname"));
  const familyName = textOf(firstChildNamed(personElement, "familyname"));
  if (givenName && familyName) {
    return { given_name: givenName, family_name: familyName };
  }

  const paperGiven = textOf(firstChildNamed(personElement, "authornamepapergiven"));
  const paperFamily = textOf(firstChildNamed(personElement, "authornamepaperfamily"));
  const freeText = splitName(textOf(firstChildNamed(personElement, "name")));
  const paperText = splitName(
    textOf(firstChildNamed(personElement, "authornamepaper"))
  );

  return {
    given_name: pick(givenName, freeText.given_name, paperGiven, paperText.given_name),
    family_name: pick(
      familyName,
      paperFamily,
      freeText.family_name,
      paperText.family_name
    ),
  };
};

const parseIdentifiers = (personElement) => {
  const identifiers = [];
  const seen = new Set();
  entriesOf(personElement, "authorids", "authorid").forEach((authorIdElement) => {
    const scheme = normalized(attributeOf(authorIdElement, "source")).toLowerCase();
    if (!AUTHOR_XML_IDENTIFIER_SCHEMES.includes(scheme)) return;
    const identifier = normalizeIdentifier(textOf(authorIdElement));
    if (!identifier) return;
    const key = `${scheme}:${identifier.toLowerCase()}`;
    if (seen.has(key)) return;
    seen.add(key);
    identifiers.push({ scheme, identifier });
  });
  return identifiers;
};

const organizationName = (organizationElement) =>
  textOf(firstChildNamed(organizationElement, "name")) || undefined;

const organizationRor = (organizationElement) => {
  for (const orgName of childrenNamed(organizationElement, "orgname")) {
    const source = toSourceKey(attributeOf(orgName, "source"));
    const value = textOf(orgName);
    if (source === "ROR" || (!source && /^ror:/i.test(value))) {
      const ror = normalizeRor(value);
      if (ror) return ror;
    }
  }
  return null;
};

/**
 * Map `<cal:organizations>` by `<foaf:Organization/@id>`, which is what
 * `<cal:authorAffiliation organizationid="…"/>` refers to.
 */
const parseOrganizations = (organizationElements) => {
  const organizations = new Map();
  organizationElements.forEach((organizationElement) => {
    const id = normalized(attributeOf(organizationElement, "id"));
    if (!id) return;
    organizations.set(id, {
      name: organizationName(organizationElement),
      ror: organizationRor(organizationElement),
    });
  });
  return organizations;
};

const parseAffiliations = (personElement, organizations) => {
  const affiliations = [];
  const seen = new Set();

  entriesOf(personElement, "authoraffiliations", "authoraffiliation").forEach(
    (affiliationElement) => {
      const organization = organizations.get(
        normalized(attributeOf(affiliationElement, "organizationid"))
      );
      if (!organization) return;
      const key = (organization.ror || organization.name || "").toLowerCase();
      if (!key || seen.has(key)) return;
      seen.add(key);
      const affiliation = {};
      if (organization.ror) affiliation.id = organization.ror;
      if (organization.name) affiliation.name = organization.name;
      affiliations.push(affiliation);
    }
  );

  return affiliations;
};

const parsePerson = (personElement, organizations) => {
  const name = parseName(personElement);
  if (!name.given_name && !name.family_name) return null;

  const personOrOrg = {
    type: CREATIBUTOR_TYPE.PERSON,
    ...name,
  };
  const identifiers = parseIdentifiers(personElement);
  if (identifiers.length > 0) personOrOrg.identifiers = identifiers;

  const entry = { person_or_org: personOrOrg };
  const affiliations = parseAffiliations(personElement, organizations);
  if (affiliations.length > 0) entry.affiliations = affiliations;
  return entry;
};

const parseXmlDocument = (text) => {
  if (typeof DOMParser === "undefined") return null;
  const document = new DOMParser().parseFromString(text, "application/xml");
  if (!document?.documentElement) return null;
  const elements = indexElements(document);
  // Browsers report malformed XML by embedding a `parsererror` element in the
  // resulting document instead of throwing.
  if (elements.has("parsererror")) return null;
  return { root: document.documentElement, elements };
};

/**
 * Parse `author.xml`, as specified in
 * https://github.com/inspirehep/author.xml into an array of creatibutors.
 *
 * @param {string} text - raw XML content of the author list
 * @returns {Array|null} the creatibutors, or `null` when the content is not a
 *   readable author list in XML format
 */
export const parseAuthorXml = (text) => {
  if (typeof text !== "string") return null;
  const parsed = parseXmlDocument(text);
  if (!parsed) return null;

  const { root, elements } = parsed;
  if (localName(root) !== AUTHOR_LIST_ROOT_ELEMENT) return null;

  const organizations = parseOrganizations(elements.get("organization") ?? []);

  return (elements.get("person") ?? [])
    .map((personElement) => parsePerson(personElement, organizations))
    .filter((entry) => entry !== null);
};
