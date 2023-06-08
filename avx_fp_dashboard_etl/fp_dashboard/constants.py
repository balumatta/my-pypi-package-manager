class BaseStatusClass:
    @classmethod
    def vars_to_dict(cls):
        valid_vars = {
            var: value
            for var, value in cls.__dict__.items()
            if not callable(getattr(cls, var)) and not var.startswith("__")
        }
        return valid_vars

    @classmethod
    def get_tuples_for_choices(cls):
        return [
            (value, value)
            for var, value in cls.__dict__.items()
            if not callable(getattr(cls, var)) and not var.startswith("__")
        ]

    @classmethod
    def get_list_for_choices(cls):
        return [
            value
            for var, value in cls.__dict__.items()
            if not callable(getattr(cls, var)) and not var.startswith("__")
        ]


class TimelineStatus(BaseStatusClass):
    REQUEST_DRAFTED = 'Request Drafted'
    REQUEST_SUBMITTED_BY_FP = 'Request Submitted by FP'
    IN_REVIEW_WITH_AVANTAX_TEAM = 'In Review with Avantax Team'
    ACCOUNT_SETUP_SUCCESSFUL = 'Account Setup Successful'
    ACCOUNT_SETUP_REJECTED = 'Account Setup Rejected'
    REQUEST_RESUBMITTED_BY_FP = 'Request Re-Submitted by FP'
    ASSETS_READY = 'Assets Ready'


class BPMStatus(BaseStatusClass):
    SECOND_REQ_FOR_INFO = "2nd Request for Information"
    SECOND_SEARCH = "2nd Search"
    ABANDONED = "Abandoned"
    ALT_INVESTMENTS = "Alt Investments"
    APPROVED = "Approved"
    APPROVED_AGREEMENT = "Approved Agreement"
    APPROVED_FINAL = "Approved Final"
    APPROVED_PLAN = "Approved Plan"
    ARCHIVE_PENDING_COMPLETED = "Archive Pending Completed"
    ARCHIVE_PENDING_NOT_PROCESSED = "Archive Pending Not Processed"
    CANCEL = "Cancel"
    CORRECTED = "Corrected"
    COMPLETED = "Completed"
    DATA_FAILURE = "Data Failure"
    DISMISSED_FIRST_OCCURRENCE = "Dismissed First Occurrence"
    ESCALATED_APPROVAL = "Escalated Approval"
    DEATH_DIVORCE = "Death Divorce"
    EDD = "EDD"
    ESIGN_COMPLETED = "Esign Completed"
    FINAL_SEARCH = "Final Search"
    IGO_PROCESSED_PEND_SETTLEMENT = "IGO Processed Pend Settlement"
    IGO = "IGO"
    IMPORT_ERROR = "Import Error"
    IN_PROCESS = "In Process"
    IN_PROGRESS = "In Progress"
    INDEXED = "Indexed"
    INJECTED = "INJECTED"
    MATCHED = "Matched"
    MM_JOURNALS = "MM Journals"
    NEEDS_CORRECTION = "Needs Correction"
    NIGO = "NIGO"
    NIGO_PROCESS_BEGUN = "NIGO PROCESS BEGUN"
    NOT_PROCESSED = "Not Processed"
    ON_HOLD = "On Hold"
    OTHER_PROCESS_FAILURE = "OTHER PROCESS FAILURE"
    PEND = "Pend"
    PEND_ONE_DAY = "Pend 1 Day"
    PEND_BOLA = "Pend Bola"
    PEND_EXPIRED = "Pend Expired"
    PENDING_CLIENT_SIGNED_FEE_PLAN = "Pending Client Signed Fee Plan"
    PENDING_DOCS = "Pending Documents"
    PENDING_FEE_PLAN_OVER_120_DAYS = "Pending Fee Plan Over 120 Days"
    PENDING_FEE_PLAN_OVER_150_DAYS = "Pending Fee Plan Over 150 Days"
    PENDING_INITIAL_FEE_PLAN_DOC = "Pending Initial Fee Plan Doc"
    PENDING_RETRANSMISSION = "Pending Retransmission"
    QC = "QC"
    RECON = "Recon"
    PROCESSED = "Processed"
    REINDEX = "Reindex"
    REJECT_TO_INBOUND = "Reject to Inbound"
    REQUEST_FOR_INFORMATION = "Request For Information"
    RESTRICTED_ACCOUNT = "Restricted Account"
    RETURN_TO_HOME_OFFICE = "Return To Home Office"
    REJECTED = "Rejected"
    REPAIRED = "Repaired"
    RETURN = "Return"
    RETURN_TO_OPS = "Return to Ops"
    RESPONSE_RECEIVED = "Response Received"
    REVIEW = "Review"
    REVIEW_AND_RESEARCH = "Review and Research"
    REVIEWED = "Reviewed"
    REVIEWED_NO_VIOLATION = "Reviewed No Violation"
    REVIEWED_YES_VIOLATION = "Reviewed Violation"
    SALES_SUPE_REVIEW = "Sales Supe Review"
    SEND_TO_ARCHIVE = "Send to Archive"
    SUCCESS = "SUCCESS"
    SUCCESSFUL_TRANSMISSION = "Successful Transmission"
    TRANSMISSION_FAILURE = "TRANSMISSION FAILURE"
    UNINDEXED = "Unindexed"
    TRANSMITTING_TO_ICP = "Transmitting to ICP"
    VERIFIED_FUNDS = "Verified Funds"
    VERIFY_FUNDS = "Verify Funds"


# work item status
class WorkItemStatus(BaseStatusClass):
    DRAFTED = 'Drafted'
    NIGO = 'NIGO'
    IN_REVIEW = 'In Review'
    COMPLETED = 'Completed'


class WorkItemRequestTypes(BaseStatusClass):
    ADVISORY_NEW_ACCOUNTS = 'Advisory New Accounts'
    NEW_ACCOUNTS = 'New Accounts'
    ACCOUNT_MAINTENANCE = 'Account Maintenance'
    MM_STANDING_INSTRUCTION = 'MM Standing Instructions'
    MONEY_MOVEMENT = 'Money Movement'
    DIRECT_ANNUITIES = 'Direct Annuities'
    CHECK_DEPOSIT = 'Check Deposit'
    STOCK_MOVEMENT = 'Stock Movement'
    INSURANCE = 'Insurance'
    ADVISORY_MAINTENANCE = 'Advisory Maintenance'
    CORRESPONDENCE = 'Correspondence'
    TRADING = 'Trading'
    TOA = 'TOA'


required_work_item_types = WorkItemRequestTypes.get_list_for_choices()

completed_timeline_status = [
    TimelineStatus.ACCOUNT_SETUP_SUCCESSFUL,
    TimelineStatus.ASSETS_READY,
    TimelineStatus.ACCOUNT_SETUP_REJECTED,
]
