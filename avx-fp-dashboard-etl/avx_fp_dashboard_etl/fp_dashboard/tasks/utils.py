from avx_fp_dashboard_etl.bpm_data.models import NFS_TransferOfAssets, NfsBpmInProgressItems
from avx_fp_dashboard_etl.fp_dashboard.constants import WorkItemRequestTypes


class TimeEstimation:
    @staticmethod
    def toa_details(account_number):
        toa_item = NFS_TransferOfAssets.get_or_none(AccountNumber=account_number)
        # check for a child item/items in the TOA table
        if toa_item:
            if toa_item.TransferType == 'ACAT':
                return {
                    'is_acat': True,
                    'is_toa': True,
                    'toa_status': toa_item.TOA_Status
                }
            else:
                return {
                    'is_acat': False,
                    'is_toa': True,
                    'toa_status': toa_item.TOA_Status
                }

        return {
            'is_acat': None,
            'is_toa': False,
            'toa_status': None
        }

    @staticmethod
    def post_process_acc_num(account_number):
        # add a hyphen between the first three letters and last set of letters
        # Eg : HVA023752 becomes HVA-023752
        if not isinstance(account_number, str):
            return account_number

        if len(account_number) < 3:
            return account_number

        account_number = account_number[0:3] + '-' + account_number[3:]
        return account_number

    @classmethod
    def get_toa_estimated_time_completion(cls, work_item_id):
        work_item = NfsBpmInProgressItems.get_or_none(WorkItemNumber=work_item_id)
        account_number = cls.post_process_acc_num(work_item.AccountNumber)

        toa_details = cls.toa_details(account_number=account_number)
        additional_days = None

        if toa_details['is_toa'] and toa_details['is_acat']:
            additional_days = 7

        elif toa_details['is_toa'] and not toa_details['is_acat']:
            additional_days = 30

        return additional_days

    @classmethod
    def get_estimated_time_completion(cls, work_item_id):

        work_item = NfsBpmInProgressItems.get_or_none(WorkItemNumber=work_item_id)

        if not work_item:
            return None

        request_type = work_item.ItemType
        origin = work_item.Origin
        money_type = work_item.MoneyType

        if request_type == WorkItemRequestTypes.ACCOUNT_MAINTENANCE:
            return 3
        elif request_type == WorkItemRequestTypes.NEW_ACCOUNTS:
            return 6
        elif request_type == WorkItemRequestTypes.ADVISORY_NEW_ACCOUNTS:
            return 6
        elif request_type == WorkItemRequestTypes.MM_STANDING_INSTRUCTION:
            # TODO - need to add the number of stall days
            # if currentQueue = "cashiering approvals"
            #     require client consent and the time estimation will need to be paused
            # else:
            #     3 days needed
            return 3
        elif request_type == WorkItemRequestTypes.MONEY_MOVEMENT:
            # TODO - need to add the number of stall days
            # if currentQueue = "cashiering approvals"
            #     require client consent and the time estimation will need to be paused
            # else:
            #     1 days needed

            return 1
        elif request_type == WorkItemRequestTypes.ADVISORY_MAINTENANCE:
            return 3
        elif request_type == WorkItemRequestTypes.DIRECT_ANNUITIES:
            # if Origin=='Hard Copy' and MoneyType=='money'
            #     2 days needed
            # else:
            #     same day
            if origin == 'ELECTRONIC':
                return 2
            return 5
        elif request_type == WorkItemRequestTypes.CHECK_DEPOSIT:
            if origin == 'HARDCOPY' and money_type == 'MONEY':
                return 2
            return 1
        elif request_type == WorkItemRequestTypes.CORRESPONDENCE:
            return 10
        elif request_type == WorkItemRequestTypes.STOCK_MOVEMENT:
            return 4
        elif request_type == WorkItemRequestTypes.INSURANCE:
            # TODO - need to do below
            # if status is "archive pending complete"; we mark the status as "complete" and timeline as "assets ready"
            # Note that in this particular case we override the default status mapping and do this instead
            # This is a part of work item create/update -> we need to update the work item mapping
            pass
        elif request_type == WorkItemRequestTypes.TRADING:
            return 2
        return None
