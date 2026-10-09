from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Course, User
from pydantic import BaseModel
import redis

router = APIRouter()
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)


class CreateOrderReq(BaseModel):
    user_id: int
    course_id: int


@router.post("/create")
def create_order(req: CreateOrderReq, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == req.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    course = db.query(Course).filter(Course.id == req.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")

    existing = db.query(Order).filter(
        Order.user_id == req.user_id,
        Order.course_id == req.course_id,
        Order.status != "cancelled"
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="您已购买过该课程，请勿重复购买")

    # ★ 新增：库存校验
    stock_key = f"stock:course:{req.course_id}"
    if not redis_client.exists(stock_key):
        redis_client.set(stock_key, course.stock)

    current_stock = int(redis_client.get(stock_key))
    if current_stock <= 0:
        raise HTTPException(status_code=400, detail="库存不足")

    remaining = redis_client.decr(stock_key)
    if remaining < 0:
        redis_client.incr(stock_key)
        raise HTTPException(status_code=400, detail="库存不足")

    order = Order(user_id=req.user_id, course_id=req.course_id, amount=course.price)
    db.add(order)
    db.commit()
    db.refresh(order)
    return {"order_id": order.id, "status": order.status}


@router.get("/list/{user_id}")
def list_orders(user_id: int, page: int = 1, size: int = 10, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    if page < 1 or size < 1:
        raise HTTPException(status_code=400, detail="页码和每页数量必须是正整数")

    offset = (page - 1) * size
    results = db.query(Order, Course.title).join(Course, Order.course_id == Course.id)\
        .filter(Order.user_id == user_id)\
        .order_by(Order.created_at.desc())\
        .offset(offset).limit(size).all()

    total = db.query(Order).filter(Order.user_id == user_id).count()

    return {
        "page": page,
        "size": size,
        "total": total,
        "data": [
            {
                "order_id": o.id,
                "course_id": o.course_id,
                "course_title": title,
                "amount": o.amount,
                "status": o.status,
                "created_at": o.created_at.strftime("%Y-%m-%d %H:%M:%S")
            }
            for o, title in results
        ]
    }


@router.post("/cancel/{order_id}")
def cancel_order(order_id: int, user_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != user_id:
        raise HTTPException(status_code=403, detail="无权操作他人订单")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="只有待支付的订单才能取消")

    order.status = "cancelled"
    # 恢复库存
    stock_key = f"stock:course:{order.course_id}"
    redis_client.incr(stock_key)
    db.commit()
    return {"message": "订单已取消"}