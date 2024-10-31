import os
from pathlib import Path
import base64

# Base directory configuration
BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"

# Database configuration (MySQL)
MYSQL_CONFIG = {
    "host": "ec2-13-212-9-190.ap-southeast-1.compute.amazonaws.com",
    "port": 3306,
    "database": "pioneerDB",
    "user": "root",
    "password": "pioneerdb",
    "pool_size": 5,
    "pool_name": "mypool",
    "charset": "utf8mb4",
    "collation": "utf8mb4_general_ci"
}

# PostgreSQL configuration
POSTGRES_CONFIG = {
    "host": "pioneer-database.cjxzjcqxbfvh.ap-southeast-1.rds.amazonaws.com",
    "port": 5432,
    "database": "pioneer_database",
    "user": "postgres",
    "password": "pioneer123"
}

# SSL Configuration
SSL_KEY_BASE64 = """LS0tLS1CRUdJTiBSU0EgUFJJVkFURSBLRVktLS0tLQpNSUlFb3dJQkFBS0NBUUVBb2JBRTg2WkpqcXBpTVVZck4zRWE4NTQ1UGRhK25oUmtIMUM1YlVJc0djb1VEK0F5CkN2N0huUm44eW42RGovaUJ6azNJZVhuSTUyNm1kT0NvcmRjc2NmNDhZSVhMNGVoYXNlbUJxTHhsMjk3ZlNmUzEKUWFLT05MR1lNekR2MWFxTjJkdnR3bEtGdEJiYUQ3SFNad1Q5eE9kNk0wNkxFTUwvYUVVRi84MjRVSXFiUkJmSgpNaFFRU0pSYkJzcnBGWkM4L0dlVUZid3N4MWNOU2k2REVuQ2JiUkcwbkp0ZFhub1VscXFBbmwrZzVOMDRwNnFLCnFXdlFVNFZ5a0E0N0JDUXkyTEx4azlWcDN5dDVoZjZjYk1SeXpXaVRVdmp1Q3hZSmhXMjhwWEpKbEJJRC9wZ1AKKzNJM2pXK3haZnV5dTJsbUNnTnlpY2taSWtlQmlKMmJhSzF5aFFJREFRQUJBb0lCQUdrOEprenEydzlYQ0Nmbgo4ckxZRStHaUJzR2Y1bHIvREpkeE0rN1AxZUpIS3oyVi94dzI3WGJyOWlOWnFvbG5CaDFmZE83VGZCWmRaMHZFCitTU0VXdklxdGVOZzBlMU1ETk9sRm5YYmdUUlUzK0hEdXNGb2FzUVRIdXVhbTA3bS9nSmc2V1BEMERBQmU1WWgKZDc4RGVhUFJ3VEJwbTR1aVR4ZnZiTk1zY3gwL3ZwR2hoeldGRkZhOG1LV000SWFnN1hBcEQzOUNuNmloQ1gvRQpBRmxoQmc0WElxNnhJakE4ZTBpZDQ4Y3B4S2dNaDBIRGZqZXBnNktaWlZFZFpXSFlaWjhXVDcxeWlEcFFYTXB4Cm02WXBVMzlsR1R6a3RBZjZQNkRKMk1HTWJmcU0rNVZleXJ6elVPQzdOK2xZMS9peUx6N3duNENJS3c3WGxQV0IKeEJsWERWVUNnWUVBNXRPWnArZEpld05ESVczSFJGQ2k3ajBXNlZhUXBvTURkN21xaUdEb3pQV1k3V25lTThQYwpJenA5V3FWTUk5cDkwMHIrOUIxUmNsWUhuc3VxUzhleEtJL3NZR0luSXNYaWtPVmJnVGN3KzQ4YVFiN1dMS085CkpuNENQREprb3ZYbnhqbHBOK1A4VFBjZndMbzhhWTFSUzE5blFXS1NWOHJjbWt5blNveGdEWGNDZ1lFQXMxSWsKVGZBbGxqbmoreGI1T1cxSE8wM3lkaFlnaDZ0MTVSVFpSaDZza2VqUlVORWVDU1VXdkJiQ3BaZHVvV1RBRUFMSwppMjVxRy9LTTRzWXhUVHQ5aldBT2NhQjdQMnJuVUwwMjdSZ1QvNzJKZ2xGcWRxck1TR0p0REFKY0FVOEtJMEM4CmpGY3BaWDZXVXRGK05VbVJtSUlUYVhXcldIZi9KUjNhaE1TakR1TUNnWUVBcnpzRDh3c0tKWENjamN3ZzhpT2wKRE9jamRaQlp6NDYyR3pXLzJEaDVndDhQY1d4bFd6YmM3NEYvbUVqVVBJT3A4YldGUnh6YXI4blBqeVZkNnBsMgpUQ3kyYlpVVjBMZ1kvNWFlbU1HbFZkT1ZRMFAwbzM3S0lXYVhtOHRGeXRDVFcxQktLRHZUVlRwbHlKR1pPeWdsCkJ1c3VIOTBNNjhqOUg4WUJXZjZuREpFQ2dZQU9HQk93YUlLYnh4c0xIaWdpZ2x0SjV2dDZtb3lkL1RUNzkyS0kKWjFySzhSQ2FtSVVTMU81dmhCNXlZMitYa2RLaXI0VjU1Z2pDLzVKaE5KQ2xjRnFTNVF6ZGsyNThjb3VSeGYxdQpMeWxMUFh0MFdhL1RlZU1xZ1VudTJyU2VpYmJUUklCTlM0QitjSytoL01NOXJ2V1psZ2V1ajBnVFlRTVZ5TDNuCkY0bDFYd0tCZ0g0U2ppR1NQdWZTZlVQUHl1SVlXT2E1cm1jMTduOUM5ZFEwTW13dExtZnhtMjFveFFLU3N6RTYKdVR1YkZENWVPZXN0T2FwQTd4QUREQWZLNUoxMXdDaFJiaDJmRGd5MmMzRjVpc2kyQWF2V1B2KzU5MVBRU2pJWgpPK1NEdmxyck11OUw4UHh6UFZiaHBEdGYxTkwrbmVVL0lHQXV0bC8yb3pYb2F6VW5yZURUCi0tLS0tRU5EIFJTQSBQUklWQVRFIEtFWS0tLS0t"""

# Firebase configuration
FIREBASE_CONFIG = {
    "type": "service_account",
    "project_id": "pioneer-43aee",
    "private_key_id": "56b321bf670f77dd907c82f0adff0fce1f3ec90d",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC4pFVv8b/zg1Iv\nON+I+GUAwvBAMHLzBG2l2V21tZn3MSYshEhqTFCYq2q1AL28jB6lUp6zyB1OONZO\nCgK/yhsZBQxgxEs88DZoCxcLxIjx+QbbqavFT/l+/zGjLbVyd2rL+WRJPXDBJfJV\nEk3UDwgh82HpV5pmYhCJFAY9STh88mfF1kaIw3hDD9SHcnecAMTMmXXp2dqcKJkg\nZ4eW8pjc4REpKzjBrFCC0paMa4jc1kIkGdEbbDtkMIiACFsSwOYoMbLI+gOCLjuw\nDwFJcwL8mBV4M8DFJe60YWWi1kptp5ji0WbIv8fCupxdgymz7QBrDTyAnpGNn73p\nvh6BXkSFAgMBAAECggEAKb61tk6A6GxbS2PfXhdStp5cNRb/FiR9Kc8AGdIKElIh\nYFU0Dhxc6Hdw86VMQHGpiBUq3lizD3lYMmKfBn+KKtjyWHpozEk+87z2I+n2UEbO\nHyG4PS78qJLHxS3TZSLMmXs0Cj8C3BhZNpSh1fzkCND+5QOyW812EZfeZULFq7G8\nHv6lJvz/+U+0RlA2uisui2CYZubZup+vd5nnGxa2Sx+vk55vpDdw4o3ojKgqh29j\nI+AFqNAXVIXanEg+Z6XOUeZv3DQ7k3e702s3zG8HzChfoYBjAcQ9ZB8jJTAHbxRN\nQbbIJo6XPK9lVf97d4OVKNvVq9f0qHc97wLcabhB7QKBgQDfERTFq3/pvG1SNuCF\ncPYY+Xu+Cc34IEl02JTkF/V1qqJXaY73Ni3TehvXESkSqjJrB7yK6/+sVQIpPJq1\nog2UTJZwjMNrSSysvzzXEfVz70jsLfnKaXBwiWBM3wk+s0kyZauKDWo3W3ygBQGx\nvNDg/881ZFvJv0xavB03T9BIUwKBgQDT5vfbDxblKr3ZYCDu9xcHjuto/roQqIbV\nyL2iY/Pnm/LmZ8nzTSNqznDKLwlSbFBGzhPRh98j8h4GfU9u8vOXqfAhNPjvaO2q\nvMw8KCI+VBeMf82xayaWm/1cNd0aZQo8b23O0UxgQ3eE7zhXqBCNbyE8AJJRNMzO\ncxZh58BExwKBgQC0W349GR5SYUzO5ZoBqsUAim+XxxunHIvoEtnH1utbWTzrimjS\nzxacX6W07aYU9lHPojC67ngJ4a3eo6a/ZyitmIMmu1miHEcn4XQSvO2F8Jo4hC/s\njfYgt6KKZOd3r8RmIDhjZddUrP8F7yZgjDcjRRJHrD5ez/KvhlvlBf51CwKBgHod\nuOi9IWyf3RjQlSohq1vnuTKg2YmQFWROczqKb50h+jFdzrwv0CFVJxrdUHn3gavM\nRw+RRb7pYPRMcuJ1kHvuqzv30x3lUlH6y5g/aLySqZ+GZ3u/TFWvP6tMP0dewy9g\n598wLturBc3OLqIVcLSRPo3dpnS2APFY0aVKcTsxAoGBANG/QrClhbwNt8S1UHxH\nZlcjT5tOevR854bi/PYUt7nJCQOxK4YqsgNUV117H17uAH+PpR9595XyBwbC8M3j\n/wrEzB5Ft06w6kAXO0MNXgfg4/5AcPvW3VMjRspYEsv3MJBAEN5U+8TfV86FT3Ew\n29WEJarvGUCSvhoNpVfMEtZ/\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-ossu1@pioneer-43aee.iam.gserviceaccount.com",
    "client_id": "112568681181913227285",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ossu1%40pioneer-43aee.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com",
    "storage_bucket": "pioneer-43aee.appspot.com"
}

# Storage configuration
STORAGE_CONFIG = {
    "max_age_days": 7,
    "max_size_mb": 500,
    "allowed_extensions": [".pdf", ".txt"]
}

# API configuration
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 5106,
    "cors_origins": ["http://localhost:3000"]  # Add more origins as needed
}

# Logging configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "filename": str(STORAGE_DIR / "app.log")
}

# Create necessary directories
def create_directories():
    """Create necessary directories if they don't exist"""
    directories = [
        STORAGE_DIR,
        STORAGE_DIR / "pdf_uploads",
        STORAGE_DIR / "txt_outputs",
        STORAGE_DIR / "logs"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Environment-specific configurations
def get_environment_config():
    """Get environment-specific configuration"""
    env = os.getenv("PIONEER_ENV", "development")
    
    if env == "production":
        return {
            "debug": False,
            "testing": False,
            "db_pool_size": 20
        }
    elif env == "testing":
        return {
            "debug": True,
            "testing": True,
            "db_pool_size": 5
        }
    else:  # development
        return {
            "debug": True,
            "testing": False,
            "db_pool_size": 10
        }

# Initialize environment config
ENV_CONFIG = get_environment_config()

# Validate configuration
def validate_config():
    """Validate critical configuration settings"""
    # Check Firebase credentials
    firebase_creds = Path(FIREBASE_CONFIG["credential_path"])
    if not firebase_creds.exists():
        raise FileNotFoundError(
            f"Firebase credentials not found at: {firebase_creds}\n"
            f"Please ensure the credentials file exists at the specified location."
        )
    
    # Check storage directories
    create_directories()
    
    # Validate database configuration
    required_db_keys = ["host", "port", "database", "user", "password"]
    missing_keys = [key for key in required_db_keys if key not in DB_CONFIG]
    if missing_keys:
        raise KeyError(f"Missing required database configuration keys: {missing_keys}")

# Export all configurations
__all__ = [
    'BASE_DIR',
    'STORAGE_DIR',
    'DB_CONFIG',
    'FIREBASE_CONFIG',
    'STORAGE_CONFIG',
    'API_CONFIG',
    'LOGGING_CONFIG',
    'ENV_CONFIG',
    'create_directories',
    'validate_config'
]