from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, leads, webhooks

app = FastAPI(title="EchoIQ Labs API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(health.router)
app.include_router(leads.router)
app.include_router(webhooks.router)
