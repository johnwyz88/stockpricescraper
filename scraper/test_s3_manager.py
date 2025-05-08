import unittest
from unittest.mock import patch, MagicMock
import boto3
import json
import os
import sys
from botocore.exceptions import ClientError

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from s3_manager import S3Manager
from mock_data import MOCK_STOCK_DATA

class TestS3Manager(unittest.TestCase):
    """
    Test cases for the S3Manager class using mocked boto3
    """
    
    def setUp(self):
        """Set up test fixtures"""
        self.bucket_name = 'test-stock-data-bucket'
        self.region_name = 'us-east-1'
        
        self.mock_s3_client = MagicMock()
        
        self.patcher = patch('boto3.client', return_value=self.mock_s3_client)
        self.mock_boto3_client = self.patcher.start()
        
        self.s3_manager = S3Manager(bucket_name=self.bucket_name, region_name=self.region_name)
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.patcher.stop()
    
    def test_init(self):
        """Test initialization of S3Manager"""
        self.mock_boto3_client.assert_called_once_with('s3', region_name=self.region_name)
        
        self.mock_s3_client.head_bucket.assert_called_once_with(Bucket=self.bucket_name)
    
    def test_ensure_bucket_exists_when_bucket_exists(self):
        """Test _ensure_bucket_exists when bucket exists"""
        self.mock_s3_client.reset_mock()
        
        self.s3_manager._ensure_bucket_exists()
        
        self.mock_s3_client.head_bucket.assert_called_once_with(Bucket=self.bucket_name)
        
        self.mock_s3_client.create_bucket.assert_not_called()
    
    def test_ensure_bucket_exists_when_bucket_does_not_exist(self):
        """Test _ensure_bucket_exists when bucket does not exist"""
        self.mock_s3_client.reset_mock()
        
        error_response = {'Error': {'Code': '404'}}
        self.mock_s3_client.head_bucket.side_effect = ClientError(error_response, 'HeadBucket')
        
        self.s3_manager._ensure_bucket_exists()
        
        self.mock_s3_client.head_bucket.assert_called_with(Bucket=self.bucket_name)
        
        expected_args = {
            'Bucket': self.bucket_name,
            'CreateBucketConfiguration': {}
        }
        self.mock_s3_client.create_bucket.assert_called_with(**expected_args)
    
    def test_ensure_bucket_exists_when_bucket_does_not_exist_us_east_1(self):
        """Test _ensure_bucket_exists when bucket does not exist in us-east-1"""
        self.mock_s3_client.reset_mock()
        
        error_response = {'Error': {'Code': '404'}}
        self.mock_s3_client.head_bucket.side_effect = ClientError(error_response, 'HeadBucket')
        
        self.s3_manager = S3Manager(bucket_name=self.bucket_name, region_name='us-east-1')
        
        self.s3_manager._ensure_bucket_exists()
        
        expected_args = {
            'Bucket': self.bucket_name,
            'CreateBucketConfiguration': {}
        }
        self.mock_s3_client.create_bucket.assert_called_with(**expected_args)
    
    def test_upload_file(self):
        """Test upload_file method"""
        temp_file = 'temp_test_file.txt'
        with open(temp_file, 'w') as f:
            f.write('Test content')
        
        try:
            object_key = 'test/temp_file.txt'
            result = self.s3_manager.upload_file(temp_file, object_key)
            
            self.mock_s3_client.upload_file.assert_called_once_with(
                temp_file, self.bucket_name, object_key
            )
            
            expected_uri = f"s3://{self.bucket_name}/{object_key}"
            self.assertEqual(result, expected_uri)
        
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_upload_file_not_found(self):
        """Test upload_file with non-existent file"""
        with self.assertRaises(FileNotFoundError):
            self.s3_manager.upload_file('non_existent_file.txt')
    
    def test_upload_data_json(self):
        """Test upload_data method with JSON format"""
        test_data = list(MOCK_STOCK_DATA.values())
        object_key = 'data/test_data.json'
        
        result = self.s3_manager.upload_data(test_data, object_key, file_format='json')
        
        self.mock_s3_client.put_object.assert_called_once()
        call_args = self.mock_s3_client.put_object.call_args[1]
        self.assertEqual(call_args['Bucket'], self.bucket_name)
        self.assertEqual(call_args['Key'], object_key)
        self.assertEqual(call_args['ContentType'], 'application/json')
        
        expected_uri = f"s3://{self.bucket_name}/{object_key}"
        self.assertEqual(result, expected_uri)
    
    def test_generate_presigned_url(self):
        """Test generate_presigned_url method"""
        expected_url = 'https://test-bucket.s3.amazonaws.com/test-object?signature=abc123'
        self.mock_s3_client.generate_presigned_url.return_value = expected_url
        
        object_key = 'data/test_data.json'
        expiration = 3600
        result = self.s3_manager.generate_presigned_url(object_key, expiration)
        
        self.mock_s3_client.generate_presigned_url.assert_called_once_with(
            'get_object',
            Params={
                'Bucket': self.bucket_name,
                'Key': object_key
            },
            ExpiresIn=expiration
        )
        
        self.assertEqual(result, expected_url)
    
    def test_download_file(self):
        """Test download_file method"""
        object_key = 'data/test_data.json'
        local_path = 'downloaded_test_data.json'
        result = self.s3_manager.download_file(object_key, local_path)
        
        self.mock_s3_client.download_file.assert_called_once_with(
            self.bucket_name, object_key, local_path
        )
        
        self.assertEqual(result, local_path)
    
    def test_list_objects(self):
        """Test list_objects method"""
        mock_response = {
            'Contents': [
                {'Key': 'data/file1.json'},
                {'Key': 'data/file2.json'},
                {'Key': 'data/file3.json'}
            ]
        }
        self.mock_s3_client.list_objects_v2.return_value = mock_response
        
        prefix = 'data/'
        result = self.s3_manager.list_objects(prefix)
        
        self.mock_s3_client.list_objects_v2.assert_called_once_with(
            Bucket=self.bucket_name,
            Prefix=prefix
        )
        
        expected_keys = ['data/file1.json', 'data/file2.json', 'data/file3.json']
        self.assertEqual(result, expected_keys)
    
    def test_list_objects_empty(self):
        """Test list_objects method with empty response"""
        mock_response = {}
        self.mock_s3_client.list_objects_v2.return_value = mock_response
        
        result = self.s3_manager.list_objects()
        
        self.assertEqual(result, [])
    
    def test_delete_object(self):
        """Test delete_object method"""
        object_key = 'data/test_data.json'
        result = self.s3_manager.delete_object(object_key)
        
        self.mock_s3_client.delete_object.assert_called_once_with(
            Bucket=self.bucket_name,
            Key=object_key
        )
        
        self.assertTrue(result)

if __name__ == '__main__':
    unittest.main()
