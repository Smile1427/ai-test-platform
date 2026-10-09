from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import user, course, order, ai, comment

Base.metadata.create_all(bind=engine)

app = FastAPI(title="在线教育平台", description="AI辅助测试被测系统")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/api/user", tags=["用户"])
app.include_router(course.router, prefix="/api/course", tags=["课程"])
app.include_router(order.router, prefix="/api/order", tags=["订单"])
app.include_router(comment.router, prefix="/api/comment", tags=["评论"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI功能"])


@app.get("/")
def root():
    return {"message": "在线教育平台运行中"}