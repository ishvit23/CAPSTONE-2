from pymongo import MongoClient
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

def get_mongo_db():
    """Get MongoDB database connection with lazy initialization"""
    mongo_uri = os.getenv('MONGODB_URI') or getattr(settings, 'MONGODB_URI', 'mongodb://mongodb-service:27017')
    mongo_db_name = os.getenv('MONGODB_DB') or getattr(settings, 'MONGODB_DB', 'digibuddy')
    
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        db = client[mongo_db_name]
        # Test connection
        client.admin.command('ping')
        logger.info(f"Connected to MongoDB: {mongo_uri}/{mongo_db_name}")
        return db
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise

# Module-level lazy initialization
_mongo_db = None

def mongo_db():
    """Lazy singleton for MongoDB database - call this function to get the db"""
    global _mongo_db
    if _mongo_db is None:
        _mongo_db = get_mongo_db()
    return _mongo_db

