from invenio_records_resources.services.base.results import \
    ServiceItemResult

class OAISetItem(ServiceItemResult):
    def __init__(self, service, identity, set, links_tpl, schema=None):
        self._identity = identity
        self._set = set
        self._schema = schema or service.schema
        self._links_tpl = links_tpl
        self._data = None


    @property
    def links(self):
        """Get links for this result item."""
        return self._links_tpl.expand(self._set)

    @property
    def data(self):
        """Property to get the record."""
        if self._data:
            return self._data

        self._data = self._schema.dump(
            self._set,
            context=dict(
                identity=self._identity,
            )
        )
        if self._links_tpl:
            self._data["links"] = self.links

        return self._data

    def to_dict(self):
        """Get a dictionary for the set."""
        res = self.data
        return res
