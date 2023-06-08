import os

import jaydebeapi
import logging
logger = logging.getLogger(__name__)


class MSSqlDatabaseConnection:
    def __init__(self, secret_name=None, region=None, db_details=None):
        if not db_details:
            db_details = self.get_connection_credentials(secret_name, region)

            if not db_details:
                exit()

        db_name = db_details['dbname']
        host = db_details['host']
        user = db_details['username']
        password = db_details['password']
        domain = db_details['domain']

        # connection_str = "Driver={SQL Server Native Client 11.0};Server=" + host + ";Database=" + db_name + ";Trusted_Connection=yes;"
        logger.info('connection str - ', connection_str)
        # self.db_connection = pyodbc.connect(connection_str)

        # connection_url = "jdbc:jtds:sqlserver://10.100.185.20/ClientCenter;useNTLMv2=true;user=svc_glue_cp_dev;password=55t1_tHRzrUNJM_F3yeSX.wirRjBGv8cCS;domain=IRV.hdv.corp"
        connection_url = "jdbc:jtds:sqlserver://" + host + "/" + db_name + ";useLOBs=false;useNTLMv2=true;user=" + user + ";password=" + password + ";domain=" + domain + """"""

        driver_name = "net.sourceforge.jtds.jdbc.Driver"
        jar_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'jtds-1.3.1.jar')
        connection_properties = {}
        self.db_connection = jaydebeapi.connect(driver_name, connection_url, connection_properties, jar_path)

    def get_db_cursor(self):
        cursor = self.db_connection.cursor()
        return cursor

    def close_db_connection(self):
        self.db_connection.close()

    def get_connection_credentials(self, secret_name, region):
        db_details = get_credentials_from_aws_secrets(secret_name, region)
        if not db_details:
            logger.info(db_details)
            logger.info('Invalid db credentials')

        return db_details
