from invenio_rdm_records.external_pids.providers import DataCite


class Providers:

    available_providers = {
        "datacite": DataCite
    }

    def __init__(self, providers):
        """."""
        self.available_providers = providers

    def list(self):
        """."""
        pass

