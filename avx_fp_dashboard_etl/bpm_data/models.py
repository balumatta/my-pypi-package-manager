from peewee import Model, IntegerField, CharField, BooleanField, DateTimeField, DecimalField, Proxy

import logging

logger = logging.getLogger(__name__)

existing_nfs_db_connection = Proxy()


class BPMModelsBaseClass(Model):
    class Meta:
        schema = 'staging'
        database = existing_nfs_db_connection

    # @classmethod
    # def vars_to_dict(cls):
    #     remove_class_vars = {'_meta', '_schema'}
    #     valid_vars = {
    #         var: None
    #         for var, value in cls.__dict__.items()
    #         if all([not callable(getattr(cls, var)), not var.startswith("__"), var not in remove_class_vars])
    #     }
    #     return copy.deepcopy(valid_vars)


class ClientType(BPMModelsBaseClass):
    ClientTypeID = IntegerField(primary_key=True)
    Code = CharField(null=True)
    Name = CharField(null=True)
    Description = CharField(null=True)
    CreateStamp = DateTimeField()
    Sort = IntegerField()

    class Meta:
        db_table = 'client_type'


class Client(BPMModelsBaseClass):
    ClientId = IntegerField(primary_key=True)
    RepId = IntegerField()
    ClientName = CharField(null=True)
    ClientTypeId = IntegerField(null=True)
    IsProspect = BooleanField()
    CreateStamp = DateTimeField()
    LastUpdateStamp = DateTimeField()
    AcknowledgeStamp = DateTimeField()
    LastUpdateUserID = IntegerField()
    Conversion_CM_contact_id = IntegerField()
    SegmentTypeId = IntegerField()
    SegmentGroupTypeId = IntegerField()
    IsPrivate = BooleanField()
    StickyNote = CharField(null=True)
    ClientSalutation = CharField(null=True)
    HouseholdSvcStamp = CharField(null=True)

    def get_client_by_id(self, client_id):
        if not client_id:
            return None
        client_details = self.get_or_none(ClientId=client_id)
        if not client_details:
            return {}

        client_details_dict = {
            'client_id': client_details.ClientId,
            'household_name': client_details.ClientName.lower() if client_details.ClientName else None,
            # 'rep_id': client_details.RepId,
            'client_type_id': client_details.ClientTypeId,
        }

        if client_details.ClientTypeId:
            client_type_details = ClientType.get_or_none(ClientTypeID=client_details.ClientTypeId)
            if not client_type_details:
                return client_details_dict

            client_details_dict['client_type'] = client_type_details.Name
            client_details_dict['client_type_code'] = client_type_details.Code

        return client_details_dict

    class Meta:
        db_table = 'client'


class NfsBpmInProgressItems(BPMModelsBaseClass):
    NfsBpmItemId = IntegerField(primary_key=True)
    ClientId = IntegerField(null=True)
    EntityId = IntegerField(null=True)
    RepId = IntegerField(null=True)
    HouseholdName = CharField(null=True)
    ItemType = CharField()
    ItemSubType = CharField(null=True)
    WorkflowCreateDate = DateTimeField()
    WorkItemNumber = CharField()
    Priority = IntegerField(null=True)
    MailType = CharField(null=True)
    Origin = CharField(null=True)
    MoneyType = CharField(null=True)
    LineOfBusiness = CharField(null=True)
    Sponsor = CharField(null=True)
    AdvisorNumber = IntegerField(null=True)
    NFRepCode = CharField()
    SSN = CharField(null=True)
    AccountNumber = CharField(null=True)
    RegistrationType = CharField(null=True)
    NonBrokerageAccount = CharField(null=True)
    NonBrokerageRegType = CharField(null=True)
    LastName = CharField(null=True)
    FirstName = CharField(null=True)
    Status = CharField(null=True)
    StatusDate = DateTimeField(null=True)
    CurrentQueue = CharField(null=True)
    QueueEntryDate = DateTimeField(null=True)
    Memo = CharField(null=True)
    WorkflowCompletionDate = DateTimeField(null=True)
    NIGOReason = CharField(null=True)
    AlertStatus = CharField(null=True)
    AlertStatusReason = CharField(null=True)
    UAOID = CharField(null=True)
    ProposalID = CharField(null=True)
    XTRAC_ConnectID = CharField(null=True)
    EncaptureLocatorID = CharField(null=True)
    KofaxCaseNumber = CharField(null=True)
    KofaxExtBatchID = CharField(null=True)
    ViaForms = BooleanField(null=True)
    NIGO = BooleanField(null=True)
    EDD = BooleanField(null=True)
    AML = BooleanField(null=True)
    AlertMemo = CharField(null=True)
    TrackerStatusId = IntegerField(null=True)
    CreateDate = DateTimeField()
    LastUpdateStamp = DateTimeField()

    def get_all_data(self):
        nfs_bpm_in_progress_items = self.select()
        all_work_item_details = []
        for work_item_details in nfs_bpm_in_progress_items:
            all_work_item_details.append({
                'work_item_number': work_item_details.WorkItemNumber,
                'item_type': work_item_details.ItemType,
                'registration_type': work_item_details.RegistrationType,
                'account_number': work_item_details.AccountNumber,
                'line_of_business': work_item_details.LineOfBusiness,
                'sponsor': work_item_details.Sponsor,
                'created_at_in_bpm': work_item_details.WorkflowCreateDate,
                'completed_at': work_item_details.WorkflowCompletionDate,
                'status': work_item_details.Status,
                'last_updated_at_in_bpm': work_item_details.StatusDate,
                'last_updated_at_in_on_prem_db': work_item_details.LastUpdateStamp,
                'nigo_reason': work_item_details.NIGOReason,
                'alert_memo': work_item_details.AlertMemo,
                'client_id': work_item_details.ClientId if work_item_details.ClientId else None,
                'first_name': work_item_details.FirstName,
                'last_name': work_item_details.LastName,
                'nf_rep_code': work_item_details.NFRepCode,
                'rep_id': work_item_details.RepId,
                'advisor_number': work_item_details.AdvisorNumber,
                'current_queue': work_item_details.CurrentQueue,
                'household_name': work_item_details.HouseholdName,
            })

        return all_work_item_details

    class Meta:
        db_table = 'nfs_bpm_inprogress_items'


class NFS_TransferOfAssets(BPMModelsBaseClass):
    NFS_TOA_ID = IntegerField(primary_key=True)
    ETL_ID = IntegerField()
    TOA_Status = CharField(null=True)
    TrackerStatusId = IntegerField(null=True)
    ClientId = IntegerField(null=True)
    EntityId = IntegerField(null=True)
    RepId = IntegerField(null=True)
    AdvisorNumber = CharField(null=True)
    HouseholdName = CharField(null=True)
    SSN = CharField(null=True)
    AccountNumber = CharField(null=True)
    PrimaryFirstName = CharField(null=True)
    PrimaryLastName = CharField(null=True)
    NFSRepCode = CharField(null=True)
    RegTypeCode = CharField(null=True)
    RegTypeDescription = CharField(null=True)
    Agency = CharField(null=True)
    RegistrationLine1 = CharField(null=True)
    RegistrationLine2 = CharField(null=True)
    TOA_CreateDate = DateTimeField(null=True)
    TOA_SettlementDate = DateTimeField(null=True)
    TOA_UpdateDate = DateTimeField(null=True)
    DaysOpen = IntegerField(null=True)
    ContraFirmName = CharField(null=True)
    ContraAccountNumber = CharField(null=True)
    ContraBrokerNumber = CharField(null=True)
    TOA_Type = CharField(null=True)
    TransferType = CharField(null=True)
    FundTransferType = CharField(null=True)
    AmountTransferred = DecimalField(null=True)
    RejectCode = CharField(null=True)
    TransferNumber = CharField(null=True)
    GiftOrInheritance = CharField(null=True)
    CreateDate = DateTimeField()
    LastUpdateStamp = DateTimeField()

    class Meta:
        db_table = 'nfs_transfer_of_assets'


class FinancialProfessional(BPMModelsBaseClass):
    financial_professional_id = CharField(primary_key=True)
    corporate_affiliate_id = CharField()
    financial_professional_role_id = CharField()
    email = CharField()
    rep_number = CharField()
    first_name = CharField()
    last_name = CharField()
    crd_number = CharField()
    npn_number = CharField()
    nfs_rep_code = CharField()
    record_hash = CharField()
    date_inserted = CharField()
    date_updated = CharField()
    is_soft_deleted = CharField()

    def get_user_by_rep_code(self, rep_code):
        if not rep_code:
            return None

        user_details = self.get_or_none(nfs_rep_code=rep_code)
        if not user_details:
            return {}

        user_details_dict = {
            'financial_professional_id': user_details.financial_professional_id,
            'first_name': user_details.first_name.lower() if user_details.first_name else None,
            'last_name': user_details.last_name.lower() if user_details.last_name else None,
            'nfs_rep_code': user_details.nfs_rep_code,
            'avantax_rep_id': user_details.rep_number,
            'email': user_details.email,
        }
        return user_details_dict

    def get_user_by_rep_id(self, rep_id):
        if not rep_id:
            return None

        user_details = self.get_or_none(rep_number=rep_id)
        if not user_details:
            return {}

        user_details_dict = {
            'financial_professional_id': user_details.financial_professional_id,
            'first_name': user_details.first_name.lower() if user_details.first_name else None,
            'last_name': user_details.last_name.lower() if user_details.last_name else None,
            'nfs_rep_code': user_details.nfs_rep_code,
            'avantax_rep_id': user_details.rep_number,
            'email': user_details.email,
        }
        return user_details_dict

    class Meta:
        db_table = 'financial_professional'


if __name__ == '__main__':
    data = FinancialProfessional().get_user_by_rep_code('DK0')
    logger.info(data)
