from config import Config
import logging.config

min_log_level = "INFO"

old_factory = logging.getLogRecordFactory()

ETL_LAMBDA_NAME = 'fp_dashboard_etl_lambda'
ETL_GLUE_LOGGER_APP_NAME = 'fp_dashboard_etl_glue'


def add_glue_app_name_attribute(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.appName = ETL_GLUE_LOGGER_APP_NAME
    return record


def add_lambda_app_name_attribute(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.appName = ETL_LAMBDA_NAME
    return record


def get_logging_config(environment, app_name=None):
    SPLUNK_SETTINGS = Config().get_splunk_details(environment)

    log_config_dict = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            # see full list of attributes here:
            # https://docs.python.org/3/library/logging.html#logrecord-attributes
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
            'timestampthread': {
                'format': "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s] [%(name)-20.20s]  %(message)s",
            },
            'json': {
                '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
                'format': '%(asctime)s %(created)f %(exc_info)s %(filename)s %(funcName)s %(levelname)s %(levelno)s %(lineno)d %(module)s %(message)s %(pathname)s %(process)s %(processName)s %(relativeCreated)d %(thread)s %(threadName)s'
            }
        },
        'handlers': {
            'splunk': {
                'level': min_log_level,
                'class': 'splunk_handler.SplunkHandler',
                'formatter': 'json',
                'host': SPLUNK_SETTINGS['host'],
                'port': SPLUNK_SETTINGS['port'],
                'token': SPLUNK_SETTINGS['token'],
                'index': SPLUNK_SETTINGS['index'],
                'verify': False,
                'sourcetype': '_json',  # assuming this part of config is used only for glue for now.
            },
            'console': {
                'level': min_log_level,  # this level or higher goes to the console
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            # root configuration – for all of our own apps
            # (feel free to do separate treatment for e.g. brokenapp vs. sth else)
            '': {
                'handlers': ['splunk', 'console'],
                'level': min_log_level,  # this level or higher goes to the console and logfile
            },
        },
    }
    logging.config.dictConfig(log_config_dict)

    # Add custom attribute
    if not app_name or app_name == ETL_GLUE_LOGGER_APP_NAME:
        logging.setLogRecordFactory(add_glue_app_name_attribute)
    elif app_name == ETL_LAMBDA_NAME:
        logging.setLogRecordFactory(add_lambda_app_name_attribute)

    # Set the log levels
    logging.getLogger('peewee').setLevel(logging.ERROR)
    logging.getLogger('java_gateway').setLevel(logging.ERROR)
    logging.getLogger('botocore').setLevel(logging.ERROR)
