from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Course

router = APIRouter()

@router.get("/list")
def list_courses(page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="页码和每页数量必须是正整数")
    courses = db.query(Course).offset((page-1)*size).limit(size).all()
    return {"page": page, "size": size, "data": courses}

@router.get("/{course_id}")
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        return {"error": "课程不存在"}
    return course