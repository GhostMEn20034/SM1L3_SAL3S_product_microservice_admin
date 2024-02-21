import os

# MongoDB Config
MONGODB_URL = os.getenv("MONGODB_URL")
ATLAS_SEARCH_INDEX_NAME = os.getenv("ATLAS_SEARCH_INDEX_NAME")

# Image type allowed for uploading into the S3 Storage
ALLOWED_IMAGE_TYPE = 'data:image/jpeg'

# Amazon web services credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

# Amazon S3 config
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
BUCKET_BASE_URL = os.getenv("BUCKET_BASE_URL")

# Celery config
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

EVENT_CHECK_INTERVAL_MINUTES = int(os.getenv("EVENT_CHECK_INTERVAL_MINUTES"))

AMPQ_CONNECTION_URL=os.getenv("AMPQ_CONNECTION_URL")
