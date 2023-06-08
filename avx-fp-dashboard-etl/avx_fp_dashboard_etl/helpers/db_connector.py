from peewee import Proxy, PostgresqlDatabase

from avx_fp_dashboard_etl.helpers.credentials import get_rds_database_credentials
import logging

logger = logging.getLogger(__name__)


class PostgresDatabaseConnection:
    def __init__(self, db_details, db_schema_name=None):
        secret_name = db_details['secret_name']
        region = db_details['region_name']
        db_end_point = db_details['host']
        db_username = db_details.get('username', None)
        db_password = db_details.get('password', None)

        if not db_username or not db_password:
            profile_name = db_details.get('aws_cli_profile_name', None)
            db_username, db_password = get_rds_database_credentials(secret_name, region, db_end_point, profile_name)
            if not db_username or not db_password:
                logger.error('Invalid db credentials')
                exit()

        # logger.info('Database Details')
        # logger.info(db_details)
        # logger.info(f'Db user name - ', db_username)
        # logger.info(f'Db password - ', db_password)
        self.db = PostgresqlDatabase(db_details['db_name'], host=db_details['host'],
                                     port=db_details['port'],
                                     user=db_username, password=db_password)
        self.db.connect()

        if db_schema_name:
            self.db.execute_sql('set search_path to ' + db_schema_name)

    def initialise_db_connection(self, conn_proxy):
        if not conn_proxy:
            conn_proxy = Proxy()

        conn_proxy.initialize(self.db)
        return conn_proxy
