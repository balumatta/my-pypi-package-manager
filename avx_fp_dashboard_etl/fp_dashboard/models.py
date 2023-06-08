import uuid

from peewee import Model, IntegerField, CharField, BooleanField, DateTimeField, \
    ForeignKeyField, UUIDField, TextField, Proxy

import logging

logger = logging.getLogger(__name__)

fp_dashboard_connection = Proxy()  # will be initialised later


class FPDasboardModelsBaseClass(Model):
    record_id = UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = DateTimeField()
    last_updated_at = DateTimeField(null=True)

    class Meta:
        schema = 'fp_dashboard'
        database = fp_dashboard_connection


class User(FPDasboardModelsBaseClass):
    username = CharField()
    first_name = CharField()
    last_name = CharField()
    email = CharField()
    avantax_fp_id = CharField()
    nfs_rep_code = CharField()
    avantax_rep_id = CharField()

    password = CharField(null=True)
    last_login = DateTimeField(null=True)
    date_joined = DateTimeField()
    is_superuser = BooleanField(default=False)
    is_staff = BooleanField(default=False)
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'avx_financial_professional'


class Client(FPDasboardModelsBaseClass):
    avantax_client_id = CharField(null=True)
    household_name = CharField()
    first_name = CharField()
    last_name = CharField()
    client_type = CharField(null=True)
    client_type_code = CharField(null=True)
    fin_rep = ForeignKeyField(User, on_delete='CASCADE', null=True)

    class Meta:
        db_table = 'avx_client'


class WorkItem(FPDasboardModelsBaseClass):
    bpm_work_item_id = CharField(null=True)
    request_type = CharField(null=True)
    acc_registration_type = CharField(null=True)

    fin_rep = ForeignKeyField(User, on_delete='CASCADE', null=True)
    advisor = ForeignKeyField(User, on_delete='CASCADE', null=True)
    creator = ForeignKeyField(User, on_delete='CASCADE', null=True)
    submitter = ForeignKeyField(User, on_delete='CASCADE', null=True)

    account_number = CharField(null=True)
    clearing_custodian = CharField(null=True)
    status = CharField(null=True)
    labels = CharField(null=True)

    created_at_in_bpm = DateTimeField(null=True)
    last_updated_at_in_bpm = DateTimeField(null=True)
    completed_at = DateTimeField(null=True)
    last_updated_at_in_on_prem_db = DateTimeField(null=True)

    est_completion_time_in_days = IntegerField(null=True)
    est_completion_time_toa_in_days = IntegerField(null=True)
    queue_entry_date = DateTimeField(null=True)
    current_queue = CharField(null=True)
    has_updates = BooleanField(default=True)

    class Meta:
        db_table = 'avx_work_item'


class ClientWorkItemMapping(FPDasboardModelsBaseClass):
    client = ForeignKeyField(Client, on_delete='CASCADE')
    work_item = ForeignKeyField(WorkItem, on_delete='CASCADE')

    class Meta:
        db_table = 'avx_client_work_item_mapping'


class Timeline(FPDasboardModelsBaseClass):
    work_item = ForeignKeyField(WorkItem, on_delete='CASCADE')
    initiated_by = ForeignKeyField(User, on_delete='CASCADE')
    title = CharField(null=True)
    description = TextField(null=True)
    work_item_status = CharField(null=True)
    bpm_status = CharField(max_length=512, null=True)
    last_updated_at = DateTimeField()
    is_archived = BooleanField(null=True)

    class Meta:
        db_table = 'avx_timeline'


class SubTimeline(FPDasboardModelsBaseClass):
    timeline = ForeignKeyField(Timeline, on_delete='CASCADE')
    initiated_by = ForeignKeyField(User, on_delete='CASCADE')
    title = CharField(null=True)
    description = TextField(null=True)
    work_item_status = CharField(null=True)
    last_updated_at = DateTimeField()
    is_archived = BooleanField(null=True)

    class Meta:
        db_table = 'avx_sub_timeline'


class TimelineStatus(FPDasboardModelsBaseClass):
    status = CharField()

    class Meta:
        db_table = 'avx_timeline_status'


class WorkItemStatus(FPDasboardModelsBaseClass):
    status = CharField()

    class Meta:
        db_table = 'avx_work_item_status'


class Status(FPDasboardModelsBaseClass):
    status = CharField(max_length=512)
    source = CharField(max_length=512)

    class Meta:
        db_table = 'avx_status'


class BPMWorkItemTimelineStatusMapping(FPDasboardModelsBaseClass):
    bpm_status = ForeignKeyField(Status, on_delete='CASCADE')
    timeline_status = ForeignKeyField(TimelineStatus, on_delete='CASCADE', null=True)
    work_item_status = ForeignKeyField(WorkItemStatus, on_delete='CASCADE', null=True)

    class Meta:
        db_table = 'avx_bpm_workitem_timeline_status_mapping'


class RequestTypeTimelineMapping(FPDasboardModelsBaseClass):
    request_type = CharField(max_length=512)
    is_acat = BooleanField(null=True)
    time_in_days = IntegerField()

    class Meta:
        db_table = 'avx_requesttype_timeline_mapping'


if __name__ == '__main__':
    for each in RequestTypeTimelineMapping.select():
        logger.info(f"{each.request_type} {each.is_acat} {each.time_in_days}")
