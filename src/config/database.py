import motor.motor_asyncio
from src.config.settings import MONGODB_URL

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)

db = client.product_microservice
