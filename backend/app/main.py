from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import minifigs, sets, stats, themes
from app.core.config import settings

app = FastAPI(
    title="BrickViewer API",
    description="LEGO set database powered by Rebrickable data",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sets.router, prefix="/api")
app.include_router(themes.router, prefix="/api")
app.include_router(minifigs.router, prefix="/api")
app.include_router(stats.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}
