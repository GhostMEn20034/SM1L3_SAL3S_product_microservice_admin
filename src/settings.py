import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")

ALLOWED_IMAGE_TYPE = 'data:image/jpeg'

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
BUCKET_BASE_URL = os.getenv("BUCKET_BASE_URL")