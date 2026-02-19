# High-Performance Product API

A high-performance backend API service for managing a product catalog, leveraging Redis for robust caching and efficient data retrieval.

## Features

- **Product Management**: Full CRUD operations for products
- **Cache-Aside Strategy**: Efficiently caches product data in Redis to minimize database load
- **Cache Invalidation**: Automatically invalidates cache on updates and deletions
- **Input Validation**: Validates all inputs with descriptive 400 Bad Request errors
- **Graceful Degradation**: Falls back to database if Redis is unavailable
- **Dockerized**: Fully containerized with Docker Compose
- **Auto-Seeding**: Database is seeded with 5 sample products on startup

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: SQLModel (SQLite)
- **Cache**: Redis 6
- **Testing**: Pytest (8 tests)

## Setup and Installation

### Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) and Docker Compose

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd High-Performance-Product-API-with-Redis-Caching-and-Invalidation-23A91A1274
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   ```

3. **Start the Application:**
   ```bash
   docker-compose up --build
   ```
   The API will be available at `http://localhost:8080`.

## API Documentation

Interactive docs available at:
- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

### Endpoints

| Method | Path | Description | Status |
| :--- | :--- | :--- | :--- |
| `POST` | `/products/` | Create a new product | `201 Created` |
| `GET` | `/products/{id}` | Get product by ID (Cached) | `200 OK` / `404` |
| `PUT` | `/products/{id}` | Update product & invalidate cache | `200 OK` / `404` |
| `DELETE` | `/products/{id}` | Delete product & invalidate cache | `204 No Content` / `404` |

### Example Requests & Responses

#### Create a Product
```bash
curl -X POST http://localhost:8080/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Wireless Mouse", "description": "Ergonomic wireless mouse", "price": 29.99, "stock_quantity": 100}'
```
**Response (201 Created):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse",
  "price": 29.99,
  "stock_quantity": 100
}
```

#### Get a Product (with Caching)
```bash
curl http://localhost:8080/products/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```
**Response (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse",
  "price": 29.99,
  "stock_quantity": 100
}
```
- **First call**: Cache MISS → fetches from DB, stores in Redis
- **Subsequent calls**: Cache HIT → returns from Redis directly

#### Update a Product
```bash
curl -X PUT http://localhost:8080/products/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Content-Type: application/json" \
  -d '{"price": 24.99, "stock_quantity": 85}'
```
**Response (200 OK):**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Wireless Mouse",
  "description": "Ergonomic wireless mouse",
  "price": 24.99,
  "stock_quantity": 85
}
```
Cache is automatically invalidated after the update.

#### Delete a Product
```bash
curl -X DELETE http://localhost:8080/products/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```
**Response: 204 No Content** (empty body)

Cache is automatically invalidated after deletion.

#### Validation Error (400 Bad Request)
```bash
curl -X POST http://localhost:8080/products/ \
  -H "Content-Type: application/json" \
  -d '{"name": "", "description": "Bad product", "price": -5, "stock_quantity": -1}'
```
**Response (400 Bad Request):**
```json
{
  "detail": "Validation error",
  "errors": [
    {"field": "name", "message": "Value error, Product name must not be empty"},
    {"field": "price", "message": "Value error, Price must be greater than zero"},
    {"field": "stock_quantity", "message": "Value error, Stock quantity must not be negative"}
  ]
}
```

## Running Tests

```bash
docker-compose exec api-service python -m pytest tests/ -v
```

**Test Results (8/8 passing):**
```
tests/integration/test_caching.py::test_cache_hit_miss                  PASSED
tests/integration/test_caching.py::test_cache_invalidation_on_update    PASSED
tests/integration/test_caching.py::test_cache_invalidation_on_delete    PASSED
tests/unit/test_api.py::test_create_product                             PASSED
tests/unit/test_api.py::test_get_product                                PASSED
tests/unit/test_api.py::test_get_product_not_found                      PASSED
tests/unit/test_api.py::test_update_product                             PASSED
tests/unit/test_api.py::test_delete_product                             PASSED
```

## Caching Strategy

### Cache-Aside Pattern
1. **Read (GET)**: Check Redis first → HIT: return cached data → MISS: fetch from DB, cache with TTL, return
2. **Write (POST/PUT/DELETE)**: Modify DB first → invalidate Redis key → subsequent reads will re-cache

### Error Resilience
If Redis is unavailable, the application gracefully falls back to direct database queries, logging the cache error but continuing to serve requests.

### TTL Management
Cache entries expire after a configurable TTL (`CACHE_TTL_SECONDS`, default: 3600s). This prevents stale data even if invalidation fails.

## Project Structure

```
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py             # Environment-based configuration
│   ├── db.py                 # Database connection & sessions
│   ├── models.py             # Product data models with validation
│   ├── seeds.py              # Database seeding (5 sample products)
│   ├── routes/
│   │   └── products.py       # CRUD API endpoints
│   └── services/
│       └── redis_service.py  # Redis cache operations
├── tests/
│   ├── unit/test_api.py             # 5 endpoint tests
│   └── integration/test_caching.py  # 3 cache behavior tests
├── Dockerfile                # Multi-stage build
├── docker-compose.yml        # API + Redis orchestration
├── ARCHITECTURE.md           # System design & decisions
├── .env.example              # Environment variable template
├── requirements.txt          # Python dependencies
└── README.md
```

## Design Decisions

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design, data flow diagrams, and rationale behind technology choices.

## Screenshots

> **Note**: Use `http://localhost:8080/docs` (Swagger UI) to interact with the API visually. Run `docker-compose exec redis redis-cli monitor` in a separate terminal to observe Redis cache activity in real-time.

## Video Demo

> **Link**: _[Add your video demo link here]_