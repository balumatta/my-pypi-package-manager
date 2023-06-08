import traceback
from datetime import datetime

from avx_fp_dashboard_etl.fp_dashboard.models import ClientWorkItemMapping, Client
import logging

logger = logging.getLogger(__name__)


class ClientTasks:
    @classmethod
    def update(cls, client_details, client_obj):
        if not client_obj:
            return None, False

        try:
            is_updated = False
            if client_details['household_name'] and client_obj.household_name.lower() != client_details[
                'household_name'].lower():
                client_obj.household_name = client_details['household_name']
                is_updated = True

            if client_details['first_name'] and client_obj.first_name.lower() != client_details['first_name'].lower():
                client_obj.first_name = client_details['first_name']
                is_updated = True

            if client_details['last_name'] and client_obj.last_name.lower() != client_details['last_name'].lower():
                client_obj.last_name = client_details['last_name']
                is_updated = True

            if client_obj.client_type != client_details['client_type']:
                client_obj.client_type = client_details['client_type']
                is_updated = True

            if is_updated:
                client_obj.last_updated_at = datetime.now()
                client_obj.save()

            return client_obj, is_updated

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            return None, False

    @classmethod
    def create_or_update(cls, client_details, work_item_obj):
        # get or create client details
        client_obj, is_created = cls.get_or_create(client_details=client_details, work_item_obj=work_item_obj)

        if is_created:
            # Mark is_updated true here as there is an update for the work item and it has to be notifed to the user
            work_item_obj.has_updates = True
            work_item_obj.save()
            return client_obj, 'Insertion', True

        client_obj, is_updated = cls.update(client_details=client_details, client_obj=client_obj)
        if is_updated:
            # Mark is_updated true here as there is an update for the work item and it has to be notifed to the user
            work_item_obj.has_updates = True
            work_item_obj.save()
            return client_obj, 'Updation', True

        if not client_obj:
            return None, 'Failed', False

        # was operation successful
        return client_obj, 'Nothing', True

    @staticmethod
    def get_or_create(client_details, work_item_obj):
        try:
            defaults = {
                'created_at': datetime.now(),
                'household_name': client_details.get('household_name', None),
                'first_name': client_details.get('first_name', None),
                'last_name': client_details.get('last_name', None),
                'client_type': client_details.get('client_type', None),
            }

            """
                If there is client id, check client on the basis of client id
                if not, check against the first name, last name and household name            
            """
            if client_details['client_id']:
                client, client_created = Client.get_or_create(avantax_client_id=client_details['client_id'],
                                                              defaults=defaults)
            else:
                client, client_created = Client.get_or_create(first_name=client_details['first_name'],
                                                              last_name=client_details['last_name'],
                                                              household_name=client_details['household_name'],
                                                              defaults=defaults)

            ClientWorkItemMapping.get_or_create(client=client, work_item=work_item_obj,
                                                defaults={'created_at': datetime.now()})
            return client, client_created
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            return None, False
