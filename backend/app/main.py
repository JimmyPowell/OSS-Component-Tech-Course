from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, course_resource, homework, showcase, showcase_comment, showcase_comment_reply, user_management, qiniu, announcement, forum_category, forum_post, forum_reply, like, notification, blog, batch_import

app = FastAPI(title="FastAPI Project Template")

# CORS Middleware
origins = [
    "http://localhost:5173",  # Allow your frontend origin
    "http://127.0.0.1:5173",
    "http://localhost:5174",  # Allow frontend on port 5174
    "http://127.0.0.1:5174",
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
api_router.include_router(user_management.router, prefix="/users", tags=["User Management"])
api_router.include_router(course_resource.router, prefix="/course-resources", tags=["Course Resources"])
api_router.include_router(course_resource.admin_router, prefix="/admin/course-resources", tags=["Admin Course Resources"])
api_router.include_router(homework.router, prefix="/homeworks", tags=["Homeworks"])
api_router.include_router(homework.admin_router, prefix="/admin/homeworks", tags=["Admin Homeworks"])
api_router.include_router(showcase.router, prefix="/showcases", tags=["Showcases"])
api_router.include_router(showcase.admin_router, prefix="/admin/showcases", tags=["Admin Showcases"])
api_router.include_router(showcase_comment.router, prefix="/showcase-comments", tags=["Showcase Comments"])
api_router.include_router(showcase_comment_reply.router, prefix="/showcase-comment-replies", tags=["Showcase Comment Replies"])
api_router.include_router(qiniu.router, prefix="/qiniu", tags=["Qiniu Cloud Storage"])
api_router.include_router(announcement.router, prefix="/announcements", tags=["Announcements"])
api_router.include_router(announcement.admin_router, prefix="/admin/announcements", tags=["Admin Announcements"])
api_router.include_router(forum_category.router, prefix="/forum/categories", tags=["Forum Categories"])
api_router.include_router(forum_category.admin_router, prefix="/admin/forum/categories", tags=["Admin Forum Categories"])
api_router.include_router(forum_post.router, prefix="/forum/posts", tags=["Forum Posts"])
api_router.include_router(forum_post.admin_router, prefix="/admin/forum/posts", tags=["Admin Forum Posts"])
api_router.include_router(forum_reply.router, prefix="/forum/replies", tags=["Forum Replies"])
api_router.include_router(forum_reply.admin_router, prefix="/admin/forum/replies", tags=["Admin Forum Replies"])
api_router.include_router(like.router, prefix="/likes", tags=["Likes"])
api_router.include_router(notification.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(notification.admin_router, prefix="/admin/notifications", tags=["Admin Notifications"])
api_router.include_router(blog.router, prefix="/blogs", tags=["Blogs"])
api_router.include_router(batch_import.router, prefix="/batch-import", tags=["Batch Import"])

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}
