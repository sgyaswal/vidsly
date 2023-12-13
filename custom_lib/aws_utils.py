# aws_utils.py

import boto3
from django.conf import settings

def get_ses_client():
    try:
        ses = boto3.client('ses', region_name=settings.AWS_SES_REGION_NAME,
                           aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        return ses
    except Exception as e:
        # Handle exceptions, log or raise a more specific exception
        raise Exception(f"Error creating AWS SES client: {str(e)}")
