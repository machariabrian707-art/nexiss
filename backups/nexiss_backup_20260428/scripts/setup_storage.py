import boto3
from botocore.client import Config
from nexiss.core.config import get_settings

def setup_minio():
    settings = get_settings()
    
    print(f"Connecting to MinIO at {settings.s3_endpoint_url}...")
    
    # Initialize S3 client for MinIO
    s3 = boto3.client(
        's3',
        endpoint_url=settings.s3_endpoint_url,
        aws_access_key_id=settings.s3_access_key_id,
        aws_secret_access_key=settings.s3_secret_access_key,
        config=Config(signature_version='s3v4'),
        region_name=settings.s3_region
    )

    bucket_name = settings.s3_bucket

    try:
        # Check if bucket exists
        s3.head_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' already exists.")
    except Exception:
        # Create bucket
        print(f"Creating bucket '{bucket_name}'...")
        s3.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created successfully.")

    print("\nStorage setup complete! Nexiss is ready to save documents locally.")

if __name__ == "__main__":
    setup_minio()
