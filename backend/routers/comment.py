from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Comment, User, Course, Order
from pydantic import BaseModel

router = APIRouter()


class CommentReq(BaseModel):
    user_id: int
    course_id: int
    content: str


@router.post("/add")
def add_comment(req: CommentReq, db: Session = Depends(get_db)):
    # ★ 先校验内容（放在最前面，避免被其他逻辑跳过）
    print(f"评论内容长度：{len(req.content)}")
    if not req.content or len(req.content.strip()) == 0:
        raise HTTPException(status_code=400, detail="评论内容不能为空")
    if len(req.content) > 500:
        raise HTTPException(status_code=400, detail="评论内容不能超过500字")

    # 校验用户
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 校验课程
    course = db.query(Course).filter(Course.id == req.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    # 校验是否购买过该课程
    purchased = db.query(Order).filter(
        Order.user_id == req.user_id,
        Order.course_id == req.course_id
    ).first()
    if not purchased:
        raise HTTPException(status_code=403, detail="请先购买该课程后再评论")

    comment = Comment(user_id=req.user_id, course_id=req.course_id, content=req.content)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"comment_id": comment.id, "message": "评论成功"}


@router.get("/list/{course_id}")
def list_comments(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    results = db.query(Comment, User.username).join(User, Comment.user_id == User.id)\
        .filter(Comment.course_id == course_id)\
        .order_by(Comment.created_at.desc()).all()

    return [
        {
            "id": c.id,
            "username": username,
            "content": c.content,
            "likes": c.likes,
            "created_at": c.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for c, username in results
    ]


@router.delete("/delete/{comment_id}")
def delete_comment(comment_id: int, user_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权删除他人评论")
    db.delete(comment)
    db.commit()
    return {"message": "删除成功"}


@router.post("/like/{comment_id}")
def like_comment(comment_id: int, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    comment.likes += 1
    db.commit()
    return {"likes": comment.likes}

@router.delete("/clean_test_data")
def clean_test_data(db: Session = Depends(get_db)):
    """测试专用：清理测试评论"""
    db.query(Comment).filter(Comment.user_id == 1).delete()
    db.commit()
    return {"message": "已清理"}