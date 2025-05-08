"""
Test script to verify S3 upload functionality using mocked boto3
"""
import json
import os
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from s3_manager import S3Manager
from mock_data import MOCK_STOCK_DATA

def test_s3_upload_functionality_with_mock():
    """Test S3 upload and related functionality using mocked boto3"""
    print("Testing S3 upload functionality with mocked boto3...")
    
    with open('test_stock_data.json', 'w') as f:
        json.dump(MOCK_STOCK_DATA, f, indent=4)
    print("Created test file: test_stock_data.json")
    
    mock_s3_client = MagicMock()
    
    mock_s3_client.generate_presigned_url.return_value = "https://test-bucket.s3.amazonaws.com/test-object?signature=abc123"
    
    with patch('boto3.client', return_value=mock_s3_client):
        s3_manager = S3Manager(bucket_name='test-stock-data-bucket')
        
        s3_uri = s3_manager.upload_file('test_stock_data.json', 'data/test_stock_data.json')
        print(f"File uploaded to: {s3_uri}")
        
        mock_s3_client.upload_file.assert_called_with(
            'test_stock_data.json', 'test-stock-data-bucket', 'data/test_stock_data.json'
        )
        
        data_uri = s3_manager.upload_data(list(MOCK_STOCK_DATA.values()), 'data/direct_upload.json')
        print(f"Data uploaded to: {data_uri}")
        
        assert mock_s3_client.put_object.called
        
        url = s3_manager.generate_presigned_url('data/test_stock_data.json')
        print(f"Presigned URL: {url}")
        
        mock_s3_client.generate_presigned_url.assert_called_with(
            'get_object',
            Params={
                'Bucket': 'test-stock-data-bucket',
                'Key': 'data/test_stock_data.json'
            },
            ExpiresIn=3600
        )
        
        try:
            s3_manager.upload_file('non_existent_file.txt')
            print("ERROR: Should have raised FileNotFoundError")
        except FileNotFoundError:
            print("Successfully caught FileNotFoundError for non-existent file")
        
        mock_s3_client.download_file.side_effect = ClientError(
            {'Error': {'Code': '404', 'Message': 'Not Found'}},
            'download_file'
        )
        
        try:
            s3_manager.download_file('data/missing_file.json', 'downloaded_missing.json')
            print("ERROR: Should have raised ClientError")
        except ClientError:
            print("Successfully caught ClientError for missing S3 object")
    
    print("S3 upload functionality test completed successfully!")
    return True

if __name__ == "__main__":
    test_s3_upload_functionality_with_mock()
