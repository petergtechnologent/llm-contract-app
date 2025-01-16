from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine
from .models import Base
from .routers import contracts

# Create DB tables (for demo; in production, use migrations)
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Enable CORS if you're calling from a separate frontend (e.g., http://localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production restric to domain, dev: http://localhost:3000 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include our contract-related routes with a consistent prefix
app.include_router(contracts.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the Contract Review API"}
