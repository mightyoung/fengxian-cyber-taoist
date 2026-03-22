"""
S3-compatible storage for reports and files
Supports MinIO, AWS S3, and other S3-compatible services

Directory Structure:
    reports/
      {report_id}/
        {timestamp}/
          report.md           # Original report
          report.pdf          # PDF version
          analysis.json       # Analysis result data
          metadata.json       # Metadata (creation time, model version, etc.)

    charts/
      {chart_id}/
        {timestamp}/
          chart_data.json    # Chart data
          embedding.json     # Vector data

    exports/
      {user_id}/
        {timestamp}/
          {filename}         # User exported files
"""

import os
import json
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from typing import Optional, List, Dict, Any


class S3Storage:
    """S3-compatible storage for reports and files"""

    # Default bucket name
    DEFAULT_BUCKET = 'fengxian_cyber_taoist-reports'

    def __init__(self, bucket_name: Optional[str] = None):
        """
        Initialize S3 storage

        Args:
            bucket_name: Optional bucket name override. If not provided,
                       tries to create 'fengxian_cyber_taoist-reports', falls back to
                       environment variable or 'mightyoung'
        """
        self.endpoint_url = os.environ.get('S3_ENDPOINT_URL')
        self.access_key = os.environ.get('S3_ACCESS_KEY')
        self.secret_key = os.environ.get('S3_SECRET_KEY')
        self.region = os.environ.get('S3_REGION_NAME', 'us-east-1')

        # Build client configuration
        client_kwargs = {
            'region_name': self.region,
        }

        if self.endpoint_url:
            client_kwargs['endpoint_url'] = self.endpoint_url

        if self.access_key and self.secret_key:
            client_kwargs['aws_access_key_id'] = self.access_key
            client_kwargs['aws_secret_access_key'] = self.secret_key

        self.client = boto3.client('s3', **client_kwargs)

        # Determine bucket name with auto-creation fallback
        self.bucket_name = self._setup_bucket(bucket_name)

    def _setup_bucket(self, preferred_bucket: Optional[str] = None) -> str:
        """
        Setup bucket with auto-creation fallback

        Args:
            preferred_bucket: Preferred bucket name

        Returns:
            Bucket name to use
        """
        # If explicitly provided, use it
        if preferred_bucket:
            return preferred_bucket

        # Try to create the default bucket first
        try:
            self.client.create_bucket(Bucket=self.DEFAULT_BUCKET)
            return self.DEFAULT_BUCKET
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            # If bucket already exists (BucketAlreadyOwnedByYou) or other success, use it
            if error_code in ['BucketAlreadyOwnedByYou', 'BucketAlreadyExists']:
                return self.DEFAULT_BUCKET
            # If permission denied or other error, fall back to old bucket
            fallback = os.environ.get('S3_BUCKET_NAME', 'mightyoung')
            return fallback

    def _generate_key(self, category: str, item_id: str, filename: str) -> str:
        """
        Generate S3 key with timestamp: {category}/{item_id}/{timestamp}/{filename}

        Args:
            category: Category (reports, charts, exports)
            item_id: Unique identifier (report_id, chart_id, user_id)
            filename: Name of the file

        Returns:
            S3 key path
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{category}/{item_id}/{timestamp}/{filename}"

    def _generate_metadata_key(self, category: str, item_id: str) -> str:
        """
        Generate S3 key for metadata file

        Args:
            category: Category (reports, charts, exports)
            item_id: Unique identifier

        Returns:
            S3 key for metadata.json
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"{category}/{item_id}/{timestamp}/metadata.json"

    def upload_with_metadata(
        self,
        category: str,
        item_id: str,
        content: bytes,
        content_type: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a file with its metadata to S3

        Args:
            category: Category (reports, charts, exports)
            item_id: Unique identifier
            content: File content as bytes
            content_type: MIME type
            filename: Original filename
            metadata: Optional metadata dict

        Returns:
            S3 key path
        """
        key = self._generate_key(category, item_id, filename)

        # Upload the main file
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=content,
            ContentType=content_type
        )

        # Upload metadata if provided
        if metadata:
            metadata_key = self._generate_metadata_key(category, item_id)
            metadata_content = json.dumps(metadata, ensure_ascii=False, indent=2)
            self.client.put_object(
                Bucket=self.bucket_name,
                Key=metadata_key,
                Body=metadata_content.encode('utf-8'),
                ContentType='application/json'
            )

        return key

    def upload_report(
        self,
        report_id: str,
        content: bytes,
        content_type: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a report file to S3

        Args:
            report_id: Unique report identifier for grouping
            content: File content as bytes
            content_type: MIME type (e.g., 'text/markdown', 'application/pdf')
            filename: Original filename
            metadata: Optional metadata dict

        Returns:
            S3 key path
        """
        return self.upload_with_metadata('reports', report_id, content, content_type, filename, metadata)

    def upload_markdown(
        self,
        report_id: str,
        content: str,
        filename: str = 'report.md',
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a markdown report to S3

        Args:
            report_id: Unique report identifier
            content: Markdown content as string
            filename: Optional filename (default: report.md)
            metadata: Optional metadata dict

        Returns:
            S3 key path
        """
        return self.upload_with_metadata(
            category='reports',
            item_id=report_id,
            content=content.encode('utf-8'),
            content_type='text/markdown; charset=utf-8',
            filename=filename,
            metadata=metadata
        )

    def upload_pdf(
        self,
        report_id: str,
        content: bytes,
        filename: str = 'report.pdf',
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a PDF report to S3

        Args:
            report_id: Unique report identifier
            content: PDF content as bytes
            filename: Optional filename (default: report.pdf)
            metadata: Optional metadata dict

        Returns:
            S3 key path
        """
        return self.upload_with_metadata(
            category='reports',
            item_id=report_id,
            content=content,
            content_type='application/pdf',
            filename=filename,
            metadata=metadata
        )

    def upload_chart(
        self,
        chart_id: str,
        content: bytes,
        content_type: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a chart file to S3

        Args:
            chart_id: Unique chart identifier
            content: File content as bytes
            content_type: MIME type
            filename: Original filename
            metadata: Optional metadata dict

        Returns:
            S3 key path
        """
        return self.upload_with_metadata('charts', chart_id, content, content_type, filename, metadata)

    def upload_export(
        self,
        user_id: str,
        content: bytes,
        content_type: str,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Upload a user export file to S3

        Args:
            user_id: User identifier
            content: File content as bytes
            content_type: MIME type
            filename: Original filename
            metadata: Optional metadata dict

        Returns:
            S3 key path
        """
        return self.upload_with_metadata('exports', user_id, content, content_type, filename, metadata)

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Generate a presigned URL for downloading

        Args:
            key: S3 object key
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Presigned URL string
        """
        return self.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': self.bucket_name, 'Key': key},
            ExpiresIn=expires_in
        )

    def download_file(self, key: str, local_path: str) -> bool:
        """
        Download a file from S3 to local path

        Args:
            key: S3 object key
            local_path: Local destination path

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.download_file(self.bucket_name, key, local_path)
            return True
        except ClientError:
            return False

    def download_report(self, report_id: str, filename: str, local_path: str) -> bool:
        """
        Download a specific report file by report_id and filename

        Args:
            report_id: Report identifier
            filename: Name of the file to download
            local_path: Local destination path

        Returns:
            True if successful, False otherwise
        """
        # Find the latest version of the file
        keys = self.list_items('reports', report_id)
        matching_keys = [k for k in keys if k.endswith(f"/{filename}")]

        if not matching_keys:
            return False

        # Use the latest version (last one in sorted list)
        latest_key = sorted(matching_keys)[-1]
        return self.download_file(latest_key, local_path)

    def list_items(self, category: str, item_id: str) -> List[str]:
        """
        List all files for a given category and item_id

        Args:
            category: Category (reports, charts, exports)
            item_id: Item identifier

        Returns:
            List of S3 keys
        """
        prefix = f"{category}/{item_id}/"
        response = self.client.list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
        return [obj['Key'] for obj in response.get('Contents', [])]

    def list_reports(self, report_id: str) -> List[str]:
        """
        List all files for a given report_id

        Args:
            report_id: Report identifier

        Returns:
            List of S3 keys
        """
        return self.list_items('reports', report_id)

    def list_charts(self, chart_id: str) -> List[str]:
        """
        List all files for a given chart_id

        Args:
            chart_id: Chart identifier

        Returns:
            List of S3 keys
        """
        return self.list_items('charts', chart_id)

    def list_exports(self, user_id: str) -> List[str]:
        """
        List all files for a given user_id

        Args:
            user_id: User identifier

        Returns:
            List of S3 keys
        """
        return self.list_items('exports', user_id)

    def delete_item(self, category: str, item_id: str) -> bool:
        """
        Delete all files for a given category and item_id

        Args:
            category: Category (reports, charts, exports)
            item_id: Item identifier

        Returns:
            True if successful
        """
        keys = self.list_items(category, item_id)
        if not keys:
            return True

        # Delete in batches (max 1000 per request)
        for i in range(0, len(keys), 1000):
            batch = keys[i:i + 1000]
            self.client.delete_objects(
                Bucket=self.bucket_name,
                Delete={
                    'Objects': [{'Key': k} for k in batch],
                    'Quiet': True
                }
            )
        return True

    def delete_report(self, report_id: str) -> bool:
        """
        Delete all files for a given report_id

        Args:
            report_id: Report identifier

        Returns:
            True if successful
        """
        return self.delete_item('reports', report_id)

    def delete_chart(self, chart_id: str) -> bool:
        """
        Delete all files for a given chart_id

        Args:
            chart_id: Chart identifier

        Returns:
            True if successful
        """
        return self.delete_item('charts', chart_id)

    def key_exists(self, key: str) -> bool:
        """
        Check if a specific key exists in S3

        Args:
            key: S3 object key

        Returns:
            True if key exists, False otherwise
        """
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except ClientError:
            return False

    def get_object_metadata(self, key: str) -> Optional[dict]:
        """
        Get metadata for an S3 object

        Args:
            key: S3 object key

        Returns:
            Metadata dict or None if not found
        """
        try:
            response = self.client.head_object(Bucket=self.bucket_name, Key=key)
            return {
                'ContentLength': response.get('ContentLength'),
                'ContentType': response.get('ContentType'),
                'LastModified': response.get('LastModified'),
                'ETag': response.get('ETag')
            }
        except ClientError:
            return None

    def copy_object(self, source_key: str, dest_key: str) -> bool:
        """
        Copy an object within the same bucket

        Args:
            source_key: Source object key
            dest_key: Destination object key

        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.copy_object(
                Bucket=self.bucket_name,
                CopySource={'Bucket': self.bucket_name, 'Key': source_key},
                Key=dest_key
            )
            return True
        except ClientError:
            return False


# Singleton instance for convenience
_storage_instance: Optional[S3Storage] = None


def get_storage() -> S3Storage:
    """
    Get the singleton S3Storage instance

    Returns:
        S3Storage instance
    """
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = S3Storage()
    return _storage_instance


def save_report_to_s3(
    report_id: str,
    report_content: str,
    report_format: str = 'markdown',
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Save report to S3 and return presigned download URL

    Args:
        report_id: Unique report identifier
        report_content: Report content (markdown string or PDF bytes)
        report_format: 'markdown' or 'pdf'
        metadata: Optional metadata dict

    Returns:
        Presigned URL for downloading the report
    """
    storage = get_storage()

    # Add standard metadata fields
    if metadata is None:
        metadata = {}
    metadata.setdefault('report_id', report_id)
    metadata.setdefault('created_at', datetime.now().isoformat())
    metadata.setdefault('report_type', 'analysis')

    if report_format == 'markdown':
        content = report_content.encode('utf-8')
        content_type = 'text/markdown; charset=utf-8'
        filename = 'report.md'
    elif report_format == 'pdf':
        content = report_content  # already bytes
        content_type = 'application/pdf'
        filename = 'report.pdf'
    else:
        raise ValueError(f"Unsupported report format: {report_format}")

    key = storage.upload_report(report_id, content, content_type, filename, metadata)
    return storage.get_presigned_url(key)
