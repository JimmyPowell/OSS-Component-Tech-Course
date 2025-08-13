from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, course_resource, homework, showcase, showcase_comment, showcase_comment_reply

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
api_router.include_router(course_resource.router, prefix="/course-resources", tags=["Course Resources"])
api_router.include_router(homework.router, prefix="/homeworks", tags=["Homeworks"])
api_router.include_router(showcase.router, prefix="/showcases", tags=["Showcases"])
api_router.include_router(showcase_comment.router, prefix="/showcase-comments", tags=["Showcase Comments"])
api_router.include_router(showcase_comment_reply.router, prefix="/showcase-comment-replies", tags=["Showcase Comment Replies"])

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
