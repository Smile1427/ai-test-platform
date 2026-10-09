from zai import ZhipuAiClient
import os

API_KEY = os.getenv("ZHIPU_API_KEY", "c5033eaca6e049a9899f9f257ceb9116.7DL6kEMKh3zUJf85")

class AIService:
    def __init__(self, api_key: str = None):
        self.client = ZhipuAiClient(api_key=api_key or API_KEY)

    def generate_course_intro(self, topic: str) -> str:
        if not topic or not topic.strip():
            raise ValueError("主题不能为空")  # ★ 改成抛异常
        if len(topic) > 100:
            raise ValueError("主题不能超过100字")
        prompt = f"请为课程《{topic}》写一段100字左右的介绍，要求语言简洁、突出课程价值。"
        response = self.client.chat.completions.create(
            model="glm-4-flash",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    def recommend_courses(self, user_id: int, db=None) -> list:
        """★ 改造：基于用户的订单推荐相似课程"""
        if db is None:
            return []

        from models import Order, Course, User
        # ★ 校验用户是否存在
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("用户不存在")

        from models import Order, Course
        # 查询用户已购买的课程
        purchased = db.query(Order).filter(
            Order.user_id == user_id,
            Order.status == "paid"
        ).all()

        if not purchased:
            # 新用户推荐热门课程
            hot = db.query(Course).limit(3).all()
            return [
                {"id": c.id, "title": c.title, "reason": "热门课程推荐"}
                for c in hot
            ]

        # 根据用户已购买课程的类别推荐相似课程
        purchased_course_ids = [o.course_id for o in purchased]
        purchased_courses = db.query(Course).filter(Course.id.in_(purchased_course_ids)).all()
        categories = list(set([c.category for c in purchased_courses if c.category]))

        recommend = db.query(Course).filter(
            Course.category.in_(categories),
            ~Course.id.in_(purchased_course_ids)
        ).limit(3).all()

        return [
            {"id": c.id, "title": c.title, "reason": f"根据你学习的{c.category}方向推荐"}
            for c in recommend
        ]

    def chat(self, question: str, user_id: int = None, db=None) -> str:
        """★ 改造：支持查询用户数据"""
        if not question or not question.strip():
            raise ValueError("问题不能为空")  # ★ 改成抛异常

        sensitive_words = ["炸弹", "毒品", "武器", "敏感"]
        for word in sensitive_words:
            if word in question:
                raise ValueError("问题包含敏感内容，无法回答")

        # ★ 判断是否为“查询我自己的数据”类问题
        data_keywords = ["我买了", "我的课", "我学了", "我的订单", "我的评论", "我购买"]
        is_query = any(kw in question for kw in data_keywords)

        if is_query and user_id and db:
            # 查询用户数据
            from models import Order, Course, Comment
            orders = db.query(Order, Course.title).join(Course, Order.course_id == Course.id)\
                .filter(Order.user_id == user_id).all()
            comment_count = db.query(Comment).filter(Comment.user_id == user_id).count()

            if not orders and comment_count == 0:
                data_context = "该用户暂无订单和评论记录。"
            else:
                order_info = [f"{title}（{order.status}）" for order, title in orders]
                data_context = f"""该用户的学习数据：
- 订单：{', '.join(order_info) if order_info else '暂无'}
- 评论数：{comment_count} 条"""

            prompt = f"""你是一个学习助手。用户问：{question}

以下是该用户的真实数据：
{data_context}

请基于以上数据回答用户问题，语言自然亲切。"""
        else:
            prompt = question

        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"AI服务暂时不可用：{str(e)}"