import traceback
from datetime import datetime

from avx_fp_dashboard_etl.fp_dashboard.constants import WorkItemStatus, BPMStatus
from avx_fp_dashboard_etl.fp_dashboard.models import WorkItem, RequestTypeTimelineMapping
from avx_fp_dashboard_etl.fp_dashboard.tasks.utils import TimeEstimation
from avx_fp_dashboard_etl.helpers.utils import datetime_equals
import logging

logger = logging.getLogger(__name__)


class WorkItemTasks:
    @classmethod
    def update(cls, work_item_details, work_item_obj):
        estimated_completion_time = TimeEstimation.get_estimated_time_completion(
            work_item_id=work_item_details['bpm_work_item_id'])
        estimated_toa_completion_time = TimeEstimation.get_toa_estimated_time_completion(
            work_item_id=work_item_details['bpm_work_item_id'])

        if not work_item_obj:
            return None, False

        try:
            is_updated = False

            if work_item_obj.request_type != work_item_details['request_type']:
                work_item_obj.request_type = work_item_details['request_type']
                is_updated = True

            if work_item_obj.account_number != work_item_details['account_number']:
                work_item_obj.account_number = work_item_details['account_number']
                is_updated = True

            if work_item_obj.clearing_custodian != work_item_details['clearing_custodian']:
                work_item_obj.clearing_custodian = work_item_details['clearing_custodian']
                is_updated = True

            if work_item_obj.status != work_item_details['work_item_status']:
                work_item_obj.status = work_item_details['work_item_status']
                is_updated = True

            if not datetime_equals(date1=work_item_obj.last_updated_at_in_bpm,
                                   date2=work_item_details['last_updated_at_in_bpm']):
                work_item_obj.last_updated_at_in_bpm = work_item_details['last_updated_at_in_bpm']
                is_updated = True

            if not datetime_equals(date1=work_item_obj.completed_at, date2=work_item_details['completed_at']):
                work_item_obj.completed_at = work_item_details['completed_at']
                is_updated = True

            if not datetime_equals(date1=work_item_obj.created_at_in_bpm,
                                   date2=work_item_details['created_at_in_bpm']):
                work_item_obj.created_at_in_bpm = work_item_details['created_at_in_bpm']
                is_updated = True

            if not datetime_equals(date1=work_item_obj.last_updated_at_in_on_prem_db,
                                   date2=work_item_details['last_updated_at_in_on_prem_db']):
                work_item_obj.last_updated_at_in_on_prem_db = work_item_details['last_updated_at_in_on_prem_db']
                is_updated = True

            if estimated_toa_completion_time and \
                    estimated_toa_completion_time != work_item_obj.est_completion_time_toa_in_days:
                work_item_obj.est_completion_time_toa_in_days = estimated_toa_completion_time
                is_updated = True

            if estimated_completion_time and \
                    estimated_completion_time != work_item_obj.est_completion_time_in_days:
                work_item_obj.est_completion_time_in_days = estimated_completion_time
                is_updated = True

            if is_updated:
                work_item_obj.last_updated_at = datetime.now()
                work_item_obj.save()

            return work_item_obj, is_updated

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            return None, False

    @classmethod
    def create_or_update(cls, work_item_details):
        if work_item_details['work_item_status'] == WorkItemStatus.COMPLETED and \
                work_item_details['completed_at'] is None:
            work_item_details['completed_at'] = work_item_details['last_updated_at_in_bpm']

        # get or create work item
        work_item_obj, is_created = cls.get_or_create(work_item_details=work_item_details)

        if is_created:
            # Mark is_updated true here as there is an update for the work item and it has to be notifed to the user
            work_item_obj.has_updates = True
            work_item_obj.save()
            return work_item_obj, 'Insertion', True

        work_item_obj, is_updated = cls.update(work_item_details=work_item_details, work_item_obj=work_item_obj)
        if is_updated:
            # Mark is_updated true here as there is an update for the work item and it has to be notifed to the user
            work_item_obj.has_updates = True
            work_item_obj.save()
            return work_item_obj, 'Updation', True

        if not work_item_obj:
            return None, 'Failed', False

        # was operation successful
        return work_item_obj, 'Nothing', True

    @staticmethod
    def get_estimated_time(request_type):
        mapping = RequestTypeTimelineMapping.get_or_none(request_type=request_type)
        if mapping:
            time_in_days = mapping.time_in_days
            return time_in_days

        return None

    @staticmethod
    def get_or_create(work_item_details):
        try:
            estimated_completion_time = TimeEstimation.get_estimated_time_completion(
                work_item_id=work_item_details['bpm_work_item_id'])
            estimated_toa_completion_time = TimeEstimation.get_toa_estimated_time_completion(
                work_item_id=work_item_details['bpm_work_item_id'])

            defaults = {
                'created_at': datetime.now(),
                'request_type': work_item_details['request_type'],
                'acc_registration_type': work_item_details['account_reg_type'],
                'creator': None,
                'submitter': None,
                'advisor': None,
                'account_number': work_item_details['account_number'],
                'clearing_custodian': work_item_details['clearing_custodian'],
                'status': work_item_details['work_item_status'],
                'labels': None,
                'last_updated_at': datetime.now(),
                'last_updated_at_in_bpm': work_item_details['last_updated_at_in_bpm'],
                'completed_at': work_item_details['completed_at'],
                'est_completion_time_in_days': estimated_completion_time,
                'est_completion_time_toa_in_days': estimated_toa_completion_time,
                'created_at_in_bpm': work_item_details['created_at_in_bpm'],
                'last_updated_at_in_on_prem_db': work_item_details['last_updated_at_in_on_prem_db'],
                'queue_entry_date': None,
                'current_queue': None
            }
            defaults = {key: value for key, value in defaults.items() if value}

            work_item, created = WorkItem.get_or_create(bpm_work_item_id=work_item_details['bpm_work_item_id'],
                                                        defaults=defaults)

            if not created:
                work_item.acc_registration_type = work_item_details['account_reg_type']
                work_item.save()

            return work_item, created
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            return None, False
