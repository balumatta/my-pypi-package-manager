import base64
import traceback

import boto3
from botocore.exceptions import ClientError

import logging

logger = logging.getLogger(__name__)


def get_rds_db_auth_token(db_end_point, user_name, port=5432):
    logger.info('Fetching RDS DB Auth token..........')
    try:
        # Generate the password
        client_rds = boto3.client("rds", "us-east-1")
        rds_db_auth_token = client_rds.generate_db_auth_token(DBHostname=db_end_point,
                                                              Port=port,
                                                              DBUsername=user_name)

        password = rds_db_auth_token
        return password
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.print_exc())
        logger.error('Exception occurred while fetching RDS DB Auth token')
        return None


def get_credentials_from_aws_secrets(secret_name, region_name, profile_name=None):
    logger.info('Establishing connection to AWS Secrets Manager to get DB credentials')
    try:
        if profile_name:
            session = boto3.session.Session(profile_name=profile_name)
        else:
            session = boto3.session.Session()

        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )
        # client = boto3.client("secretsmanager", region_name=region_name)
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)

        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']

            logger.info('DB credentials retrieved')
            return secret
        else:
            decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
            logger.info(decoded_binary_secret)

        logger.error('Could not retrieve DB credentials')
        return None
    except ClientError as e:
        logger.error(str(e))
        logger.error(traceback.print_exc())
        logger.error(e.response.get('Error', {}).get('Code', None))
        logger.error('Exception occurred while fetching DB creds from AWS Secrets Manager')
        return None
    except Exception as e:
        logger.error(str(e))
        logger.error(traceback.print_exc())
        logger.error('Exception occurred while fetching DB creds from AWS Secrets Manager')
        return None


def get_rds_database_credentials(secret_name, region_name, db_end_point, profile_name=None):
    rds_db_user_name = get_credentials_from_aws_secrets(secret_name, region_name, profile_name)
    rds_db_password = get_rds_db_auth_token(db_end_point, rds_db_user_name)

    if not rds_db_user_name or not rds_db_password:
        logger.info('Username/Password not found.')
        return None, None

    return rds_db_user_name, rds_db_password


if __name__ == '__main__':
    session = boto3.session.Session(profile_name='avx-dev')
    client = session.client(
        service_name='secretsmanager',
        region_name='us-east-1'
    )
    # client = boto3.client("secretsmanager", region_name='us-east-1')
    all_secrets = client.list_secrets()
    for secret in all_secrets['SecretList']:
        logger.info(secret)
