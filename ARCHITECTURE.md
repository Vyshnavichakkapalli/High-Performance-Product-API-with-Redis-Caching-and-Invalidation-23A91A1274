# System Architecture

## Overview

The High-Performance Product API is designed to handle high read loads by leveraging Redis as a caching layer in front of a persistent database. The system follows the **Cache-Aside** pattern to ensure data consistency and performance.

## System Components

```
┌──────────┐      ┌──────────────────┐      ┌───────────┐
│          │ HTTP │                  │      │           │
│  Client  │─────>│  FastAPI Service │─────>│   Redis   │
│          │<─────│   (Port 8080)    │<─────│  (Cache)  │
│          │      │                  │      │           │
└──────────┘      └────────┬─────────┘      └───────────┘
                           │
                           │ SQLModel
                           v
                    ┌──────────────┐
                    │   SQLite DB  │
                    │  (Persistent)│
                    └──────────────┘
```

## Data Flow

### Read Path (GET /products/{id})

The read path prioritizes the cache to reduce database load:

1. Client sends `GET /products/{id}`
2. API checks Redis for key `product:{id}`
3. **Cache Hit**: Return cached data immediately
4. **Cache Miss**: Query SQLite DB → Store result in Redis with TTL → Return data

### Write Path (POST, PUT, DELETE)

The write path ensures data consistency:

1. Client sends a write request
2. API modifies the primary database first
3. API invalidates (deletes) the corresponding Redis key
4. Next read will fetch fresh data from DB and re-cache it

## Design Decisions

### Why Cache-Aside?
- **Resilience**: If Redis fails, the system gracefully degrades to database-only mode
- **Flexibility**: Only requested data is cached, preventing unused data from filling the cache
- **Consistency**: Immediate invalidation on write ensures subsequent reads get fresh data

### Why Redis?
- **Performance**: In-memory storage offers sub-millisecond latency
- **Simplicity**: Key-Value store fits the JSON document model perfectly
- **TTL Support**: Built-in expiration provides eventual consistency as a safety net

### Why SQLite?
- **Zero Configuration**: No additional database service needed
- **Portability**: Single file database, easy to manage in containers
- **Focus**: Keeps the focus on Redis caching rather than database setup

### Error Handling Strategy
- **Redis Down**: Application falls back to direct database queries (logs the error)
- **Invalid Input**: Returns 400 Bad Request with descriptive error messages
- **Not Found**: Returns 404 with clear error detail
- **Server Errors**: Returns 500 with generic error message (details logged server-side)
