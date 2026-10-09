from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from pydantic import BaseModel
from jose import jwt
from passlib.hash import bcrypt
import redis
import re

router = APIRouter()
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
SECRET_KEY = "edu-platform-secret"

class RegisterReq(BaseModel):
    username: str
    password: str

class LoginReq(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(req: RegisterReq, db: Session = Depends(get_db)):
    # 校验用户名
    if not re.match(r'^[a-zA-Z0-9_]{6,20}$', req.username):
        raise HTTPException(status_code=400, detail="用户名必须是6-20位字母数字下划线")
    # 校验密码
    if len(req.password) < 6 or len(req.password) > 20:
        raise HTTPException(status_code=400, detail="密码长度必须是6-20位")

    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    user = User(username=req.username, password=bcrypt.hash(req.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "注册成功", "user_id": user.id}

@router.post("/login")
def login(req: LoginReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not bcrypt.verify(req.password, user.password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = jwt.encode({"user_id": user.id, "role": user.role}, SECRET_KEY, algorithm="HS256")
    redis_client.setex(f"token:{user.id}", 3600, token)
    return {"token": token, "role": user.role, "user_id": user.id}
