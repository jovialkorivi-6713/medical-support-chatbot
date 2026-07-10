from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
from app.models.user import User
from app.models.chat import ChatSession
import logging

logger = logging.getLogger(__name__)

import certifi

async def init_db():
    try:
        # Create Motor client
        client = AsyncIOMotorClient(settings.MONGO_URI, tlsCAFile=certifi.where())
        
        # Initialize beanie with the User and ChatSession document classes
        await init_beanie(
            database=client.get_default_database(),
            document_models=[User, ChatSession]
        )
        logger.info("Successfully connected to MongoDB and initialized Beanie.")
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise e
