from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth

app = FastAPI(title="FastAPI Project Template")

# CORS Middleware
origins = [
    "http://localhost:5173",  # Allow your frontend origin
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main router with /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
