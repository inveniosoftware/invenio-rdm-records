
class Client:

    name = ""


class Provider:

    name = ""
    client = None
    url = ""

    def __init__(self, client):
        """."""
        self.client = client

    def reserve(self):
        pass

    def register(self, record, identifier):
        pass

    def update(self, record, identifier):
        pass

    def unregister(self, identifier):
        pass

    def get_status(self, identifier):
        pass


class DataCiteClient(Client):

    name = "zenodo"
    username = ""
    password = ""


class DataCiteProvider(Provider):

    name = "datacite"

    def __init__(self, client):
        """."""
        self.client = client


