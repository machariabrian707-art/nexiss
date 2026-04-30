import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid

from nexiss.core.config import settings


class StorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )
        self.bucket = settings.AWS_S3_BUCKET

    def generate_upload_url(self, filename: str, content_type: str) -> dict:
        """Generate a pre-signed S3 PUT URL for direct browser upload."""
        ext = filename.rsplit('.', 1)[-1] if '.' in filename else 'bin'
        s3_key = f"uploads/{uuid.uuid4()}.{ext}"

        url = self.s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': self.bucket,
                'Key': s3_key,
                'ContentType': content_type,
            },
            ExpiresIn=900,  # 15 minutes
        )
        return {'upload_url': url, 's3_key': s3_key}

    def generate_download_url(self, s3_key: str, expires_in: int = 3600) -> str:
        """Generate a pre-signed S3 GET URL."""
        url = self.s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket, 'Key': s3_key},
            ExpiresIn=expires_in,
        )
        return url

    def get_object_bytes(self, s3_key: str) -> bytes:
        """Download file bytes from S3 for processing."""
        response = self.s3.get_object(Bucket=self.bucket, Key=s3_key)
        return response['Body'].read()

    def delete_object(self, s3_key: str) -> None:
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=s3_key)
        except ClientError:
            pass


# Singleton
storage_service = StorageService()
