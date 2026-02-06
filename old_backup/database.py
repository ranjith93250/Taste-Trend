from pymongo import MongoClient
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

class Database:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017/")
            database_name = os.getenv("DATABASE_NAME", "restaurant_finder")
            
            logger.info(f"Connecting to MongoDB at {mongodb_url}")
            self._client = MongoClient(
                mongodb_url,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=30000,         # 30 second connection timeout
                socketTimeoutMS=45000           # 45 second socket timeout
            )
            
            # Test the connection
            self._client.server_info()
            self._db = self._client[database_name]
            
            # Create indexes
            self._db.users.create_index("email", unique=True)
            
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    @property
    def client(self):
        if self._client is None:
            self._initialize()
        return self._client

    @property
    def db(self):
        if self._db is None:
            self._initialize()
        return self._db

    @property
    def users(self):
        return self.db.users

# Create a singleton instance
db = Database()
