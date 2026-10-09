"""AI学习记录分析"""
from zai import ZhipuAiClient
from sqlalchemy.orm import Session
from models import Order, Course, Comment, User


class StudyAnalyzer:
    def __init__(self, api_key: str):
        self.client = ZhipuAiClient(api_key=api_key)

    def analyze(self, user_id: int, db: Session) -> dict:
        """分析用户学习记录，返回AI建议"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        # 查询用户的订单
        orders = db.query(Order, Course.title).join(Course, Order.course_id == Course.id)\
            .filter(Order.user_id == user_id).all()

        # 查询用户的评论数
        comment_count = db.query(Comment).filter(Comment.user_id == user_id).count()

        # 组装学习记录
        purchased = []
        pending = []
        for order, title in orders:
            if order.status == "paid":
                purchased.append(title)
            elif order.status == "pending":
                pending.append(title)

        # 构建Prompt
        prompt = f"""你是一个学习顾问。请根据以下用户的学习记录，分析学习情况并给出3条个性化建议。

【用户信息】
用户名：{user.username}

【已购买课程】
{', '.join(purchased) if purchased else '暂无'}

【待支付课程】
{', '.join(pending) if pending else '暂无'}

【发表评论数】
{comment_count} 条

【要求】
1. 分析该用户的学习情况（学习方向、活跃度、专注度）
2. 给出3条具体可执行的建议
3. 语言亲切自然，像老师对学生说话
4. 直接返回分析文本，不要用markdown标记

请直接返回分析结果。"""

        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5
            )
            analysis = response.choices[0].message.content
        except Exception as e:
            analysis = f"AI分析失败：{str(e)}"

        return {
            "user_id": user_id,
            "username": user.username,
            "purchased_count": len(purchased),
            "pending_count": len(pending),
            "comment_count": comment_count,
            "analysis": analysis
        }