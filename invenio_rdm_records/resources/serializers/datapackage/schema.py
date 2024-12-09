# -*- coding: utf-8 -*-
#
# Copyright (C) 2024 Open Knowledge Foundation
#
# Invenio-RDM-Records is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Data Package based Schema for Invenio RDM Records."""

from marshmallow import Schema, fields, missing

PROFILE_URL = "https://datapackage.org/profiles/2.0/datapackage.json"


class DataPackageSchema(Schema):
    """Schema for Data Package in JSON."""

    profile = fields.Constant(PROFILE_URL, data_key="$schema")

    id = fields.Str(attribute="links.doi")
    name = fields.Str(attribute="id")
    title = fields.Str(attribute="metadata.title")
    description = fields.Str(attribute="metadata.description")
    version = fields.Str(attribute="metadata.version")
    created = fields.Str(attribute="created")
    homepage = fields.Str(attribute="links.self_html")
    keywords = fields.Method("get_keywords")
    resources = fields.Method("get_resources")
    licenses = fields.Method("get_licenses")
    contributors = fields.Method("get_contributors")

    def get_keywords(self, obj):
        """Get keywords."""
        keywords = []
        for subject in obj.get("metadata", {}).get("subjects", []):
            keyword = subject.get("subject")
            if keyword:
                keywords.append(keyword)
        return keywords if keywords else missing

    def get_resources(self, obj):
        """Get resources."""
        resources = []
        basepath = obj.get("links", {}).get("self_html")
        if basepath:
            for file in obj.get("files", {}).get("entries", {}).values():
                resource = {}
                resource["name"] = file.get("key")
                resource["path"] = f'{basepath}/files/{file.get("key")}'
                resource["format"] = file.get("ext")
                resource["mimetype"] = file.get("mimetype")
                resource["bytes"] = file.get("size")
                resource["hash"] = file.get("checksum")
                resource = {k: v for k, v in resource.items() if v is not None}
                if resource.get("name") and resource.get("path"):
                    resources.append(resource)
        return resources

    def get_licenses(self, obj):
        """Get licenses."""
        licenses = []
        for item in obj.get("metadata", {}).get("rights", []):
            license = {}
            license["name"] = item.get("id")
            license["path"] = item.get("link") or item.get("props", {}).get("url")
            license["title"] = item.get("title", {}).get("en")
            license = {k: v for k, v in license.items() if v is not None}
            if license.get("name"):
                licenses.append(license)
        return licenses if licenses else missing

    def get_contributors(self, obj):
        """Get contributors."""
        contributors = []
        for type in ["creator", "contributor"]:
            for item in obj.get("metadata", {}).get(f"{type}s", []):
                entity = item.get("person_or_org", {})
                parent = (item.get("affiliations") or [{}])[0]
                contributor = {}
                contributor["title"] = entity.get("name")
                contributor["givenName"] = entity.get("given_name")
                contributor["familyName"] = entity.get("family_name")
                contributor["roles"] = [item.get("role", {}).get("id", type)]
                contributor["organization"] = parent.get("name")
                contributor = {k: v for k, v in contributor.items() if v is not None}
                if contributor:
                    contributors.append(contributor)
        return contributors if contributors else missing
