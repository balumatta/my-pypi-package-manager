import traceback
from datetime import datetime

from avx_fp_dashboard_etl.fp_dashboard.models import User
import logging
logger = logging.getLogger(__name__)


class UserTasks:
    @classmethod
    def update(cls, user_details, user_obj):
        if not user_obj:
            return None, False

        try:
            is_updated = False
            if user_details['first_name'] and user_obj.first_name != user_details['first_name'].lower():
                user_obj.first_name = user_details['first_name'].lower()
                is_updated = True

            if user_details['last_name'] and user_obj.last_name != user_details['last_name'].lower():
                user_obj.last_name = user_details['last_name'].lower()
                is_updated = True

            if is_updated:
                user_obj.last_updated_at = datetime.now()
                user_obj.save()

            return user_obj, is_updated

        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            return None, False

    @classmethod
    def create_or_update(cls, user_details):
        # get or create user details
        user_obj, is_created = cls.get_or_create(user_details=user_details)

        if is_created:
            return user_obj, 'Insertion', True

        user_obj, is_updated = cls.update(user_details=user_details, user_obj=user_obj)
        if is_updated:
            return user_obj, 'Updation', True

        if not user_obj:
            return None, 'Failed', False

        # was operation successful
        return user_obj, 'Nothing', True

    @staticmethod
    def get_or_create(user_details):
        try:
            # for now username is mandatory according to Django User Model which we are using as DB ORM.
            # So we use rep code as username which is anyway unique with first name appended to it

            first_name = user_details.get('first_name', None) if user_details.get('first_name', None) else ''
            user_name = str(user_details['avantax_rep_id']) + '_' + first_name

            defaults = {
                'created_at': datetime.now(),
                'first_name': user_details.get('first_name', None),
                'last_name': user_details.get('last_name', None),
                'avantax_fp_id': user_details.get('financial_professional_id', None),
                'nfs_rep_code': user_details.get('nfs_rep_code', None),
                'avantax_rep_id': user_details.get('avantax_rep_id', None),
                'username': user_name,
                'password': '12345',
                'is_superuser': False,
                'is_staff': False,
                'email': user_details.get('email', None),
                'date_joined': datetime.today()
            }

            user, user_created = User.get_or_create(avantax_rep_id=user_details['avantax_rep_id'], defaults=defaults)

            return user, user_created
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            return None, False
