# app/services/service_manager.py
from typing import Optional
from app.services.elasticsearch_service import ElasticsearchService
from app.services.product_service import ProductService
from app.services.coupon_service import CouponService
from app.services.redis_service import RedisService

class ServiceManager:
    _instance = None
    _es_service: Optional[ElasticsearchService] = None
    _product_service: Optional[ProductService] = None
    _coupon_service: Optional[CouponService] = None
    _redis_service: Optional[RedisService] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_es_service(self) -> ElasticsearchService:
        if self._es_service is None:
            self._es_service = ElasticsearchService()
        return self._es_service
    
    def get_product_service(self) -> ProductService:
        if self._product_service is None:
            self._product_service = ProductService(es_service=self.get_es_service())
        return self._product_service
    
    def get_coupon_service(self) -> CouponService:
        if self._coupon_service is None:
            self._coupon_service = CouponService(es_service=self.get_es_service())
        return self._coupon_service
    
    def get_redis_service(self) -> RedisService:
        if self._redis_service is None:
            self._redis_service = RedisService()
        return self._redis_service
    
    async def close_all(self):
        """Close all services"""
        if self._es_service:
            await self._es_service.close()
        if self._product_service:
            await self._product_service.close()
        if self._coupon_service:
            await self._coupon_service.close()
        if self._redis_service:
            await self._redis_service.close()

# Global instance
service_manager = ServiceManager()