import time
import json
from fastapi.testclient import TestClient
import pytest
from src.models import Product

def test_cache_hit_miss(client: TestClient, redis_client):
    # 1. Create Product
    create_response = client.post(
        "/products/",
        json={"name": "Cache Test", "description": "Testing cache", "price": 50.0, "stock_quantity": 10}
    )
    product_id = create_response.json()["id"]

    # 2. First GET - Cache MISS (should set cache)
    # Check that key does NOT exist yet (or we can't really guarantee it doesn't without mocking, 
    # but in a clean integration env it shouldn't)
    
    response_1 = client.get(f"/products/{product_id}")
    assert response_1.status_code == 200
    
    # 3. Verify Redis has the key
    cached_data = redis_client.get(f"product:{product_id}")
    assert cached_data is not None
    cached_product = json.loads(cached_data)
    assert cached_product["id"] == product_id

    # 4. Manually modify cache to verify HIT (Demonstrate specific cache value returned)
    modified_cache_product = cached_product.copy()
    modified_cache_product["name"] = "Cached Name"
    redis_client.set(f"product:{product_id}", json.dumps(modified_cache_product))

    # 5. Second GET - Cache HIT
    response_2 = client.get(f"/products/{product_id}")
    assert response_2.status_code == 200
    assert response_2.json()["name"] == "Cached Name" # Should get the modified value from cache, not DB

def test_cache_invalidation_on_update(client: TestClient, redis_client):
    # 1. Create & Cache
    create_response = client.post(
        "/products/",
        json={"name": "Invalidate Update", "description": "Testing invalidation", "price": 60.0, "stock_quantity": 10}
    )
    product_id = create_response.json()["id"]
    client.get(f"/products/{product_id}") # Populate cache
    
    assert redis_client.get(f"product:{product_id}") is not None

    # 2. Update Product
    client.put(
        f"/products/{product_id}",
        json={"price": 65.0}
    )

    # 3. Verify Cache is Invalidated (Deleted)
    assert redis_client.get(f"product:{product_id}") is None

    # 4. Next GET should Refetch and Recache
    response = client.get(f"/products/{product_id}")
    assert response.json()["price"] == 65.0
    assert redis_client.get(f"product:{product_id}") is not None

def test_cache_invalidation_on_delete(client: TestClient, redis_client):
    # 1. Create & Cache
    create_response = client.post(
        "/products/",
        json={"name": "Invalidate Delete", "description": "Testing delete invalidation", "price": 70.0, "stock_quantity": 10}
    )
    product_id = create_response.json()["id"]
    client.get(f"/products/{product_id}") # Populate cache
    
    assert redis_client.get(f"product:{product_id}") is not None

    # 2. Delete Product
    client.delete(f"/products/{product_id}")

    # 3. Verify Cache is Invalidated
    assert redis_client.get(f"product:{product_id}") is None
