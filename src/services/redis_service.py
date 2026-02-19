import redis
import json
import logging
from typing import Optional
from src.config import settings
from src.models import Product

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisService:
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True
            )
            self.redis_client.ping()
            logger.info("Successfully connected to Redis.")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None

    def get_product(self, product_id: str) -> Optional[Product]:
        if not self.redis_client:
            return None
        
        try:
            cached_data = self.redis_client.get(f"product:{product_id}")
            if cached_data:
                logger.info(f"Cache HIT for product {product_id}")
                return Product.model_validate_json(cached_data)
        except redis.RedisError as e:
            logger.error(f"Redis error getting product {product_id}: {e}")
        
        logger.info(f"Cache MISS for product {product_id}")
        return None

    def set_product(self, product: Product):
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(
                f"product:{product.id}",
                settings.CACHE_TTL_SECONDS,
                product.model_dump_json()
            )
            logger.info(f"Cached product {product.id}")
        except redis.RedisError as e:
            logger.error(f"Redis error setting product {product.id}: {e}")

    def invalidate_product(self, product_id: str):
        if not self.redis_client:
            return

        try:
            self.redis_client.delete(f"product:{product_id}")
            logger.info(f"Invalidated cache for product {product_id}")
        except redis.RedisError as e:
            logger.error(f"Redis error invalidating product {product_id}: {e}")

redis_service = RedisService()
