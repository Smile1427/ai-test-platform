from database import SessionLocal, Base, engine
from models import Course, User
from passlib.hash import bcrypt

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# 初始化课程
if db.query(Course).count() == 0:
    courses = [
        Course(title="Python入门", description="零基础学Python", price=99.0, stock=100, category="编程"),
        Course(title="数据分析实战", description="用Python做数据分析", price=199.0, stock=50, category="数据"),
        Course(title="机器学习基础", description="机器学习入门课程", price=299.0, stock=30, category="AI"),
        Course(title="Web前端开发", description="HTML/CSS/JS入门", price=129.0, stock=80, category="编程"),
        Course(title="SQL数据库", description="数据库基础与实战", price=89.0, stock=200, category="数据"),
    ]
    db.add_all(courses)
    db.commit()
    print("初始化课程数据成功")

# ★ 新增：初始化管理员账号
if not db.query(User).filter(User.username == "admin").first():
    admin = User(username="admin", password=bcrypt.hash("admin123"), role="admin")
    db.add(admin)
    db.commit()
    print("初始化管理员账号成功：admin / admin123")

db.close()