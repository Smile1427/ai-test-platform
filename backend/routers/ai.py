from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from services.ai_service import AIService
from services.study_analysis import StudyAnalyzer
from pydantic import BaseModel
import config
from fastapi import HTTPException


router = APIRouter()

ai_service = AIService(api_key=config.ZHIPU_API_KEY)
study_analyzer = StudyAnalyzer(api_key=config.ZHIPU_API_KEY)


class ContentReq(BaseModel):
    topic: str


class ChatReq(BaseModel):
    question: str
    user_id: int = None


@router.post("/generate")
def generate_content(req: ContentReq):
    try:
        return {"content": ai_service.generate_course_intro(req.topic)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/recommend/{user_id}")
def recommend(user_id: int, db: Session = Depends(get_db)):
    try:
        return {"courses": ai_service.recommend_courses(user_id, db)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/chat")
def chat(req: ChatReq, db: Session = Depends(get_db)):
    try:
        return {"answer": ai_service.chat(req.question, req.user_id, db)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analysis/{user_id}")
def analysis(user_id: int, db: Session = Depends(get_db)):
    try:
        return study_analyzer.analyze(user_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))