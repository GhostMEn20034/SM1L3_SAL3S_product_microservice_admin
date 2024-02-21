from boto3 import client
from botocore.client import BaseClient

from src.config.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

def get_s3_client(access_key_id=AWS_ACCESS_KEY_ID, secret_access_key=AWS_SECRET_ACCESS_KEY) -> BaseClient:
    s3 = client('s3', aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
    return s3