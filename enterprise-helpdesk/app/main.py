from fastapi import FastAPI

from app.routes.auth import router as auth_router
from app.routes.comments import router as comments_router
from app.routes.reports import router as reports_router
from app.routes.tickets import router as tickets_router

app = FastAPI(
    title="Enterprise Helpdesk API",
    version="1.0.0",
    description="A junior-friendly enterprise ticket management backend.",
)

app.include_router(auth_router)
app.include_router(tickets_router)
app.include_router(comments_router)
app.include_router(reports_router)


@app.get("/")
def home():
    return {
        "message": "Enterprise Helpdesk API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
