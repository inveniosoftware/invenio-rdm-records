"""Example of a record draft API."""

from invenio_communities.records.records.systemfields import CommunitiesField
from invenio_records.systemfields import ConstantField
from invenio_records_resources.records import Record as RecordBase
from invenio_records_resources.records.systemfields import IndexField

from .models import MockRecordCommunity, MockRecordMetadata


class MockRecord(RecordBase):
    """Example parent record."""

    # Configuration
    model_cls = MockRecordMetadata

    # System fields
    schema = ConstantField("$schema", "local://mocks/mock-v1.0.0.json")

    index = IndexField("mocks-mock-v1.0.0", search_alias="mocks")

    communities = CommunitiesField(MockRecordCommunity)

    # request = CommunityRequestField(model=MockRequestCommunity)
