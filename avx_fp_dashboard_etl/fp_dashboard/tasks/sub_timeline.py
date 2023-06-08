from avx_fp_dashboard_etl.fp_dashboard.models import SubTimeline

from datetime import datetime
import traceback
import logging

logger = logging.getLogger(__name__)


class SubTimeLineTasks:
    @classmethod
    def create(cls, work_item_obj, timeline_obj, sub_timeline_details):
        sub_timeline_title = sub_timeline_details.get('title', None)
        if not sub_timeline_title:
            return None, 'Failed', False

        sub_timeline_obj, is_created = cls.get_or_create(sub_timeline_details=sub_timeline_details,
                                                         timeline_obj=timeline_obj)
        if is_created:
            # Mark is_updated true here as there is an update for the work item and it has to be notifed to the user
            work_item_obj.has_updates = True
            work_item_obj.save()
            return sub_timeline_obj, 'Insertion', True

        if not sub_timeline_obj:
            return None, 'Failed', False

        return sub_timeline_obj, 'Nothing', True

    @staticmethod
    def get_or_create(timeline_obj, sub_timeline_details):
        try:
            sub_timeline_title = sub_timeline_details['title']
            current_timeline_updated_at = sub_timeline_details['last_updated_at']

            # Now after ingesting all the previous timeline status, insert the current one
            defaults = {
                'created_at': datetime.now(),
                'initiated_by': None,
                'last_updated_at': current_timeline_updated_at,
                'work_item_status': timeline_obj.work_item.status,
                'is_archived': False
            }

            defaults = {key: value for key, value in defaults.items() if value}
            sub_timeline_obj, created = SubTimeline.get_or_create(timeline=timeline_obj,
                                                                  title=sub_timeline_title,
                                                                  description=sub_timeline_details['description'],
                                                                  defaults=defaults)

            return sub_timeline_obj, created
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            return None, False
