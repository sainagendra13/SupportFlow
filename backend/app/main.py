from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.cache import close_cache
from app.config import settings
from app.database import connect_database, close_database
from app.routers import auth, tickets, comments, dashboard, admin, notifications
from fastapi import Request
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_database()
    yield
    await close_cache()
    await close_database()


app = FastAPI(
    title="SupportFlow API",
    lifespan=lifespan
)


@app.middleware("http")
async def verify_request_origin(request: Request, call_next):
    if (
        request.url.path.startswith("/api/")
        and request.method in ("POST", "PUT", "PATCH", "DELETE")
    ):
        origin = request.headers.get("origin")

        if origin not in settings.cors_origins:
            return JSONResponse(
                status_code=403,
                content={"detail": "Untrusted request origin"},
            )

    return await call_next(request)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(comments.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(notifications.router)

@app.get("/health")
async def health():
    return {"status": "healthy"}
