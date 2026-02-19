from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from src.db import create_db_and_tables
from src.seeds import seed_db
from src.routes import products

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_db()
    yield

app = FastAPI(
    title="High-Performance Product API",
    description="Product API with Redis Caching and Invalidation",
    version="1.0.0",
    lifespan=lifespan
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Return 400 Bad Request instead of 422 for validation errors."""
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({"field": field, "message": error["msg"]})
    return JSONResponse(
        status_code=400,
        content={"detail": "Validation error", "errors": errors}
    )

app.include_router(products.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
