from flask import current_app
from invenio_drafts_resources.services.records.components import ServiceComponent
from invenio_records_resources.services.files.processors import ProcessorRunner


class IIIFComponent(ServiceComponent):
    """Service component for IIIF."""

    def publish(self, identity, draft=None, record=None):
        """Publish handler."""

        # TODO Makes sense to add the below if we move it to records-resources/rdm-records
        iiif_generate_tiles = current_app.config.get("IIIF_GENERATE_TILES")
        if not iiif_generate_tiles:
            return
        for fname, file in draft.files.items():
            ProcessorRunner(self.service.config.file_processors).run(file, uow=self.uow)
