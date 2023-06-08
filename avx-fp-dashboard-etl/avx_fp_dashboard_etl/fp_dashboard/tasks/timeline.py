from datetime import datetime
import traceback

from avx_fp_dashboard_etl.fp_dashboard.models import Timeline
from avx_fp_dashboard_etl.fp_dashboard.constants import TimelineStatus, WorkItemStatus, BPMStatus, \
    completed_timeline_status
import logging

logger = logging.getLogger(__name__)


class TimeLineTasks:
    @classmethod
    def create(cls, work_item_obj, timeline_details, bpm_status):
        timeline_status = timeline_details.get('timeline_status', None)
        if not timeline_status:
            return None, 'Failed', False

        timeline_obj, is_created = cls.get_or_create(timeline_details=timeline_details, work_item_obj=work_item_obj,
                                                     bpm_status=bpm_status)

        if is_created:
            # Mark is_updated true here as there is an update for the work item and it has to be notifed to the user
            work_item_obj.has_updates = True
            work_item_obj.save()
            return timeline_obj, 'Insertion', True

        if not timeline_obj:
            return None, 'Failed', False

        return timeline_obj, 'Nothing', True

    @staticmethod
    def get_or_create(work_item_obj, timeline_details, bpm_status):
        try:
            current_timeline_status = timeline_details['timeline_status']
            current_timeline_updated_at = timeline_details['last_updated_at']
            is_archive_needed = timeline_details.get('is_archive_needed', False)
            """
                Whenever the data is being ingested for the first time, 
                we know there will not be any info regarding its prev state.
                Hence, if the current timeline status is ahead of initial ones, 
                we back fill the prev timeline status so that in the work items view, we can see the timeline history.   
                created_at is the date when the record was added to FP Dashboard data. 
                last_updated_at holds the workitem updated time.
            """
            existing_timelines = work_item_obj.timeline_set.count()
            if not existing_timelines:
                if current_timeline_status != TimelineStatus.REQUEST_SUBMITTED_BY_FP:
                    defaults = {
                        'created_at': datetime.now(),
                        'last_updated_at': current_timeline_updated_at,
                        'work_item_status': WorkItemStatus.IN_REVIEW,
                        'bpm_status': "Timeline Backfilled by ETL Script",
                        'is_archived': False,
                    }
                    Timeline.get_or_create(work_item=work_item_obj, title=TimelineStatus.REQUEST_SUBMITTED_BY_FP,
                                           defaults=defaults)

                    if current_timeline_status in completed_timeline_status:
                        Timeline.get_or_create(work_item=work_item_obj,
                                               title=TimelineStatus.IN_REVIEW_WITH_AVANTAX_TEAM,
                                               last_updated_at=current_timeline_updated_at,
                                               defaults=defaults)

            """
                Timeline Insertion Logic
                
                - We need to create a timeline record with relevant title and this is obtained from the nfs_bpm_timeline_data_mapping table
                - If bpm status is response received there are two special conditions to be followed                
                     1) If work item is already completed, we need to move back to IN-REVIEW state.
                         - Re-open the work item by moving it to in-review status
                         - Archive all previous timeline status except Request Submitted By FP
                         - Create a new timeline entry with IN_REVIEW_WITH_AVANTAX_TEAM
                         
                     2) If work item is already in IN_REVIEW_WITH_AVANTAX_TEAM, 
                        just add REQUEST RE-SUBMITTED as sub timeline and move back to IN-REVIEW state
                        - Get/Create a timeline entry with title IN_REVIEW_WITH_AVANTAX_TEAM
                        - Return this timeline entry under which REQUEST RE-SUBMITTED subtimeline will be added
                        - Create a additional new timeline with IN_REVIEW_WITH_AVANTAX_TEAM indicating                
            """
            # else if RESPONSE_RECEIVED
            if is_archive_needed:
                ordered_timeline = reversed(work_item_obj.timeline_set)

                for prev_timeline in ordered_timeline:
                    prev_timeline_status = prev_timeline.title
                    # Do not set is_archived to True if it is REQUEST_SUBMITTED_BY_FP
                    if prev_timeline_status == TimelineStatus.REQUEST_SUBMITTED_BY_FP:
                        continue

                    # If it is already archived, ignore and continue
                    if prev_timeline.is_archived:
                        continue

                    # Archive the timeline
                    prev_timeline.is_archived = True
                    prev_timeline.save()

                    # Remove the completed at time as it is now going to be in in-review with avantax state
                    work_item_obj.completed_at = None
                    work_item_obj.save()

                    for prev_sub_timeline in prev_timeline.subtimeline_set:
                        prev_sub_timeline.is_archived = True
                        prev_sub_timeline.save()

                    continue

            # Now insert this new record
            defaults = {
                'created_at': datetime.now(),
                'description': timeline_details['timeline_notes'],
                'last_updated_at': current_timeline_updated_at,
                'work_item_status': work_item_obj.status,
                'bpm_status': bpm_status,
                'is_archived': False
            }
            defaults = {key: value for key, value in defaults.items()}
            timeline_obj, created = Timeline.get_or_create(work_item=work_item_obj,
                                                           title=current_timeline_status,
                                                           is_archived=False,
                                                           defaults=defaults)

            if bpm_status == BPMStatus.RESPONSE_RECEIVED and not is_archive_needed:
                Timeline.create(work_item=work_item_obj,
                                title=TimelineStatus.IN_REVIEW_WITH_AVANTAX_TEAM,
                                bpm_status=BPMStatus.RESPONSE_RECEIVED,
                                work_item_status=work_item_obj.status,
                                is_archived=False,
                                created_at=datetime.now(),
                                last_updated_at=current_timeline_updated_at,
                                description=timeline_details['timeline_notes'])

            return timeline_obj, created

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            return None, False
