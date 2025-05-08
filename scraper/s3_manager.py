import boto3
import logging
import json
import os
from botocore.exceptions import ClientError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class S3Manager:
    """
    A class to manage S3 operations for storing and retrieving stock data
    """
    
    def __init__(self, bucket_name, region_name='us-east-1'):
        """
        Initialize the S3 manager
        
        Args:
            bucket_name (str): Name of the S3 bucket
            region_name (str, optional): AWS region name
        """
        self.bucket_name = bucket_name
        self.region_name = region_name
        
        self.s3_client = boto3.client('s3', region_name=region_name)
        
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """
        Ensure that the specified S3 bucket exists, create it if it doesn't
        """
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            logger.info(f"Bucket {self.bucket_name} exists")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"Bucket {self.bucket_name} doesn't exist, creating...")
                try:
                    self.s3_client.create_bucket(
                        Bucket=self.bucket_name,
                        CreateBucketConfiguration={
                            'LocationConstraint': self.region_name
                        } if self.region_name != 'us-east-1' else {}
                    )
                    logger.info(f"Bucket {self.bucket_name} created successfully")
                except ClientError as create_error:
                    logger.error(f"Error creating bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise
    
    def upload_file(self, file_path, object_key=None):
        """
        Upload a file to S3
        
        Args:
            file_path (str): Path to the local file
            object_key (str, optional): S3 object key. If not provided, use the file name
            
        Returns:
            str: S3 URI of the uploaded file
        """
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} does not exist")
            raise FileNotFoundError(f"File {file_path} does not exist")
        
        if object_key is None:
            object_key = os.path.basename(file_path)
        
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, object_key)
            logger.info(f"File {file_path} uploaded to s3://{self.bucket_name}/{object_key}")
            return f"s3://{self.bucket_name}/{object_key}"
        except ClientError as e:
            logger.error(f"Error uploading file to S3: {e}")
            raise
    
    def upload_data(self, data, object_key, file_format='json'):
        """
        Upload data directly to S3
        
        Args:
            data: Data to upload (dict, list, DataFrame, etc.)
            object_key (str): S3 object key
            file_format (str): Format of the data ('json' or 'csv')
            
        Returns:
            str: S3 URI of the uploaded data
        """
        try:
            if file_format.lower() == 'json':
                if hasattr(data, 'to_json'):  # Handle pandas DataFrame
                    content = data.to_json(orient='records')
                else:  # Handle dict or list
                    content = json.dumps(data)
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=content,
                    ContentType='application/json'
                )
            
            elif file_format.lower() == 'csv':
                if hasattr(data, 'to_csv'):  # Handle pandas DataFrame
                    content = data.to_csv(index=False)
                else:
                    logger.error("Data must be a pandas DataFrame for CSV format")
                    raise ValueError("Data must be a pandas DataFrame for CSV format")
                
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=content,
                    ContentType='text/csv'
                )
            
            else:
                logger.error(f"Unsupported file format: {file_format}")
                raise ValueError(f"Unsupported file format: {file_format}")
            
            logger.info(f"Data uploaded to s3://{self.bucket_name}/{object_key}")
            return f"s3://{self.bucket_name}/{object_key}"
        
        except ClientError as e:
            logger.error(f"Error uploading data to S3: {e}")
            raise
    
    def generate_presigned_url(self, object_key, expiration=3600):
        """
        Generate a presigned URL for an S3 object
        
        Args:
            object_key (str): S3 object key
            expiration (int, optional): URL expiration time in seconds
            
        Returns:
            str: Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration
            )
            logger.info(f"Generated presigned URL for s3://{self.bucket_name}/{object_key}")
            return url
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
            raise
    
    def download_file(self, object_key, file_path):
        """
        Download a file from S3
        
        Args:
            object_key (str): S3 object key
            file_path (str): Path to save the downloaded file
            
        Returns:
            str: Path to the downloaded file
        """
        try:
            self.s3_client.download_file(self.bucket_name, object_key, file_path)
            logger.info(f"File downloaded from s3://{self.bucket_name}/{object_key} to {file_path}")
            return file_path
        except ClientError as e:
            logger.error(f"Error downloading file from S3: {e}")
            raise
    
    def list_objects(self, prefix=''):
        """
        List objects in the S3 bucket
        
        Args:
            prefix (str, optional): Prefix to filter objects
            
        Returns:
            list: List of object keys
        """
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                objects = [obj['Key'] for obj in response['Contents']]
                logger.info(f"Listed {len(objects)} objects in s3://{self.bucket_name}/{prefix}")
                return objects
            else:
                logger.info(f"No objects found in s3://{self.bucket_name}/{prefix}")
                return []
        except ClientError as e:
            logger.error(f"Error listing objects in S3: {e}")
            raise
    
    def delete_object(self, object_key):
        """
        Delete an object from S3
        
        Args:
            object_key (str): S3 object key
            
        Returns:
            bool: True if deletion was successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=object_key
            )
            logger.info(f"Deleted object s3://{self.bucket_name}/{object_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting object from S3: {e}")
            raise


if __name__ == "__main__":
    s3_manager = S3Manager(bucket_name='stock-data-bucket')
