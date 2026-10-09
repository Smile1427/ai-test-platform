"""性能测试 - 多场景压测"""
from locust import HttpUser, task, between


class EduPlatformUser(HttpUser):
    """模拟在线教育平台用户"""
    wait_time = between(1, 3)

    @task(3)
    def view_course_list(self):
        """查看课程列表（权重3）"""
        self.client.get("/api/course/list")

    @task(2)
    def view_course_detail(self):
        """查看课程详情（权重2）"""
        self.client.get("/api/course/1")

    @task(1)
    def view_orders(self):
        """查看订单（权重1）"""
        self.client.get("/api/order/list/1")