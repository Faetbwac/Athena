"""FastAPI application for Aegis."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Athena.Aegis.api.collector import router as collector_router


app = FastAPI(
    title="Aegis API",
    description="Knowledge Collection Enhancer for Athena",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(collector_router)


@app.get("/")
async def root():
    return {"message": "Aegis API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8484)