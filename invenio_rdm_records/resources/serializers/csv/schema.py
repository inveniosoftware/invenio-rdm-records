from commonmeta import doi_as_url
from invenio_communities import current_communities
from invenio_communities.communities.services.service import get_cached_community_slug
from marshmallow import Schema, fields, missing
from marshmallow_utils.fields import SanitizedHTML, SanitizedUnicode


class CSVSchema(Schema):
    id = SanitizedUnicode(attribute="")
    title = SanitizedUnicode(attribute="metadata.title")
    description = SanitizedHTML(attribute="metadata.description")
    access_right = fields.Method("get_access")
    # upload_type = SanitizedUnicode(attribute="")
    # image_type = SanitizedUnicode(attribute="")
    communities = fields.Method("get_communities")
    # publication_date = SanitizedUnicode(attribute="")
    # journal_title = SanitizedUnicode(attribute="")
    # journal_volume = SanitizedUnicode(attribute="")
    # journal_issue = SanitizedUnicode(attribute="")
    # journal_pages = SanitizedUnicode(attribute="")
    doi = fields.Method("get_id")
    # creators.name = SanitizedUnicode(attribute="")
    # creators.affiliation = SanitizedUnicode(attribute="")
    # creators.orcid = SanitizedUnicode(attribute="")
    # keywords = SanitizedUnicode(attribute="")
    # files = SanitizedUnicode(attribute="")
    # extra_formats = SanitizedUnicode(attribute="")
    # related_identifiers.identifier = SanitizedUnicode(attribute="")
    # related_identifiers.relation = SanitizedUnicode(attribute="")
    # custom.dwc:kingdom = SanitizedUnicode(attribute="")
    # custom.dwc:colectionCode = SanitizedUnicode(attribute="")

    def get_access(self, obj):
        """Get access rights."""
        # access = {"a": obj["access"]["record"]}
        # return access
        pub_date = obj.get("access", {}).get("record")
        # YYYY-MM-DD
        return pub_date or missing

    def _get_communities_slugs(self, ids):
        """Get communities slugs."""
        service_id = current_communities.service.id
        return [
            get_cached_community_slug(community_id, service_id) for community_id in ids
        ]

    def get_communities(self, obj):
        """Get communities."""
        ids = obj["parent"].get("communities", {}).get("ids", [])
        if not ids:
            return missing
        # Communities are prefixed with ``user-``
        return [{"a": f"user-{slug}"} for slug in self._get_communities_slugs(ids)]

    def get_date_released(self, obj):
        """Serialize release date."""
        pub_date = obj.get("metadata", {}).get("publication_date")
        # YYYY-MM-DD
        return pub_date or missing

    def get_id(self, obj):
        """Get id. Use the DOI expressed as a URL."""
        # doi = py_.get(obj, "pids.doi.identifier")
        doi = obj["pids"].get("doi", {}).get("identifier", [])
        if doi:
            return doi_as_url(doi)
        return missing
