from fastapi.testclient import TestClient
from src.models import Product

def test_create_product(client: TestClient):
    response = client.post(
        "/products/",
        json={"name": "Test Product", "description": "A test description", "price": 10.0, "stock_quantity": 5}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Product"
    assert "id" in data

def test_get_product(client: TestClient):
    create_response = client.post(
        "/products/",
        json={"name": "Get Product", "description": "For getting", "price": 20.0, "stock_quantity": 10}
    )
    product_id = create_response.json()["id"]

    response = client.get(f"/products/{product_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == product_id
    assert data["name"] == "Get Product"

def test_get_product_not_found(client: TestClient):
    response = client.get("/products/non-existent-id")
    assert response.status_code == 404

def test_update_product(client: TestClient):
    create_response = client.post(
        "/products/",
        json={"name": "Update Product", "description": "Before update", "price": 30.0, "stock_quantity": 15}
    )
    product_id = create_response.json()["id"]

    update_response = client.put(
        f"/products/{product_id}",
        json={"price": 35.0, "stock_quantity": 20}
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["price"] == 35.0
    assert data["stock_quantity"] == 20
    assert data["name"] == "Update Product"

def test_delete_product(client: TestClient):
    create_response = client.post(
        "/products/",
        json={"name": "Delete Product", "description": "To be deleted", "price": 40.0, "stock_quantity": 5}
    )
    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404

# --- Input Validation Tests ---

def test_create_product_empty_name(client: TestClient):
    """POST with empty name should return 400"""
    response = client.post(
        "/products/",
        json={"name": "", "description": "Bad product", "price": 10.0, "stock_quantity": 5}
    )
    assert response.status_code == 400

def test_create_product_negative_price(client: TestClient):
    """POST with negative price should return 400"""
    response = client.post(
        "/products/",
        json={"name": "Bad Price", "description": "Negative price", "price": -5.0, "stock_quantity": 5}
    )
    assert response.status_code == 400

def test_create_product_negative_stock(client: TestClient):
    """POST with negative stock should return 400"""
    response = client.post(
        "/products/",
        json={"name": "Bad Stock", "description": "Negative stock", "price": 10.0, "stock_quantity": -1}
    )
    assert response.status_code == 400

def test_create_product_missing_fields(client: TestClient):
    """POST with missing required fields should return 400"""
    response = client.post(
        "/products/",
        json={"name": "Incomplete"}
    )
    assert response.status_code == 400

def test_update_product_negative_price(client: TestClient):
    """PUT with negative price should return 400"""
    create_response = client.post(
        "/products/",
        json={"name": "Valid Product", "description": "For validation test", "price": 10.0, "stock_quantity": 5}
    )
    product_id = create_response.json()["id"]

    update_response = client.put(
        f"/products/{product_id}",
        json={"price": -10.0}
    )
    assert update_response.status_code == 400
