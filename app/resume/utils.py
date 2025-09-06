import os
from uuid import uuid4
from fastapi import HTTPException, UploadFile
import boto3
from boto3.s3.transfer import TransferConfig
from botocore.exceptions import ClientError
from botocore.config import Config
from decouple import config

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

AWS_S3_ACCESS_KEY_ID = config("AWS_S3_ACCESS_KEY_ID")
AWS_S3_SECRET_ACCESS_KEY = config("AWS_S3_SECRET_ACCESS_KEY")
AWS_S3_ENDPOINT_URL = config("AWS_S3_ENDPOINT_URL")
AWS_S3_CUSTOM_DOMAIN = config("AWS_S3_CUSTOM_DOMAIN")
AWS_STORAGE_BUCKET_NAME = config("AWS_STORAGE_BUCKET_NAME")
AWS_REGION_NAME = config("AWS_REGION_NAME")

session = boto3.session.Session()
s3_client = session.client(
    "s3",
    aws_access_key_id=AWS_S3_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_S3_SECRET_ACCESS_KEY,
    endpoint_url=AWS_S3_ENDPOINT_URL,
    region_name=AWS_REGION_NAME,
    config=Config(s3={"addressing_style": "virtual"}),
)

TRANSFER_CONFIG = TransferConfig(
    multipart_threshold=1024 * 1024 * 5,
    multipart_chunksize=5 * 1024 * 1024,
    max_concurrency=4,
    use_threads=True,
)


async def save_uploaded_file(upload_file: UploadFile, sub_dir: str) -> str:
    try:
        allowed_types = [
            "application/pdf",
            "application/docx",
            "application/xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "image/jpeg",
            "image/png",
            "image/jpg",
        ]

        if upload_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, detail=f"Invalid file type: {upload_file.content_type}"
            )
        file_size = upload_file.size
        if file_size is None:
            raise HTTPException(status_code=400, detail=f"File size is not available")
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"File size exceeds 10MB limit")
        await upload_file.seek(0)

        filename: str = upload_file.filename or ""
        if filename == "":
            raise HTTPException(status_code=400, detail="Filename is missing")
        file_ext = os.path.splitext(filename)[-1]
        file_path = f"{sub_dir}/{uuid4().hex}{file_ext}"
        s3_client.upload_fileobj(
            Fileobj=upload_file.file,
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key=file_path,
            ExtraArgs={
                "ContentType": upload_file.content_type,
                "ACL": "public-read",
            },
            Config=TRANSFER_CONFIG,
        )
        return f"{AWS_S3_CUSTOM_DOMAIN}/{file_path}"
    except ClientError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to upload file to spaces: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload Error: {str(e)}")
