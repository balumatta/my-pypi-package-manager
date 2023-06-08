from avx_fp_dashboard_etl.fp_dashboard.models import BPMWorkItemTimelineStatusMapping, Status, WorkItem
from avx_fp_dashboard_etl.bpm_data.models import NfsBpmInProgressItems, Client, FinancialProfessional
from avx_fp_dashboard_etl.fp_dashboard.tasks.timeline import TimeLineTasks
from avx_fp_dashboard_etl.fp_dashboard.constants import *
from avx_fp_dashboard_etl.fp_dashboard.tasks.work_item import WorkItemTasks
from avx_fp_dashboard_etl.fp_dashboard.tasks.sub_timeline import SubTimeLineTasks
from avx_fp_dashboard_etl.fp_dashboard.tasks.utils import TimeEstimation
from avx_fp_dashboard_etl.fp_dashboard.tasks.client import ClientTasks
from avx_fp_dashboard_etl.fp_dashboard.tasks.user import UserTasks

from pprint import pprint
from datetime import datetime

import logging

logger = logging.getLogger(__name__)


class Ingestion:
    def __init__(self):
        self.report = {
            'WorkItem': {
                'Insertion': [],
                'Updation': [],
                'Failed': [],
                'Missing Info': [],
                'Nothing': [],
            },
            'TimeLine': {
                'Insertion': [],
                'Updation': [],
                'Failed': [],
                'Missing Info': [],
                'Nothing': []
            },
            'Sub TimeLine': {
                'Insertion': [],
                'Updation': [],
                'Failed': [],
                'Missing Info': [],
                'Nothing': []
            },
            'Client': {
                'Insertion': [],
                'Updation': [],
                'Failed': [],
                'Missing Info': [],
                'Nothing': [],
            },
            'Advisor': {
                'Insertion': [],
                'Updation': [],
                'Failed': [],
                'Missing Info': [],
                'Nothing': [],
            },
            'Fin Rep': {
                'Insertion': [],
                'Updation': [],
                'Failed': [],
                'Missing Info': [],
                'Nothing': [],
            },
            'No Mapping': []
        }

        self.counter = 0

    def ingest_data(self):
        ########################### DATA EXTRACTION STARTS HERE ###########################
        all_bpm_inprogress_items = NfsBpmInProgressItems().get_all_data()
        ########################### DATA EXTRACTION ENDS HERE ###########################

        logger.info('Processing bpm work items')
        for bpm_in_progress_item in all_bpm_inprogress_items:
            ########################### DATA PROCESSING STARTS HERE ###########################
            if bpm_in_progress_item['item_type'] not in required_work_item_types:
                logger.info('Work item type is not in required types. So ignoring it.')
                logger.info(f'Work item number - {bpm_in_progress_item["work_item_number"]}')
                continue

            # self.counter += 1
            # logger.info(f'Index - {str(self.counter)}')
            # logger.info(f'Work item number - {bpm_in_progress_item["work_item_number"]}')

            bpm_item_details_dict = dict()

            # Extract the work item, timeline and other information to save further
            sponsor = bpm_in_progress_item['sponsor'].title() if bpm_in_progress_item['sponsor'] else ''
            line_of_business = bpm_in_progress_item['line_of_business']

            if line_of_business and line_of_business.lower() == 'brokerage':
                custodian = 'National Financial Services'
            elif sponsor and sponsor.strip('.').lower() == 'H.D. VEST':
                custodian = 'Avantax'
            else:
                custodian = sponsor

            bpm_item_details_dict['work_item_details'] = {
                'bpm_work_item_id': bpm_in_progress_item['work_item_number'],
                'request_type': bpm_in_progress_item['item_type'],
                'account_reg_type': bpm_in_progress_item['registration_type'],
                'account_number': bpm_in_progress_item['account_number'],
                'clearing_custodian': custodian,

                'created_at_in_bpm': bpm_in_progress_item['created_at_in_bpm'],
                'last_updated_at_in_bpm': bpm_in_progress_item['last_updated_at_in_bpm'],
                'last_updated_at_in_on_prem_db': bpm_in_progress_item['last_updated_at_in_on_prem_db'],
                'completed_at': bpm_in_progress_item['completed_at'],

                'avantax_advisor_id': bpm_in_progress_item['advisor_number'],
                'bpm_status': bpm_in_progress_item['status'],
                'current_queue': bpm_in_progress_item['current_queue'],
            }

            bpm_item_details_dict['user_details'] = {
                'nf_rep_code': bpm_in_progress_item['nf_rep_code'],
                'advisor_number': bpm_in_progress_item['advisor_number'],
            }

            bpm_status = bpm_item_details_dict['work_item_details']['bpm_status']
            bpm_work_item_id = bpm_item_details_dict['work_item_details']['bpm_work_item_id']
            bpm_status_obj = Status.get_or_none(Status.status == bpm_status)
            if not bpm_status_obj:
                self.report['No Mapping'].append(bpm_status)
                logger.info(
                    f"Item - {self.counter}; ALL - Operation : Failed; work item : {bpm_work_item_id}; "
                    f"BPM Status : {bpm_status}; Reason : Invalid status")
                continue

            status_mapping_obj = BPMWorkItemTimelineStatusMapping.get_or_none(bpm_status=bpm_status_obj)
            if not all([status_mapping_obj, status_mapping_obj.work_item_status, status_mapping_obj.timeline_status]):
                if not status_mapping_obj:
                    logger.info(f"Item - {self.counter}; ALL - Operation : Failed; "
                                f"work item : {bpm_work_item_id}; BPM Status : {bpm_status}; "
                                f"Reason : No mapping record found")

                if not status_mapping_obj.work_item_status:
                    self.report['WorkItem']['Missing Info'].append(bpm_status)
                    self.report['WorkItem']['Failed'].append(bpm_work_item_id)

                    logger.info(f"Item - {self.counter}; ALL - Operation : Failed; "
                                f"work item : {bpm_work_item_id}; BPM Status : {bpm_status}; "
                                f"Reason : Work item status mapping is None")

                if not status_mapping_obj.timeline_status:
                    self.report['TimeLine']['Missing Info'].append(bpm_status)
                    self.report['TimeLine']['Failed'].append(bpm_work_item_id)

                    logger.info(f"Item - {self.counter}; ALL - Operation : Failed; "
                                f"work item : {bpm_work_item_id}; BPM Status : {bpm_status}; "
                                f"Reason : Timeline status mapping is None")

                continue

            bpm_item_details_dict['work_item_details']['work_item_status'] = status_mapping_obj.work_item_status.status
            bpm_item_details_dict['work_item_details']['status_created_at'] = bpm_in_progress_item['last_updated_at_in_bpm']
            timeline_status = status_mapping_obj.timeline_status.status
            work_item_details = bpm_item_details_dict['work_item_details']

            if work_item_details['request_type'] in [WorkItemRequestTypes.MM_STANDING_INSTRUCTION,
                                                     WorkItemRequestTypes.MONEY_MOVEMENT]:
                if bpm_status == "IGO" and work_item_details['current_queue'] != "Cashiering Approvals":
                    work_item_details['work_item_status'] = WorkItemStatusConstants.COMPLETED
                    timeline_status = TimelineStatusConstants.ACCOUNT_SETUP_SUCCESSFUL

                if bpm_status == "Approved" and work_item_details['current_queue'] == "Cashiering Approvals":
                    work_item_details['work_item_status'] = WorkItemStatusConstants.COMPLETED
                    timeline_status = TimelineStatusConstants.ACCOUNT_SETUP_SUCCESSFUL

            elif work_item_details['request_type'] == WorkItemRequestTypes.INSURANCE:
                if bpm_status == BPMStatus.ARCHIVE_PENDING_COMPLETED:
                    work_item_details['work_item_status'] = WorkItemStatusConstants.COMPLETED
                    timeline_status = TimelineStatusConstants.ACCOUNT_SETUP_SUCCESSFUL

            """
                Whenever the timeline details are being ingested, 
                we calculate the respective timeline status using BPMWorkItemTimelineStatusMapping table.
    
                For MVP, we are currently storing nothing in  timeline_notes field.
    
                Sub-timeline Computation Logic For MVP
                If work_item status
                    - Non NIGO
                        Nothing, sub_timelines will be empty dict
                    - NIGO
                        sub_timeline info will be created as 
                        - nigo_reason will be sub_timeline title
                        - alert_memo will be sub_timeline description            
            """
            last_updated_at = bpm_in_progress_item['last_updated_at_in_bpm']
            if isinstance(bpm_in_progress_item['completed_at'], datetime):
                if bpm_in_progress_item['last_updated_at_in_bpm'] > bpm_in_progress_item['completed_at']:
                    last_updated_at = bpm_in_progress_item['completed_at']
                    bpm_item_details_dict['work_item_details']['last_updated_at_in_bpm'] = last_updated_at

            bpm_item_details_dict['timeline_details'] = {
                'timeline_status': timeline_status,
                'timeline_notes': None,
                'sub_timeline_details': {},
                'last_updated_at': last_updated_at,
                'is_archive_needed': False,
            }

            #  check if work item status is NIGO
            if bpm_item_details_dict['work_item_details']['work_item_status'] == WorkItemStatusConstants.NIGO:
                bpm_item_details_dict['timeline_details']['sub_timeline_details'] = {
                    'title': bpm_in_progress_item['nigo_reason'],
                    'description': bpm_in_progress_item['alert_memo'],
                    'last_updated_at': last_updated_at,
                }

            existing_work_item_obj = WorkItem.get_or_none(bpm_work_item_id=work_item_details['bpm_work_item_id'])
            if existing_work_item_obj:
                # Do not process if the work item status is already completed unless the bpm status is RESPONSE_RECEIVED
                if existing_work_item_obj.status == WorkItemStatusConstants.COMPLETED and bpm_status != BPMStatus.RESPONSE_RECEIVED:
                    logger.debug(f'Skipping as the work item is already completed and bpm status is not response '
                                 f'received. Work Item Id - {existing_work_item_obj.bpm_work_item_id}')
                    continue

                # skip if last status update time is same as that of now as there will not be any update to be made
                # This will save time and also avoid duplication record insertion in timeline and sub-timeline
                if existing_work_item_obj.last_updated_at_in_bpm and bpm_in_progress_item['last_updated_at_in_bpm']:
                    if existing_work_item_obj.last_updated_at_in_bpm == bpm_in_progress_item['last_updated_at_in_bpm']:
                        logger.debug(
                            f'Skipping as last record updated at for existing work item is same as current one. '
                            f'Work Item Id - {existing_work_item_obj.bpm_work_item_id}')
                        continue

                #  check if bpm status is Response Received
                if bpm_status == BPMStatus.RESPONSE_RECEIVED:
                    if existing_work_item_obj.status == WorkItemStatusConstants.COMPLETED:
                        bpm_item_details_dict['timeline_details']['is_archive_needed'] = True
                    else:
                        bpm_item_details_dict['timeline_details']['sub_timeline_details'] = {
                            'title': TimelineStatusConstants.REQUEST_RESUBMITTED_BY_FP,
                            'description': 'Thank you for re-submitting the request. '
                                           'Our team is currently reviewing all the details of the request '
                                           'and will be able to assist you shortly.',
                            'last_updated_at': last_updated_at,
                        }

            ########################### DATA PROCESSING ENDS HERE ###########################

            ########################### DATA INGESTION STARTS HERE ###########################
            work_item_details = bpm_item_details_dict['work_item_details']
            timeline_details = bpm_item_details_dict['timeline_details']
            self.check_assets_ready_logic_for_toa_items(work_item_details, timeline_details)

            # ingest work item data
            work_item_obj = self.ingest_work_item_info(work_item_details, bpm_work_item_id)
            # if work item ingestion fails, do not proceed. Process to the next item
            if not work_item_obj:
                continue

            # Ingest timeline data (by checking if item type is TOA)
            timeline_status = bpm_item_details_dict.get('timeline_details', {}).get('timeline_status', None)
            timeline_obj = self.ingest_timeline_info(timeline_status, timeline_details, work_item_obj, bpm_work_item_id,
                                                     bpm_status)

            # Ingest sub timeline data. (Only if sub timeline info and timeline details exists)
            if bpm_item_details_dict['timeline_details']['sub_timeline_details'] and timeline_obj:
                sub_timeline_details = bpm_item_details_dict['timeline_details']['sub_timeline_details']
                self.ingest_sub_timeline_info(sub_timeline_details, work_item_obj, timeline_obj, bpm_work_item_id)

            # Ingest Client data
            client_id = bpm_in_progress_item.get('client_id', None)
            client_obj = self.ingest_client_info(client_id, bpm_work_item_id, bpm_in_progress_item, work_item_obj)

            # ingest User/Finpro data
            """
                According to the latest discussion with Alan and Cesar on 25th Dec,
                AdvisorNumber is a rep id of the advisor and rep_code belongs to the same advisor.
                We will consider this advisor to be creator, submittor and also the main fin-pro under 
                whom the work-item shall be associated.
                
                AdvisorNumber - A number generated for each fin rep by Avantax
                NFRepCode - A 3-digit alphanumeric code generated by BPM            
                PS: Ignore repId in the nfs bpm table as we are not sure what it is.              
            """
            advisor_rep_number = bpm_item_details_dict['user_details']['advisor_number']
            advisor_obj = self.ingest_advisor_info(advisor_rep_number, bpm_work_item_id)

            # save the same advisor to the creator and submitter as of now for POC
            if advisor_obj:
                fin_rep = advisor = creator = submitter = advisor_obj
                work_item_obj.advisor = advisor
                work_item_obj.creator = creator
                work_item_obj.submitter = submitter
                work_item_obj.fin_rep = fin_rep
                work_item_obj.save()

            # rep_id = bpm_item_details_dict['user_details']['rep_id']
            # fin_rep_obj = self.ingest_rep_info(rep_id, bpm_work_item_id)
            # if not fin_rep_obj:
            #     fin_rep_obj = advisor_obj if advisor_obj else None
            #
            # # Save the fin rep object into work item object as well as in the client object.
            # work_item_obj.fin_rep = fin_rep_obj
            # work_item_obj.advisor = fin_rep_obj
            # work_item_obj.creator = fin_rep_obj
            # work_item_obj.submitter = fin_rep_obj

            # work_item_obj.save()

            if client_obj:
                client_obj.fin_rep = advisor_obj
                client_obj.save()

            ########################### DATA INGESTION ENDS HERE ###########################

    def ingest_work_item_info(self, work_item_details, bpm_work_item_id):
        work_item_obj, operation, is_success_work_item = WorkItemTasks.create_or_update(
            work_item_details=work_item_details)

        self.report['WorkItem'][operation].append(bpm_work_item_id)
        if operation in ['Failed'] or not is_success_work_item:
            logger.info(f"Item - {self.counter}; WORKITEM - Operation : {operation}; "
                        f"work item : {bpm_work_item_id}")
            return None

        return work_item_obj

    def check_assets_ready_logic_for_toa_items(self, work_item_details, timeline_details):
        """
            TOA LOGIC
            if work item request_type is TOA, check the current state of work item
            If Completed, we cannot directly consider it as completed. It should satisfy ACAT and NON ACAT condition

            So, for all TOA - COMPLETED work items,
                - first change the work_item status to IN_REVIEW & timeline_status to IN_REVIEW_WITH_AVANTAX_TEAM
                - Check for ACAT & NON ACAT status to mark as Assets Ready
                    - If condition satisfies, work item status shall be COMPLETED & timeline_status will be ASSETS READY
                    - Otherwise, it will remain in IN_REVIEW state
        """

        # If not TOA, return
        if work_item_details['request_type'] != WorkItemRequestTypes.TOA:
            return

        # If TOA and status is not Account Setup Successful, return
        if timeline_details['timeline_status'] != TimelineStatusConstants.ACCOUNT_SETUP_SUCCESSFUL:
            return

        # Else, If TOA and Account Setup Successful, process
        if work_item_details['work_item_status'] == WorkItemStatusConstants.COMPLETED:
            work_item_details['work_item_status'] = WorkItemStatusConstants.IN_REVIEW

        if timeline_details['timeline_status'] == TimelineStatusConstants.ACCOUNT_SETUP_SUCCESSFUL:
            timeline_details['timeline_status'] = TimelineStatusConstants.IN_REVIEW_WITH_AVANTAX_TEAM

        account_number = TimeEstimation.post_process_acc_num(work_item_details['account_number'])
        toa_details = TimeEstimation.toa_details(account_number=account_number)

        if any([toa_details['is_acat'] is True and toa_details['toa_status'] == 'SETTLE-CLOSE',
                not toa_details['is_acat'] is False and toa_details['toa_status'] == 'SETTLED']):
            timeline_details['timeline_status'] = TimelineStatusConstants.ASSETS_READY
            work_item_details['work_item_status'] = WorkItemStatusConstants.COMPLETED

    def ingest_timeline_info(self, timeline_status, timeline_details, work_item_obj, bpm_work_item_id, bpm_status):
        timeline_obj, operation, is_success_timeline = TimeLineTasks.create(timeline_details=timeline_details,
                                                                            work_item_obj=work_item_obj,
                                                                            bpm_status=bpm_status)

        self.report['TimeLine'][operation].append((bpm_work_item_id, timeline_status))
        if operation in ['Failed'] or not is_success_timeline:
            logger.debug(f"Item - {self.counter}; TIMELINE - Operation : {operation}; "
                         f"work item : {bpm_work_item_id}; timeline : {timeline_status}")
            return None

        return timeline_obj

    def ingest_sub_timeline_info(self, sub_timeline_details, work_item_obj, timeline_obj,
                                 bpm_work_item_id):
        sub_timeline_obj, operation, is_success_timeline = SubTimeLineTasks.create(work_item_obj, timeline_obj,
                                                                                   sub_timeline_details)

        sub_timeline_title = sub_timeline_details.get('title', None)
        self.report['Sub TimeLine'][operation].append((bpm_work_item_id, sub_timeline_title))
        if operation in ['Failed'] or not is_success_timeline:
            logger.debug(f"Item - {self.counter}; SUB TIMELINE - Operation : {operation}; "
                         f"work item : {bpm_work_item_id}; sub_timeline : {sub_timeline_title}")
            return None

        return sub_timeline_obj

    def ingest_rep_info(self, rep_id, bpm_work_item_id):
        fin_rep_details = FinancialProfessional().get_user_by_rep_id(rep_id)
        if not fin_rep_details:
            self.report['Fin Rep']['Missing Info'].append((bpm_work_item_id, rep_id))
            logger.debug(f'Fin rep details not found for work_item - {bpm_work_item_id} for rep id - {str(rep_id)}')
            return None

        logger.info(f'Processing fin rep details for rep id :: {rep_id}')
        fin_rep_obj, operation, is_success = UserTasks.create_or_update(user_details=fin_rep_details)
        self.report['Fin Rep'][operation].append((bpm_work_item_id, rep_id))
        if operation in ['Failed'] or not is_success:
            logger.debug(f"Item - {self.counter}; Fin Rep - Operation : {operation}; work item : {bpm_work_item_id};")
            return None

        return fin_rep_obj

    def ingest_advisor_info(self, rep_number, bpm_work_item_id):
        advisor_details = FinancialProfessional().get_user_by_rep_id(rep_number)
        if not advisor_details:
            self.report['Advisor']['Missing Info'].append((bpm_work_item_id, rep_number))
            logger.debug(
                f'Advisor details not found for work_item - {bpm_work_item_id} for rep number - {str(rep_number)}')
            return None

        logger.info(f'Processing advisor details for rep number :: {rep_number}')
        advisor_obj, operation, is_success = UserTasks.create_or_update(user_details=advisor_details)
        self.report['Advisor'][operation].append((bpm_work_item_id, rep_number))
        if operation in ['Failed'] or not is_success:
            logger.debug(f"Item - {self.counter}; Advisor - Operation : {operation}; work item : {bpm_work_item_id};")
            return None

        return advisor_obj

    def ingest_client_info(self, client_id, bpm_work_item_id, bpm_in_progress_item, work_item_obj):
        client_details = Client().get_client_by_id(client_id)
        if not any([client_details, bpm_in_progress_item['first_name'], bpm_in_progress_item['last_name']]):
            self.report['Client']['Missing Info'].append((bpm_work_item_id, client_id))
            logger.info(f'Client Details not found for work_item - {bpm_work_item_id} for client id - {str(client_id)}')
            return None

        if not client_details:
            client_details = {'client_id': client_id, 'client_type': None}

        # The first name and last name are obtained by nfs_bpm_inprogress_table
        client_details['first_name'] = bpm_in_progress_item['first_name']
        client_details['last_name'] = bpm_in_progress_item['last_name']
        client_details['household_name'] = bpm_in_progress_item['household_name'].lower() \
            if bpm_in_progress_item['household_name'] else None

        logger.info(f'Processing client details for id :: {client_id}')
        client_obj, operation, is_success = ClientTasks.create_or_update(client_details=client_details,
                                                                         work_item_obj=work_item_obj)
        self.report['Client'][operation].append((bpm_work_item_id, client_id))
        if operation in ['Failed'] or not is_success:
            logger.debug(f"Item - {self.counter}; CLIENT - Operation : {operation}; work item : {bpm_work_item_id};")
            return None

        return client_obj

    def print_report(self):
        self.report = {key: {
            'Insertion': len(value['Insertion']),
            'Updation': len(value['Updation']),
            'Failed': len(value['Failed']),
            'Nothing': len(value['Nothing']),
            'Missing Info': len(value['Missing Info'])
        } if key != 'No Mapping' else set(value) for key, value in self.report.items()}
        pprint(self.report)


if __name__ == '__main__':
    i = Ingestion()
    i.ingest_data()
    i.print_report()
