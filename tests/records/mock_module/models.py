"""Example of a record/community model."""

from invenio_db import db
from invenio_records.models import RecordMetadataBase

from invenio_rdm_records.records.models import CommunityRelationMixin


class MockRecordMetadata(db.Model, RecordMetadataBase):
    """A baisc record."""

    __tablename__ = "mock_metadata"


class MockRecordCommunity(db.Model, CommunityRelationMixin):
    """Relationship between record and community."""

    __tablename__ = "mock_community"
    __record_model__ = MockRecordMetadata
