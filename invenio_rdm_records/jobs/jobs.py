from invenio_jobs.jobs import JobType

from invenio_rdm_records.services.tasks import update_expired_embargos

update_expired_embargos_cls = JobType.create(
    arguments_schema=None,
    job_cls_name="UpdateEmbargoesJob",
    id_="update_expired_embargos",
    task=update_expired_embargos,
    description="Updates expired embargos",
    title="Update expired embargoes"
)
