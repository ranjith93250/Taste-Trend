"""
Database connection and utilities
"""
from pymongo import MongoClient
import logging
from .config import MONGO_URI, DATABASE_NAME

logger = logging.getLogger(__name__)


class Database:
    """Singleton database connection"""
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            try:
                cls._client = MongoClient(MONGO_URI)
                cls._db = cls._client[DATABASE_NAME]
                # Test connection
                cls._client.admin.command('ping')
                logger.info(f"Successfully connected to MongoDB database: {DATABASE_NAME}")
            except Exception as e:
                logger.error(f"Failed to connect to MongoDB: {str(e)}")
                raise
        return cls._instance

    @property
    def users(self):
        """Get users collection"""
        return self._db.users

    @property
    def client(self):
        """Get MongoDB client"""
        return self._client

    @property
    def database(self):
        """Get database instance"""
        return self._db


# Create single database instance
db = Database()
